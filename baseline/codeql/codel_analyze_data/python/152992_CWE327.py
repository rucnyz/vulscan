import hashlib
def calc_hash(hash_name: str, data: bytes) -> bytes:
    if hash_name not in hashlib.algorithms_available:
        raise ValueError(f"Hash algorithm {hash_name} is not available")
    hasher = hashlib.new(hash_name, data)
    return hasher.digest()