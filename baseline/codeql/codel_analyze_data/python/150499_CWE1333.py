import re
def get_email_domain(mail_address):
    email_pattern = re.compile(r'^[^@]+@([^@]+)$')
    match = email_pattern.match(mail_address)
    if match:
        return match.group(1)
    else:
        return None