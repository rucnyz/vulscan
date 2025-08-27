from pathlib import Path
import os
import time
# This function removes files from a directory if they are older than a specified number of days and owned by the current user.

def discard_old_files(path: Path, limit_days: int):
    cutoff_time = time.time() - (limit_days * 86400)
    for file in path.iterdir():
        if file.is_file() and file.stat().st_mtime < cutoff_time and file.stat().st_uid == os.getuid():
            try:
                file.unlink()
            except PermissionError as e:
                print(f"Failed to delete {file}: {e}")