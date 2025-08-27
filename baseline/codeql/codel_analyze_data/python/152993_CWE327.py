import hashlib
def calc_hash(hash_name: str, data: bytes) -> bytes:
    if hash_name not in hashlib.algorithms_available:
        raise ValueError(f"Hash algorithm {hash_name} is not available")
    safe_hash_names = ["sha256", "sha512", "sha244", "sha384", "blake2s"]
    if hash_name not in safe_hash_names:
        raise ValueError(f"Hash algorithm {hash_name} is not available")
    hasher = hashlib.new(hash_name, data)
    return hasher.digest()