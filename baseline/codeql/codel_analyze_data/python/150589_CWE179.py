import os
import re
from urllib.parse import unquote

valid_path_pattern = re.compile(r'^[a-zA-Z0-9._/-]+$')
def validate_file_path(file_input_path: str) -> bool:
    # Canonicalize the file path by decoding URL-encoded characters
    canonicalized_path = unquote(file_input_path)
    
    # Ensure the canonicalized path doesn't contain dangerous components such as '..'
    if not valid_path_pattern.match(canonicalized_path) or '..' in canonicalized_path:
        return False
    
    # Additional check to disallow absolute file paths (depending on system requirement)
    if os.path.isabs(canonicalized_path):
        return False

    # Prevent any further manipulation of filesystem by checking directory traversal attempts
    real_path = os.path.realpath(canonicalized_path)
    if ".." in real_path.split(os.path.sep) or "." in real_path.split(os.path.sep):
        return False
    # File path is valid
    return True