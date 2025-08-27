import hashlib
import hmac
secret_key = b'supersecret'
def sign_data(hash_algorithm: str, content: bytes) -> bytes:
    if hash_algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Hash algorithm {hash_algorithm} is not available")
    hash_function = getattr(hashlib, hash_algorithm)
    signature = hmac.new(secret_key, content, hash_function).digest()
    return signature