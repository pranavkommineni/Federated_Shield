import hashlib
import hmac
import numpy as np

FIELD_PRIME = 2_147_483_647
SCALE = 1_000_000

def encode(values: np.ndarray) -> np.ndarray:
    """Encode float values to integer field elements."""
    scaled = np.rint(np.asarray(values, dtype=np.float64) * SCALE).astype(np.int64)
    return np.mod(scaled, FIELD_PRIME).astype(object)

def decode(values: np.ndarray) -> np.ndarray:
    """Decode integer field elements back to float values."""
    vals = np.asarray(values, dtype=np.int64)
    half_prime = FIELD_PRIME // 2
    centered = np.where(vals <= half_prime, vals, vals - FIELD_PRIME).astype(np.float64)
    return centered / SCALE

def derive_pairwise_mask(seed: bytes, round_id: str, dimension: int) -> np.ndarray:
    """HMAC binds a pseudorandom pairwise mask stream to one aggregation round (vectorized)."""
    blocks = []
    num_blocks = (dimension + 7) // 8  # 32 bytes digest yields 8 u4 elements
    for counter in range(num_blocks):
        msg = f'secagg:{round_id}:{counter}'.encode()
        digest = hmac.new(seed, msg, hashlib.sha256).digest()
        blocks.append(np.frombuffer(digest, dtype='>u4'))
    
    if blocks:
        concatenated = np.concatenate(blocks)[:dimension].astype(np.int64)
        masked = np.mod(concatenated, FIELD_PRIME)
        return masked.astype(object)
    return np.array([], dtype=object)

