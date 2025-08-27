import os

def create_secure_config_file():
    path = "/tmp/config.txt"
    
    fd = os.open(path, os.O_WRONLY | os.O_CREAT, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write("admin_password=supersecret\n")

    os.chown(path, os.getuid(), os.getgid())

create_secure_config_file()