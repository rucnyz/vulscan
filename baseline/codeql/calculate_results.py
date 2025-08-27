import argparse
import pandas as pd
import os

import re

def extract_cwe_number(file_path: str) -> str:
    match = re.search(r"CWE(\d+)", os.path.basename(file_path))
    if match:
        return match.group(1)
    return ""

def parse_csv(file_path, is_juliet=True):
    cwe_details_path = "../../datasets/cwe-details.csv"
    cwe_db = pd.read_csv(cwe_details_path)
    cwe_id_to_name = {str(row['CWE-ID']): row['Name'] 
                      for _, row in cwe_db.iterrows()}

    df = pd.read_csv(file_path, header=None)
    df.columns = ["Issue Type", "Description", "Severity", "Details", "File Path",
                 "Start Line", "Start Column", "End Line", "End Column"]
    
    if is_juliet:
        df["Label"] = "TP"
    else:
        def extract_file_number(filename):
            try:
                base_name = os.path.splitext(os.path.basename(filename))[0]
                number_part = base_name.split('_')[0]
                return int(number_part)
            except:
                return 0
        
        df["File Number"] = df["File Path"].apply(extract_file_number)
        df["Label"] = df["File Number"].apply(lambda x: "TP" if x % 2 == 0 else "FP")

    def extract_cwe_number(file_path):
        try:
            filename = os.path.splitext(os.path.basename(file_path))[0]
            match = re.search(r'CWE(\d+)', filename)
            if match:
                return match.group(1)
        except Exception:
            return None
        return None
    

    def check_label(row):
        if row["Label"] != "TP":
            return row["Label"]
        
        cwe_num = extract_cwe_number(row["File Path"])

        if not cwe_num:
            return "FP" 
        
        cwe_name = cwe_id_to_name.get(cwe_num)
        if not cwe_name:
            return "FP"

        print(F"cwe_name.lower() = {cwe_name.lower()}, row['Issue Type'] = {row['Issue Type']}")
        if cwe_name.lower() == str(row["Issue Type"]).lower() or cwe_name.lower() in str(row["Issue Type"]).lower() or str(row["Issue Type"]).lower() in cwe_name.lower():
            return "TP"  # 匹配成功，确实是TP
        else:
            return "FP"  # 不匹配，改为FP

    df["Label"] = df.apply(check_label, axis=1)
    
    return df

def compute_metrics(df, total_ground_truth):
    TP = len(df[df["Label"] == "TP"])
    FP = len(df[df["Label"] == "FP"])
    
    Precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    Recall = TP / total_ground_truth if total_ground_truth > 0 else 0
    F1 = 2 * (Precision * Recall) / (Precision + Recall) if (Precision + Recall) > 0 else 0
    
    return {
        "TP": TP,
        "FP": FP,
        "Precision": Precision,
        "Recall": Recall,
        "F1": F1
    }

def count_juliet_total_cases(directory):
    # Count ground truth positive cases: files starting with "CWE" and ending with .c or .cpp
    return len([f for f in os.listdir(directory) if f.startswith("CWE") and f.endswith((".c", ".cpp"))])

def count_seccodeplt_total_cases(directory):
    # Count ground truth positive cases
    count = 0
    for f in os.listdir(directory):
        if f.endswith(".py"):
            try:
                number = int(f.split("_")[0])

                if number % 2 == 1:
                    count += 1
            except ValueError:
                continue
    return count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate CodeQL metrics for juliet or seccodeplt dataset")
    parser.add_argument('--dataset', type=str, required=True, choices=["juliet", "seccodeplt"],
                        help="Choose dataset: juliet or seccodeplt")
    args = parser.parse_args()
    
    if args.dataset == "juliet":
        # For juliet: ground truth from c directory and predictions from codeql_juliet.csv
        csv_path = "./codel_analyze_data/c/codeql_juliet.csv"
        directory = "./codel_analyze_data/c"
        df = parse_csv(csv_path, is_juliet=True)
        total_cases = count_juliet_total_cases(directory)
        metrics = compute_metrics(df, total_cases)
        result_str = "juliet Metrics: TP=%d, FP=%d, Recall=%.2f, Precision=%.2f, F1=%.2f, Total Cases=%d" % \
            (metrics["TP"], metrics["FP"], metrics["Recall"], metrics["Precision"], metrics["F1"], total_cases)
        print(result_str)
        with open("../../results/codeql_result/codeql_juliet_metric.csv", "w") as f:
            f.write(result_str + "\n")
    elif args.dataset == "seccodeplt":
        # For seccodeplt: ground truth from python directory and predictions from codeql_seccodeplt.csv
        csv_path = "./codel_analyze_data/python/codeql_seccodeplt.csv"
        directory = "./codel_analyze_data/python"
        df = parse_csv(csv_path, is_juliet=False)
        total_cases = count_seccodeplt_total_cases(directory)
        metrics = compute_metrics(df, total_cases)
        result_str = "seccodeplt Metrics: TP=%d, FP=%d, Recall=%.2f, Precision=%.2f, F1=%.2f, Total Cases=%d" % \
            (metrics["TP"], metrics["FP"], metrics["Recall"], metrics["Precision"], metrics["F1"], total_cases)
        print(result_str)
        with open("../../results/codeql_result/codeql_seccodeplt_metric.csv", "w") as f:
            f.write(result_str + "\n")