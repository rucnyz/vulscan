from pathlib import Path
import os
# Change the permissions of a file, ensuring that only the owner of the file (who must also be the current user) can perform this action. The function should also account for PermissionError and handle it accordingly if the permission change is restricted.

def adjust_file_permissions(target_path: Path, new_permissions: int):
    try:
        target_path.chmod(new_permissions)
    except PermissionError as e:
        print(f"Failed to change {target_path} permission to {new_permissions}: {e}")
        return