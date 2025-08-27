from datasets import load_dataset as hf_load_dataset
import pickle


sven = hf_load_dataset("bstee615/sven")
sven_train = sven["train"]
pairs = {}

for sample in sven_train:
    f0 = sample["func_src_before"].strip()
    f1 = sample["func_src_after"].strip()

    pairs[f0] = f1
    pairs[f1] = f0

sven_test = sven["val"]
for sample in sven_test:
    f0 = sample["func_src_before"].strip()
    f1 = sample["func_src_after"].strip()

    pairs[f0] = f1
    pairs[f1] = f0

with open("tmp/sven_pairs.pkl", "wb") as f:
    pickle.dump(pairs, f)