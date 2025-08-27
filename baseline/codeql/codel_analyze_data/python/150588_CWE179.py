import os
import re
from urllib.parse import unquote

valid_path_pattern = re.compile(r'^[a-zA-Z0-9._/-]+$')
def validate_file_path(file_input_path: str) -> bool:
    if not valid_path_pattern.match(file_input_path):
        return False
    # File path is valid
    return True