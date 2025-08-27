import json
import pickle
import re
from pathlib import Path
from typing import Literal
import argparse

from pydantic import BaseModel, Field

from vulscan.test.test_utils.generation_utils import check_pred_cwe_correctness
from vulscan.utils.project_info import parse_test_json_filename


class ResultSample(BaseModel):
    input: str
    code: str
    pair_code: str | None = None
    is_vuln: bool
    vuln_type: Literal["none"] | str

    output: str
    pred_is_vuln: bool | None  # None means invalid
    pred_vuln_type: (
        Literal["none"] | str | None
    )  # str means CWE-xxx, None means invalid
    unparsed_pred_vuln_type: str
    idx: str
    judge: Literal["tp", "tn", "fp", "fn", "invalid"]


class Task(BaseModel):
    dataset: str
    language: str
    prompt_type: Literal["cot", "own_cot", "none"]
    add_policy: bool


class Metrics(BaseModel):
    total: int = 0
    tp: int = 0
    tn: int = 0
    fp: int = 0
    fn: int = 0
    invalid: int = 0


class ResultData(BaseModel):
    model: str
    task: Task
    metrics: Metrics = Field(default_factory=Metrics)
    results: list[ResultSample] = Field(default_factory=list)


# class InputSample(BaseModel):
#     id: str
#     idx: str
#     dataset: str
#     cwe: list[str]
#     code: str
#     language: str
#     is_vuln: bool
#     pair_id: str | None = None

# class InputData(BaseModel):
#     inputs: list[InputSample] = Field(default_factory=list)


def parse_result_filename(filename: str):
    # pattern = (
    #     r"(?:_(?P<cot>cot))?"  # COT presence
    #     r"(?:_(?P<language>[a-zA-Z]+))?"  # Language (optional)
    #     r"(?:_(?P<own_cot>own_cot))?"  # Own COT presence
    #     r"(?:_(?P<policy>policy))?"  # Policy presence
    #     r"_(?P<model_shortname>[\w.-]+)\.json"  # Model shortname before .json
    # )
    data = parse_test_json_filename(filename)
    if data:
        # Extract language (if present)
        language = data["language"] if data["language"] else "none"

        return ResultData(
            model=data["model_shortname"],
            task=Task(
                dataset=data["dataset"],
                language=language,
                prompt_type=data["cot"],
                add_policy=data["policy"] == "policy",
            ),
        )


def clean_pred_vuln_type(pred_vuln_type: str):
    if "N/A" in pred_vuln_type:
        return "none"

    # try to extract the last number in the string
    nums = re.findall(r"\d+", pred_vuln_type)
    if nums:
        return f"CWE-{nums[-1]}"

    return None


def update_metrics(
    data: ResultData,
    sample: ResultSample,
):
    data.metrics.total += 1
    if sample.judge == "tp":
        data.metrics.tp += 1
    elif sample.judge == "tn":
        data.metrics.tn += 1
    elif sample.judge == "fp":
        data.metrics.fp += 1
    elif sample.judge == "fn":
        data.metrics.fn += 1
    elif sample.judge == "invalid":
        data.metrics.invalid += 1


def judge(
    is_vuln: bool, vuln_type: str, pred_is_vuln: bool | None, pred_vuln_type: str | None
):
    if pred_is_vuln is None or pred_vuln_type is None:
        return "invalid"
    if is_vuln and pred_is_vuln and vuln_type == pred_vuln_type:
        return "tp"
    if not is_vuln and not pred_is_vuln:
        return "tn"
    if is_vuln and not pred_is_vuln:
        return "fn"
    if (not is_vuln and pred_is_vuln) or (
        is_vuln and pred_is_vuln and vuln_type != pred_vuln_type
    ):
        return "fp"

    raise ValueError("Invalid prediction")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert old input data to new format."
    )
    parser.add_argument(
        "--result_dir",
        type=Path,
        required=True,
        help="Directory containing result JSON files.",
    )
    parser.add_argument(
        "--out_dir",
        type=Path,
        required=True,
        help="Output directory for converted results.",
    )
    parser.add_argument(
        "--pairs",
        type=Path,
        nargs="+",
        required=True,
        help="List of pairs files to merge.",
    )
    parser.add_argument(
        "--skip_existing_json",
        action="store_true",
    )
    return parser.parse_args()


def load_pairs(pairs_files):
    pairs = {}
    for file in pairs_files:
        with open(file, "rb") as f:
            pairs.update(pickle.load(f))
    return pairs


def main(raw_args=None):
    args = parse_args()
    results_dir = args.result_dir
    out_dir = args.out_dir
    pairs_files = args.pairs

    pairs = load_pairs(pairs_files)

    out_dir.mkdir(parents=True, exist_ok=True)

    for res_json in results_dir.glob("*.json"):
        out_file = out_dir / res_json.name
        if args.skip_existing_json and out_file.exists():
            print(f"[!] Skipping {res_json}, already processed.")
            continue

        print(f"[*] Processing {res_json}")
        with open(res_json) as f:
            data = json.load(f)

        result_data = parse_result_filename(res_json.name)

        for d in data[1:]:
            code = d["input"].split("```")[1].split("```")[0].strip()
            is_vuln = d["is_vulnerable"] == "yes"
            vuln_type = d["vulnerability_type"] if is_vuln else "none"
            pred_is_vuln = None
            if d["predicted_is_vulnerable"] == "yes":
                pred_is_vuln = True
            elif d["predicted_is_vulnerable"] == "no":
                pred_is_vuln = False
            # pred_vuln_type = clean_pred_vuln_type(d["predicted_vulnerability_type"])
            if check_pred_cwe_correctness(
                d["predicted_is_vulnerable"],
                d["predicted_vulnerability_type"],
                d["is_vulnerable"],
                d["vulnerability_type"],
            ):
                pred_vuln_type = vuln_type
            else:
                pred_vuln_type = None

            sample = ResultSample(
                input=d["input"],
                code=code,
                pair_code=pairs.get(code),
                is_vuln=is_vuln,
                vuln_type=vuln_type,
                output=d["output"],
                pred_is_vuln=pred_is_vuln,
                pred_vuln_type=pred_vuln_type,
                unparsed_pred_vuln_type=d["predicted_vulnerability_type"],
                judge=d["flag"] if not d["is_wrong"] else "invalid",
                idx=str(d["idx"]),
            )

            result_data.results.append(sample)
            update_metrics(result_data, sample)

        with open(out_file, "w") as f:
            f.write(result_data.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
