import re
from urllib.parse import unquote

email_pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
BLACKLISTED_DOMAINS = ['.xyz', '.ru']
def validate_email(mail: str) -> bool:
    canonicalized_mail = unquote(mail)

    if not email_pattern.match(canonicalized_mail):
        return False

    if "<" in canonicalized_mail or ">" in canonicalized_mail or "(" in canonicalized_mail:
        return False

    if any(canonicalized_mail.lower().endswith(domain) for domain in BLACKLISTED_DOMAINS):
        return False
    return True