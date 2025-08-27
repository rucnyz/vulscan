import os
import shutil
import stat

def secure_backup_data():
    src = "/etc/important_config.conf"
    dst = "/tmp/backup_config.conf"
    shutil.copy(src, dst)
    os.chmod(dst, stat.S_IRUSR | stat.S_IWUSR)  # 600 permission
    print(f"Secure backup saved at {dst}")

secure_backup_data()