import string
import re
def generate_access_token(api_length: int) -> str:
    # Using weak pseudo-random number generator (vulnerable code)
    import random
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(characters, k=api_length))
# No additional code needed after the function.