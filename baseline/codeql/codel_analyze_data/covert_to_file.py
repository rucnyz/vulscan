import os
import json

input_dir = './datasets/test/test_clean/python'
output_dir = './baseline/codeql/codel_analyze_data/python'

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith('.json'):
        input_path = os.path.join(input_dir, filename)
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            continue

        for item in data_list:
            try:
                code = item.get('code')
                idx = item.get('idx')
                cwe_id = item.get('CWE_ID', [''])[0]  # Get first CWE_ID or empty string
                
                if code is None or idx is None:
                    print(f"Missing 'code' or 'idx' in item from {filename}")
                    continue
                
                # Process CWE_ID to remove hyphen (e.g., "CWE-1333" -> "CWE1333")
                clean_cwe = cwe_id.replace('-', '') if cwe_id else 'UNKNOWN'
                
                output_path = os.path.join(output_dir, f"{idx}_{clean_cwe}.py")
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(code)
            except Exception as e:
                print(f"Error processing item in {filename}: {e}")

print("✅ Finished extracting code to .py files.")