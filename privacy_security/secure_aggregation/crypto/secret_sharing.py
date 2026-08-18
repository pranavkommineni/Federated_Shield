from Crypto.Protocol.SecretSharing import Shamir
from ..exceptions import DropoutRecoveryError

def split_secret(secret: bytes, threshold: int, count: int) -> list[tuple[int, bytes]]:
    if len(secret) != 16: raise ValueError('Shamir backend requires a 16-byte secret')
    return Shamir.split(threshold, count, secret)

def reconstruct_secret(shares: list[tuple[int, bytes]], threshold: int) -> bytes:
    if len(shares) < threshold: raise DropoutRecoveryError('insufficient recovery shares')
    return Shamir.combine(shares[:threshold])
