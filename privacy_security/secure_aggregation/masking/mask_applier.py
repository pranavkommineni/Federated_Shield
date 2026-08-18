import numpy as np
def apply_mask(vector: np.ndarray, mask: np.ndarray) -> np.ndarray:
    if vector.shape != mask.shape: raise ValueError('mask dimension mismatch')
    return vector + mask
