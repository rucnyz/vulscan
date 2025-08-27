import difflib
import os
import re
import orjson
from dotenv import load_dotenv

from openai import OpenAI

from vulscan.utils.project_info import PROJECT_PATH

system_prompt = """
You are an organizing assistant, and your task is to help filter out useful content from the given reasoning process. Follow these instructions:

1. Choose to discard the reasoning process or keep it. If the reasoning process mentions more than three potential vulnerabilities, discard it, otherwise keep it.
2. Filter and keep the functionality analysis. Keep the analysis and descriptions of the entire code (without vulnerability/CWE analysis) in the reasoning process, including explanations on the logic of the code.
3. Filter and keep the vulnerability analysis. Filter out the vulnerability analysis corresponding to the given vulnerability (CWE type) and the provided code diff from the reasoning process:
Only keep reasoning data related to the given vulnerability (CWE type) and the specific lines of code diff.
Remove reasoning data that does not directly relate to the specified vulnerability or diff.

For the functionality analysis and vulnerability analysis, keep the original words, sentences and tones from the reasoning process, repeat the the words in the input reasoning as much as possible, as detailed as possible, as long as possible.
Describe the functionality analysis and vulnerability analysis just like you are giving the reasoning output yourself (pretend you are a code analyzer and the object is the code).

- Input:
### The reasoning process.
### CWE type: The specific vulnerability type (e.g., CWE-174.).
### Code with diff: The code snippet that shows the lines modified.

- Output:
### Keep it or Not: Indicate whether to keep the reasoning process. [Yes/No]
### Reason for keeping it or not: [Your reason]
### Functionality analysis: [Your filtered result] (pretend you are a code analyzer and the object is the code)
### Vulnerability analysis: [Your filtered result] (pretend you are a code analyzer and the object is the code)

- Example output:

### Keep it or Not: Yes

### Reason for keeping it or not: This reasoning process only contains the given CWE-174 ......

### Functionality analysis: It's part of a media processing library, specifically for HEVC video decoding. The function is called `onQueueFilled`, which suggests ...

### Vulnerability analysis: Potential Issues\n\n1. **Timestamp Management:**\n\n   - The code manages timestamps for synchronization. If there's an error in encoding or decoding timestamps, it could lead to playback issues ...

"""


def extract_sections(llm_output):
    keep_it_or_not = ""
    reason_for_keep = ""
    functionality_analysis = ""
    vulnerability_analysis = ""

    keep_it_or_not_match = re.search(
        r"### Keep it or Not:\s*(.*?)(?=\n### |$)", llm_output, re.DOTALL
    )
    reason_for_keep_match = re.search(
        r"### Reason for keeping it or not:\s*(.*?)(?=\n### |$)", llm_output, re.DOTALL
    )
    functionality_analysis_match = re.search(
        r"### Functionality analysis:\s*(.*?)(?=\n### |$)", llm_output, re.DOTALL
    )
    vulnerability_analysis_match = re.search(
        r"### Vulnerability analysis:\s*(.*?)(?=\n### |$)", llm_output, re.DOTALL
    )

    if keep_it_or_not_match:
        keep_it_or_not = keep_it_or_not_match.group(1).strip()
    if reason_for_keep_match:
        reason_for_keep = reason_for_keep_match.group(1).strip()
    if functionality_analysis_match:
        functionality_analysis = functionality_analysis_match.group(1).strip()
    if vulnerability_analysis_match:
        vulnerability_analysis = vulnerability_analysis_match.group(1).strip()

    return {
        "Keep it or Not": keep_it_or_not,
        "Reason for keeping it or not": reason_for_keep,
        "Functionality analysis": functionality_analysis,
        "Vulnerability analysis": vulnerability_analysis,
    }


if __name__ == "__main__":
    # TODO: This code is like earlier version of generate.py it is not extensible

    load_dotenv(os.path.join(PROJECT_PATH, ".env"))
    # datasets/reasoning_data/noisy_dataset/QwQ-32B-Preview/QwQ-32B-Preview_train.json
    INPUT_DIR = os.path.join(PROJECT_PATH, "datasets/reasoning_data/noisy_dataset/")
    model_name = "Qwen/QwQ-32B-Preview"
    short_model_name = model_name.split("/")[-1]

    client = OpenAI()

    input_path = os.path.join(INPUT_DIR, f"{short_model_name}_small_train.json")
    output_path = os.path.join(
        INPUT_DIR, "extracted", f"{short_model_name}_small_train.json"
    )
    # filter dataset==primevul_pair, "correct": true, "model_reasoning" is not None, "model_answer": "yes"
    with open(input_path, "rb") as f:
        reasoning_data = orjson.loads(f.read())[1:]
    filtered_data = [
        item
        for item in reasoning_data
        if item["dataset"] == "primevul_pair" and item["model_reasoning"] is not None
    ]
    # model_answer: if the code contains a vulnerability according to the model
    # correct: model_answer == output(label)

    # TODO: i don't understand why having argument vul and fix

    for i in range(len(filtered_data) // 2):  # len(filtered_data)//2
        vul = filtered_data[2 * i]
        fix = filtered_data[2 * i + 1]

        # diff = "\n".join(
        #     difflib.ndiff(vul["code"].splitlines(), fix["code"].splitlines())
        # )

        diff = "\n".join(
            difflib.unified_diff(vul["code"].splitlines(), fix["code"].splitlines())
        )

        print(diff)

        llm_input = f"""
        ### The reasoning process: {vul["model_reasoning"]}
        ### CWE type: {vul["cwe"]}
        ### Code with diff: {diff}
        """

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": llm_input,
                    },
                ],
                model="o3-mini",
            )

            llm_output = chat_completion.choices[0].message.content

            print(chat_completion.choices[0].message.content)

            extract_result = extract_sections(llm_output)
            print(extract_result)
        except Exception as e:
            extract_result = extract_result = {"error": str(e)}

        file_path = "new_diff_result.json"

        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                try:
                    data = orjson.loads(f.read())
                    if not isinstance(data, list):
                        data = []
                except orjson.JSONDecodeError:
                    data = []
        else:
            data = []

        data.append(extract_result)

        with open(file_path, "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
