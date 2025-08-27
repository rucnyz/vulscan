import argparse
import os

import orjson
from aiolimiter import AsyncLimiter
from datasets import load_dataset, Dataset
from dotenv import load_dotenv
from model_zoo import LiteLLMModel
from tqdm import trange

from vulscan.test.test_utils.generation_utils import (
    check_pred_cwe_correctness,
    extract_answer,
)
from vulscan.utils.project_info import PROJECT_PATH
from vulscan.utils.sys_prompts import (
    deepseek_sys_prompt,
    qwq_sys_prompt_generation,
    sft_sys_prompt,
)


def create_prm_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--dataset_type", type=str, default="noisy_dataset")
    parser.add_argument("--training_set", type=str, default="train")
    parser.add_argument("--max_tokens", type=int, default=16384)
    parser.add_argument("--batch_size", type=int, default=10)
    parser.add_argument("--tp", type=int, default=2)
    parser.add_argument("--requests_per_minute", type=int, default=60)
    parser.add_argument("--together_deepseek", action="store_true", default=False)
    parser.add_argument("--server_url", type=str, default=None)
    parser.add_argument("--output_dir", type=str, default="datasets/prm_data")
    return parser


def split_into_steps(reasoning):
    """Split reasoning into steps separated by double newlines"""
    return [step.strip() for step in reasoning.split("\n\n") if step.strip()]


def evaluate_step(model, example, step, max_tokens=1024, system_prompt=None):
    """Evaluate a step by generating 10 completions and checking correctness"""
    # Create a new prompt that includes the current step
    step_example = example.copy()
    step_example["input"] = example["input"] + "\n\n" + step

    # Run the model 10 times for this step
    outputs, answers, _, _ = model.run(
        eval_examples=[step_example],
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        n=10,
        temperature=0.7,
        top_p=0.9,
    )

    # Extract completion and check correctness
    correct_count = 0
    true_score = example["answer"].split("#judge: ")[1].split()[0].strip()
    true_vul_type = example["answer"].split("#type: ")[1].split()[0].strip()

    for output in outputs[0]:
        from vulscan.test.test_utils.generation_utils import extract_answer

        pred_score, pred_vul_type = extract_answer(output)

        if check_pred_cwe_correctness(
            pred_score, pred_vul_type, true_score, true_vul_type
        ):
            correct_count += 1

    return correct_count >= 5, outputs[0]


def generate_prm_data(args):
    # Setup directories
    output_dir = args.output_dir

    short_model_name = args.model_name.split("/")[-1]
    output_path = os.path.join(
        PROJECT_PATH,
        output_dir,
        f"{short_model_name}_{args.dataset_type}_{args.training_set}.json",
    )
    prm_output_path = os.path.join(
        PROJECT_PATH,
        output_dir,
        f"{short_model_name}_{args.dataset_type}_{args.training_set}_prm.json",
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load reasoning data
    dataset = load_dataset(
        f"secmlr/{args.dataset_type}_filtered_{short_model_name}_{args.training_set}_len_8000_inputlen_5000"
    )["train"]

    # Setup model
    system_prompt = None
    if "deepseek-reasoner" in args.model_name:
        system_prompt = deepseek_sys_prompt
    elif "QwQ" in args.model_name:
        system_prompt = qwq_sys_prompt_generation

    limiter = AsyncLimiter(args.requests_per_minute, 60)
    if (
        "gpt" in args.model_name
        or "o3" in args.model_name
        or "claude" in args.model_name
        or "deepseek-reasoner" in args.model_name
    ):
        model = LiteLLMModel(
            model=args.model_name,
            limiter=limiter,
            together_deepseek=args.together_deepseek,
        )
    elif args.server_url:
        model = LiteLLMModel(
            model=args.model_name, server_url=args.server_url, limiter=limiter
        )
    else:
        from model_zoo import VllmModel

        model = VllmModel(model=args.model_name, num_gpus=args.tp)  # Assuming 2 GPUs

    # Process data in batches
    if os.path.exists(output_path) and os.path.exists(prm_output_path):
        with open(output_path, "rb") as f:
            new_dataset = orjson.loads(f.read())
        with open(prm_output_path, "rb") as f:
            prm_data = orjson.loads(f.read())

        start_idx = new_dataset["0"]
    else:
        prm_data = []
        new_dataset = {}
        start_idx = 0
        for idx in trange(len(dataset)):
            item = dataset[idx]
            new_item = {"idx": item["idx"], "input": item["conversations"][0]["value"]}
            output = item["conversations"][1]["value"]
            # reasoning in <begin_of_solution> ... <end_of_solution>
            reasoning = (
                output.split("<|begin_of_thought|>")[1]
                .split("<|end_of_thought|>")[0]
                .strip()
            )
            answer = (
                output.split("<|begin_of_solution|>")[1]
                .split("<|end_of_solution|>")[0]
                .strip()
            )
            new_item["output"] = answer
            reasoning_data = reasoning.split("\n\n")
            current_step = ""
            for each_step in reasoning_data:
                each_step_data = new_item.copy()
                current_step += each_step + "\n\n"
                each_step_data["assistant"] = current_step
                prm_data.append(each_step_data)
            new_reasoning_data = [item + " <extra_0>" for item in reasoning_data]
            new_item["input"] = [
                {"role": "system", "content": sft_sys_prompt},
                {"role": "user", "content": new_item["input"]},
                {
                    "role": "assistant",
                    "content": output.replace(
                        reasoning, "\n\n".join(new_reasoning_data)
                    ),
                },
            ]
            new_item["input"] = model.model.get_tokenizer().apply_chat_template(
                new_item["input"], tokenize=False
            )
            new_item["value"] = []
            new_dataset[str(item["idx"])] = new_item
        # Save the initial dataset
        new_dataset["0"] = 0
        with open(output_path, "wb") as f:
            f.write(orjson.dumps(new_dataset, option=orjson.OPT_INDENT_2, default=str))
        with open(prm_output_path, "wb") as f:
            f.write(orjson.dumps(prm_data, option=orjson.OPT_INDENT_2, default=str))

    for current_data_idx in trange(start_idx, len(prm_data), args.batch_size):
        current_batch = prm_data[current_data_idx : current_data_idx + args.batch_size]
        # Generate initial responses for the batch
        outputs, answers, latencies, completion_tokens = model.run(
            eval_examples=current_batch,
            system_prompt=system_prompt,
            max_tokens=args.max_tokens,
            n=8,
            temperature=0.6,
            top_p=0.9,
        )
        for i, (output, answer, latency, completion_token) in enumerate(
            zip(outputs, answers, latencies, completion_tokens["output_token"])
        ):
            try:
                true_score, true_vul_type = extract_answer(answer)
            except Exception as e:
                print(f"Error parsing answer: {answer}")
                with open("error.json", "wb") as f:
                    f.write(orjson.dumps(current_batch[i], option=orjson.OPT_INDENT_2, default=str))
                raise e
            correctness = 0
            for each_answer in output:
                pred_score, pred_vul = extract_answer(each_answer)

                if check_pred_cwe_correctness(
                    pred_score, pred_vul, true_score, true_vul_type
                ):
                    correctness += 1
            if correctness >= 2:
                new_dataset[str(current_batch[i]["idx"])]["value"].append("+")
            else:
                new_dataset[str(current_batch[i]["idx"])]["value"].append("-")

        # Save after each example to avoid data loss
        new_dataset["0"] = current_data_idx + args.batch_size
        with open(output_path, "wb") as f:
            f.write(orjson.dumps(new_dataset, option=orjson.OPT_INDENT_2, default=str))

        print(f"Processed example {current_data_idx + args.batch_size}/{len(dataset)}")

    data = Dataset.from_dict(new_dataset)
    data.push_to_hub(
        f"secmlr/prm_{args.dataset_type}_filtered_{short_model_name}_{args.training_set}_len_8000_inputlen_5000"
    )


if __name__ == "__main__":
    load_dotenv()
    parser = create_prm_parser()
    args = parser.parse_args()

    generate_prm_data(args)
