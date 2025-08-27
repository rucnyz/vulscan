import os
import shutil

def backup_data():
    src = "/etc/important_config.conf"
    dst = "/tmp/backup_config.conf"
    shutil.copy(src, dst)
    print(f"Backup saved at {dst}")

backup_data()