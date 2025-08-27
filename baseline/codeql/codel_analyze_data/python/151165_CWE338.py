import string
def create_reset_key(size: int) -> str:
    # Secure: Strong PRNG
    import secrets
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(size))
# No additional code needed after the function.