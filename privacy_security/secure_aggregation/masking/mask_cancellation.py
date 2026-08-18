import numpy as np
def cancel_dropout_masks(protected_sum: np.ndarray, correction: np.ndarray) -> np.ndarray:
    if protected_sum.shape != correction.shape: raise ValueError('correction dimension mismatch')
    return protected_sum + correction
