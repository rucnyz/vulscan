import argparse

from datasets import load_dataset
from transformers import AutoTokenizer


def process_token(example, input_key):
    # Example processing: replace placeholder token with new token
    example[input_key] = example[input_key].replace(
        args.placeholder_token, args.new_placeholder_token
    )
    return example


if __name__ == "__main__":
    # change original placeholder token to new token
    parser = argparse.ArgumentParser(
        description="Convert old input data to new format."
    )
    parser.add_argument(
        "--placeholder_token",
        type=str,
        required=True,
        help="Placeholder token to be replaced.",
    )
    parser.add_argument(
        "--new_placeholder_token",
        type=str,
        required=True,
        help="New placeholder token to replace the old one.",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Dataset to be converted.",
    )
    parser.add_argument("--input_key", type=str, default="input")
    parser.add_argument("--label_key", type=str, default="value")
    args = parser.parse_args()

    dataset = load_dataset(args.dataset)
    dataset = dataset.map(process_token, fn_kwargs={"input_key": args.input_key})
    dataset_shortname = args.dataset.split("/")[-1]
    dataset.push_to_hub(f"secmlr/{dataset_shortname}")
