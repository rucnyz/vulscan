import re
from urllib.parse import unquote

email_pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
BLACKLISTED_DOMAINS = ['.xyz', '.ru']
def validate_email(mail: str) -> bool:
    if not email_pattern.match(mail):
        return False
    return True