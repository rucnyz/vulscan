
def generate_secure_key(bits: int) -> str:
    # Secure: Strong PRNG for generating encryption key (patched code)
    import secrets
    acceptable_bits = {128, 192, 256}
    if bits not in acceptable_bits:
        raise ValueError("Invalid key size provided. Use 128, 192, or 256 bits.")
    
    bytes_key = secrets.token_bytes(bits // 8)
    return bytes_key.hex()
# No additional code needed after the function.