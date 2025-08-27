import os
import stat
def save_api_tokens(token_file, secrets):
    # Check if the directory exists
    directory = os.path.dirname(token_file)
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return
    # Proceed to write the API keys to the file with ownership and permission validations
    try:
        file_exists = os.path.exists(token_file)
        if file_exists:
            file_stat = os.stat(token_file)
            file_mode = file_stat.st_mode            
            # Check if the file is owned by the current user
            if file_stat.st_uid != os.getuid():
                print(f"File '{token_file}' is not owned by the current user.")
                return
            # Check if 'group' or 'others' have any permissions
            if file_mode & 0o077:
                print(f"File '{token_file}' has group or others permissions. Aborting write operation.")
                return
        
        # Write API keys to the file
        with open(token_file, 'w') as file:
            for service, key in secrets.items():
                file.write(f"{service}:{key}\n")

        # Set secure file permissions (600)
        os.chmod(token_file, stat.S_IRUSR | stat.S_IWUSR)
        print(f"API tokens securely stored in '{token_file}'")
        
    except Exception as e:
        print(f"Error securing and writing API tokens to '{token_file}': {e}")