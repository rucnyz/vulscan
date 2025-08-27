import string
import re
def generate_access_token(api_length: int) -> str:
    # Using secure pseudo-random number generator (patched code)
    import secrets
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(api_length))
# No additional code needed after the function.