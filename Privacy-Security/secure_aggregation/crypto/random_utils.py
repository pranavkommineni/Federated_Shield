import secrets
def secure_seed(length: int = 32) -> bytes:
    if length < 16: raise ValueError('seed must be at least 128 bits')
    return secrets.token_bytes(length)
