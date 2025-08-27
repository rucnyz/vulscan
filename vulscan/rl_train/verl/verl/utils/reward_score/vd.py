# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from vulscan.test.test_utils.generation_utils import (
    check_single_cwe,
)


def extract_answer_strict(output):
    try:
        output = output.split("## Final Answer")[-1]
        output = output.lower()
        pred_score = output.split("#judge: ")[1].split("#type: ")[0].strip().lower()
        pred_vul_type = output.split("#type: ")[1].split("\n")[0].strip().upper()
        assert "yes" == pred_score or "no" == pred_score
        if not check_single_cwe(pred_vul_type):
            assert pred_vul_type == "N/A"
    except Exception as _:
        pred_score = "Invalid format"
        pred_vul_type = "Invalid format"
    return pred_score, pred_vul_type


def compute_score(
    solution_str,
    ground_truth,
    invalid_format_score=-1,
    format_score=0.1,
    correct_score=0.4,
    all_correct_score=1.0,
):
    """The scoring function for vulscan.

    Args:
        all_correct_score: the score for all correct
        correct_score: the score for correct score but wrong vul type
        format_score: the score for wrong score but correct vul type
        invalid_format_score: the score for invalid format
        solution_str: the solution text
        ground_truth: the ground truth
    """
    pred_score, pred_vul = extract_answer_strict(solution_str)
    true_score, true_vul_type = extract_answer_strict(ground_truth)
    ret = None
    # if the format is wrong, return 0
    if pred_score == "Invalid format":
        ret = invalid_format_score
    # if the format is correct, but the score is wrong, return format_score
    elif pred_score != true_score:
        ret = format_score
    # if the score is correct, but the vul type is wrong, return 0.5
    elif pred_score == true_score and pred_vul != true_vul_type:
        ret = correct_score
    # if the score and the vul type are correct, return 1
    elif pred_score == true_score and pred_vul == true_vul_type:
        ret = all_correct_score
    else:
        raise ValueError(f"Unknown case: {pred_score=}, {true_score=}, {pred_vul=}, {true_vul_type=}")
    return {
        "score": ret,
        "acc": ret,
        "pred_score": pred_score,
        "true_score": true_score,
        "pred_vul_type": pred_vul,
        "true_vul_type": true_vul_type,
    }