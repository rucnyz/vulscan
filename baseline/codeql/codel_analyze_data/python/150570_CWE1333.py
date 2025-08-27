import re
def extract_log_data(log_text):
    log_pattern = re.compile(r'(.+?)\[(.*)\] : (.+)')
    match = log_pattern.match(log_text)
    if match:
        return match.groups()
    else:
        return None