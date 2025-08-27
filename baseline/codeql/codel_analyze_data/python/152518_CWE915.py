MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "application/pdf"]
def upload_file(file_db: dict, file_name: str, file_content: bytes, file_type: str):
    file_db[file_name] = file_content
    return file_db