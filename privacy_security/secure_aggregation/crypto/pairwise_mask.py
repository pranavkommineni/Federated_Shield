import hashlib, hmac
import numpy as np

FIELD_PRIME = 2_147_483_647
SCALE = 1_000_000
def encode(values: np.ndarray) -> np.ndarray: return np.mod(np.rint(values*SCALE).astype(object), FIELD_PRIME)
def decode(values: np.ndarray) -> np.ndarray:
    centered=np.asarray([int(v) if int(v)<=FIELD_PRIME//2 else int(v)-FIELD_PRIME for v in values],dtype=np.float64)
    return centered/SCALE
def derive_pairwise_mask(seed: bytes, round_id: str, dimension: int) -> np.ndarray:
    """HMAC binds a pseudorandom pairwise mask stream to one aggregation round."""
    blocks=[]; counter=0
    while len(blocks) < dimension:
        blocks.extend(np.frombuffer(hmac.new(seed, f'secagg:{round_id}:{counter}'.encode(), hashlib.sha256).digest(), dtype='>u4'))
        counter += 1
    return np.asarray([int(x) % FIELD_PRIME for x in blocks[:dimension]], dtype=object)
