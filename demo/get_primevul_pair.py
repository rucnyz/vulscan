from datasets import load_dataset as hf_load_dataset
import pickle


primevul_paired_test = hf_load_dataset("colin/PrimeVul", "paired", split="test")
print(primevul_paired_test)

pairs = {}
for idx in range(0, len(primevul_paired_test), 2):
    s0 = primevul_paired_test[idx]
    s1 = primevul_paired_test[idx + 1]
    f0 = s0["func"].strip()
    f1 = s1["func"].strip()

    pairs[f0] = f1
    pairs[f1] = f0

with open("tmp/primevul_pairs.pkl", "wb") as f:
    pickle.dump(pairs, f)