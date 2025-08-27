import json
import os

from llamafirewall import (
    LlamaFirewall,
    AssistantMessage,
    Role,
    ScannerType,
    ScanDecision,
)

from vulscan.test.test_utils.utils import calculate_score
from vulscan.utils.project_info import PROJECT_PATH

# Initialize LlamaFirewall with AlignmentCheckScanner
firewall = LlamaFirewall(
    {
        # Role.ASSISTANT: [ScannerType.AGENT_ALIGNMENT],
        Role.ASSISTANT: [ScannerType.CODE_SHIELD]
    }
)
tp = 0
fp = 0
fn = 0
tn = 0
count = 0

dataset_dir = "test_secllmholmes/c"
for file in os.listdir(
    os.path.join(PROJECT_PATH, f"datasets/test/{dataset_dir}")
):
    if file.endswith(".json"):
        with open(
            os.path.join(PROJECT_PATH, f"datasets/test/{dataset_dir}", file),
            "r",
        ) as f:
            data = json.load(f)
            for item in data:
                count += 1
                code = item["code"]
                conversation_trace = [AssistantMessage(content=code)]
                result = firewall.scan_replay(conversation_trace)
                if item["target"] == 1 and result.decision == ScanDecision.BLOCK:
                    tp += 1
                elif item["target"] == 1 and result.decision == ScanDecision.ALLOW:
                    fn += 1
                elif item["target"] == 0 and result.decision == ScanDecision.BLOCK:
                    fp += 1
                elif item["target"] == 0 and result.decision == ScanDecision.ALLOW:
                    tn += 1
                else:
                    raise ValueError("Invalid target or decision")
result = calculate_score(tp, fp, fn, tn, count, False, 0)
print(f"results for {dataset_dir}")
print("total: {}".format(count))
print("wrong: {}".format(result["wrong_num"]))
print("fpr: {:.3f}".format(result["false_positive_rate"]))
print("fnr: {:.3f}".format(result["false_negative_rate"]))
print("Vul F1: {:.3f}".format(result["positive F1"]))
print("Benign F1: {:.3f}".format(result["negative F1"]))
print("Overall F1: {:.3f}".format(result["overall F1"]))
# Scan the entire conversation trace


# Print the result
print(result)
