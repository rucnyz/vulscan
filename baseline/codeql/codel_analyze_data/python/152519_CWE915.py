MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "application/pdf"]

def upload_file_safe(file_db: dict, file_name: str, file_content: bytes, file_type: str):
    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024)} MB.")

    if file_type not in ALLOWED_FILE_TYPES:
        raise ValueError(f"File type {file_type} is not allowed. Allowed types are: {', '.join(ALLOWED_FILE_TYPES)}.")

    # Check if the file already exists in the database
    if file_name in file_db:
        raise ValueError(f"A file with the name {file_name} already exists in the database.")

    # Add the file to the database
    file_db[file_name] = {
        "content": file_content,
        "type": file_type,
        "size": len(file_content)
    }

    return file_db