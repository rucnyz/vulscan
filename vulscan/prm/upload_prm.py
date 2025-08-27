import json

from datasets import Dataset


def filter_data(example, idx):
    inputs = example["input"].split("<extra_0>")
    length = len(inputs) - 1
    if len(example["value"]) != length:
        print(f"error for {idx} with input {example['input']}")
        return False
    return True


if __name__ == "__main__":
    dataset_type = "clean_dataset"
    training_set = "train"
    short_model_name = "QwQ-32B-Preview"
    data_path = f"/scratch/yuzhou/projects/vulllm/datasets/prm_data/{short_model_name}_{dataset_type}_{training_set}.json"
    with open(data_path, "r") as f:
        dataset = json.load(f)
    # remove "0" key
    dataset.pop("0", None)
    # convert to list
    dataset = list(dataset.values())
    data = Dataset.from_list(dataset)
    data = data.filter(filter_data, with_indices=True)
    data.push_to_hub(
        f"secmlr/prm_{dataset_type}_filtered_{short_model_name}_{training_set}_len_8000_inputlen_5000"
    )
