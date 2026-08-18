from dataclasses import dataclass
import numpy as np
from ..exceptions import InvalidUpdateError

def vector(data):
    value = np.asarray(data, dtype=np.float64)
    if value.ndim != 1 or value.size == 0 or not np.isfinite(value).all():
        raise InvalidUpdateError('update_data must be a non-empty finite vector')
    return value.copy()

@dataclass(frozen=True)
class ModelUpdate:
    participant_id: str
    round_id: str
    model_version: str
    update_data: np.ndarray
    def __post_init__(self):
        if not all(isinstance(x, str) and x for x in (self.participant_id, self.round_id, self.model_version)):
            raise InvalidUpdateError('participant_id, round_id, and model_version are required')
        object.__setattr__(self, 'update_data', vector(self.update_data))
