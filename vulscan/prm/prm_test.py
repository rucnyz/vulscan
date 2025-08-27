from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM
import torch


if __name__ == "__main__":
    good_token = "+"
    bad_token = "-"
    step_tag = "<extra_0>"

    tokenizer = AutoTokenizer.from_pretrained(
        "/scratch/yuzhou/projects/vulllm/vulscan/prm/checkpoint/Qwen2.5-7B-Instruct/prm_clean_dataset_filtered_QwQ-32B-Preview_train_len_8000_inputlen_5000/"
    )
    # vocab = tokenizer.get_vocab()
    # with open("vocab.json", "w") as f:
    #     json.dump(vocab, f, indent=4)
    candidate_tokens_good = tokenizer.encode(f"{good_token}")
    candidate_tokens_bad = tokenizer.encode(f"{bad_token}")
    print(candidate_tokens_good)
    print(candidate_tokens_bad)
    candidate_tokens = candidate_tokens_good + candidate_tokens_bad
    step_tag_id = tokenizer.encode(f"{step_tag}")[-1]  # 12902

    print(step_tag_id)
    model = AutoModelForCausalLM.from_pretrained(
        "/scratch/yuzhou/projects/vulllm/vulscan/prm/checkpoint/Qwen2.5-7B-Instruct/prm_clean_dataset_filtered_QwQ-32B-Preview_train_len_8000_inputlen_5000/"
    ).eval()

    question = """Janet\u2019s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?"""
    output1 = f"""Step 1: Janet's ducks lay 16 eggs per day. {step_tag}\nStep 2: She eats three for breakfast every morning, so she has 16 - 3 = 13 eggs left. {step_tag}\nStep 3: She bakes muffins for her friends every day with four eggs, so she has 13 - 4 = 9 eggs left. {step_tag}\nStep 4: She sells the remainder at the farmers' market daily for $2 per fresh duck egg, so she makes 9 * $2 = $18 every day at the farmers' market. The answer is: 18 <extra_0>"""  # 18 is right
    output2 = f"""Step 1: Janet's ducks lay 16 eggs per day. {step_tag}\nStep 2: She eats three for breakfast every morning, so she has 16 - 3 = 13 eggs left. {step_tag}\nStep 3: She bakes muffins for her friends every day with four eggs, so she has 13 - 4 = 9 eggs left. {step_tag}\nStep 4: She sells the remainder at the farmers' market daily for $2 per fresh duck egg, so she makes 9 * $2 = $17 every day at the farmers' market. The answer is: 17 {step_tag}"""  # 17 is wrong

    for output in [output1, output2]:
        input_for_prm = f"{question} {output}"
        # input_for_prm = input
        input_id = torch.tensor([tokenizer.encode(input_for_prm)])

        print(input_id)
        print(tokenizer.decode(tokenizer.encode(input_for_prm)))
        print(tokenizer.encode(input_for_prm))

        with torch.no_grad():
            logits = model(input_id).logits[:, :, candidate_tokens]
            scores = logits.softmax(dim=-1)[:, :, 1]
            step_scores = scores[input_id == step_tag_id]
            print(step_scores)

    # tensor([0.9955, 0.9958, 0.9983, 0.9957])
    # tensor([0.9955, 0.9958, 0.9983, 0.0240])
