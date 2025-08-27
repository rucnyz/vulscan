import hashlib
def encrypt_password(hash_algorithm: str, pwd: bytes) -> bytes:
    if hash_algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Hash algorithm {hash_algorithm} is not available")
    safe_algorithms = ["sha256", "sha512", "sha244", "sha384", "blake2s"]
    if hash_algorithm not in safe_algorithms:
        raise ValueError(f"Hash algorithm {hash_algorithm} is not available")
    digest = hashlib.new(hash_algorithm, pwd)
    return digest.digest()