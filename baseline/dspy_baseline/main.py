import argparse
import os
import sys

import dspy
from dotenv import load_dotenv
from dspy import MIPROv2, Evaluate
from transformers import (
    set_seed,
)

from vulscan.test.test_utils.generation_utils import (
    check_each_data,
)
from vulscan.test.test_utils.utils import load_reasoning_data
from vulscan.utils.cwes import hard_ood_cwes, clean_ood_cwes, remove_idx
from vulscan.utils.project_info import PROJECT_PATH
from vulscan.utils.sys_prompts import (
    our_cot,
    policy,
    qwen_sys_prompt,
    sft_sys_prompt,
)


def vulscan_metric(gold, pred, trace=None):
    ret = check_each_data(pred.output, gold.output)
    return ret


def set_args():
    args = argparse.ArgumentParser()
    args.add_argument("--seed", type=int, default=42, help="seed")
    args.add_argument("--test_dataset_path", type=str, required=True)
    args.add_argument("--train_dataset_path", type=str, required=True)
    args.add_argument("--output_dir", type=str, required=True)
    args.add_argument("--save", action="store_true")
    args.add_argument(
        "--requests_per_minute", type=int, default=60, help="requests per minute"
    )
    args.add_argument(
        "--test_samples_num", type=int, default=sys.maxsize, help="test samples num"
    )
    args.add_argument(
        "--max_tokens", type=int, default=16384, help="max tokens for each prompt"
    )
    args.add_argument("--n", type=int, default=1, help="n samples")
    args.add_argument("--model", type=str, default="gpt-4o-2024-11-20")
    args.add_argument("--model_type", type=str, default=None)
    args.add_argument("--revision", type=str, default=None)
    args.add_argument("--use_policy", action="store_true", default=False)
    args.add_argument("--use_free_policy", action="store_true", default=False)
    args.add_argument("--use_cot", action="store_true", default=False)
    args.add_argument("--use_own_cot", action="store_true", default=False)
    args.add_argument("--random_cwe", action="store_true", default=False)
    args.add_argument("--server_url", type=str, default=None)
    args.add_argument("--tp", type=int, default=1, help="tensor parallel size")
    args.add_argument("--batch_size", type=int, default=4, help="batch size")
    args.add_argument("--vllm", action="store_true", default=False)
    args.add_argument("--temperature", type=float, default=0.0)
    args.add_argument("--together_deepseek", action="store_true", default=False)
    args.add_argument("--language", type=str, required=True, nargs="+")
    args.add_argument("--ids", type=str, nargs="+")
    args.add_argument("--ood", action="store_true", default=False)
    args.add_argument("--addition_constraint", action="store_true", default=False)
    args = args.parse_args()
    if args.use_cot and args.use_own_cot:
        raise ValueError("Cannot use both cot and own_cot")
    return args


class Vulscan_default(dspy.Signature):
    f"""{qwen_sys_prompt}"""
    input: str = dspy.InputField()
    output: str = dspy.OutputField()


class Vulscan_sft(dspy.Signature):
    f"""{sft_sys_prompt}"""
    input: str = dspy.InputField()
    output: str = dspy.OutputField()


class CoT(dspy.Module):
    def __init__(self, signature=Vulscan_default):
        super().__init__()
        self.prog = dspy.ChainOfThought(signature)

    def forward(self, input):
        return self.prog(input=input)


def select_examples(examples, num):
    """
    Select num examples in each cwe
    """
    selected_examples = []
    cwe_dict = dict()
    for example in examples:
        if example["cwe"][0] not in cwe_dict:
            cwe_dict[example["cwe"][0]] = []
        cwe_dict[example["cwe"][0]].append(example)
    for cwe, example_list in cwe_dict.items():
        selected_examples.extend(example_list[:num])
    return selected_examples


if __name__ == "__main__":
    load_dotenv()
    args = set_args()
    os.makedirs(os.path.join(PROJECT_PATH, args.output_dir), exist_ok=True)
    # set current working directory
    os.chdir(PROJECT_PATH)
    # set seed by huggingface
    set_seed(args.seed)

    print("=" * 80)
    for k, v in vars(args).items():
        print(k, ": ", v)
    print("=" * 80)

    base_model = args.model
    if "secmlr" in base_model:
        signature = Vulscan_sft
    else:
        signature = Vulscan_default
    lm = dspy.LM(
        f"openai/{base_model}",
        api_base="http://localhost:8000/v1",  # ensure this points to your port
        api_key="empty",
        model_type="chat",
        cache=False,
    )
    # lm = dspy.LM("openai/gpt-4o")
    dspy.configure(lm=lm)
    for language in args.language:
        if not os.path.exists(os.path.join(args.test_dataset_path, language)):
            continue
        name = args.output_dir.split("/")[-1]

        # data
        output_path = "/dev/null"
        ood_dict = dict()
        if args.ood:
            if "clean" in args.test_dataset_path.as_posix():
                ood_dict[language] = clean_ood_cwes[language]
            elif "primevul_pair" in args.test_dataset_path.as_posix():
                ood_dict[language] = hard_ood_cwes[language]
            else:
                raise ValueError("dataset must be clean_dataset or noisy_dataset")
        else:
            # this is needed for load_reasoning_data
            ood_dict[language] = []
        eval_examples, _, _ = load_reasoning_data(
            args.test_dataset_path,

            output_path,
            ood_dict,
            args.model,
            policy if args.use_policy else "",
            our_cot,
            args.use_own_cot,
            skip_human=False,
            random_cwe=args.random_cwe,
            reduced=False,
            addition_constraint=args.addition_constraint,
        )

        eval_examples = eval_examples[: args.test_samples_num]
        eval_examples = [
            dspy.Example(**item).with_inputs("input")
            for item in eval_examples
            if str(item["idx"]) not in remove_idx
        ]
        # train examples
        train_examples, _, _ = load_reasoning_data(
            args.train_dataset_path,
            output_path,
            ood_dict,
            args.model,
            policy if args.use_policy else "",
            our_cot,
            args.use_own_cot,
            skip_human=False,
            random_cwe=args.random_cwe,
            reduced=False,
            addition_constraint=args.addition_constraint,
        )
        # select 10 examples for each cwe
        train_examples = select_examples(train_examples, 10)
        train_examples = [
            dspy.Example(**item).with_inputs("input") for item in train_examples
        ]
        # start to use dspy
        teleprompter = MIPROv2(
            metric=vulscan_metric,
            auto="light",  # Can choose between light, medium, and heavy optimization runs
        )
        program = CoT(signature=signature)

        evaluate = Evaluate(
            devset=eval_examples[:],
            metric=vulscan_metric,
            num_threads=8,
            display_progress=True,
            display_table=False,
        )
        evaluate(program, devset=eval_examples[:500])
        zeroshot_optimized_program = teleprompter.compile(
            program.deepcopy(),
            trainset=eval_examples[500:],
            max_bootstrapped_demos=2,  # ZERO FEW-SHOT EXAMPLES
            max_labeled_demos=2,  # ZERO FEW-SHOT EXAMPLES
            requires_permission_to_run=False,
        )
        # Save optimize program for future use
        zeroshot_optimized_program.save("mipro_zeroshot_optimized.json")

        # Evaluate optimized program
        print("Evaluate optimized program...")
        evaluate(zeroshot_optimized_program, devset=eval_examples[:500])
