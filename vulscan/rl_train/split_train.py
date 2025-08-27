# split the data into train and test (recipe/dapo/data/dapo_dataset.parquet)

import os

from datasets import load_dataset
from transformers import AutoTokenizer


def remove_long_sequence(data, max_length=8192):
    """
    Remove sequences longer than max_length from the dataset.
    """
    tokenized = tokenizer.apply_chat_template(data["prompt"], add_special_tokens=True)
    # Check if the length of the tokenized sequence exceeds max_length
    if len(tokenized) > max_length:
        return False
    return True


def modify_source(data):
    """
    Modify the source of the dataset.
    """
    # Modify the source field in the dataset
    data["data_source"] = "vulscan_" + data["data_source"]
    return data


def split_dataset(input_file, output_dir, test_size=0.1):
    # Load the dataset
    dataset = load_dataset("parquet", data_files=input_file)
    dataset = dataset.map(modify_source)
    # Split the dataset into train and test sets
    train_test_split = dataset["train"].train_test_split(test_size=test_size, seed=42)
    train_dataset = train_test_split["train"]
    test_dataset = train_test_split["test"]
    # Remove long sequences from both train and test sets
    train_dataset = train_dataset.filter(lambda x: remove_long_sequence(x), num_proc=4)
    test_dataset = test_dataset.filter(lambda x: remove_long_sequence(x), num_proc=4)
    # Save the split datasets
    os.makedirs(output_dir, exist_ok=True)
    train_dataset.to_parquet(os.path.join(output_dir, "vulscan_train.parquet"))
    test_dataset.to_parquet(os.path.join(output_dir, "vulscan_test.parquet"))


if __name__ == "__main__":
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
    input_file = "verl/recipe/vulscan_dapo/data/dapo_dataset.parquet"
    output_dir = "verl/recipe/vulscan_dapo/data/"
    split_dataset(input_file, output_dir)
