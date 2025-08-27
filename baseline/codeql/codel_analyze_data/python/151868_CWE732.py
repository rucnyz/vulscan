import os

def create_config_file():
    path = "/tmp/config.txt"
    
    with open(path, "w") as f:
        f.write("admin_password=supersecret\n")

    os.chown(path, os.getuid(), os.getgid())