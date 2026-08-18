from dataclasses import dataclass
import numpy as np
from ..exceptions import InvalidUpdateError

@dataclass(frozen=True)
class MaskedUpdate:
    participant_id: str
    round_id: str
    model_version: str
    protected_data: np.ndarray
    submission_id: str
    signature: bytes
    def __post_init__(self):
        value=np.asarray(self.protected_data,dtype=object)
        if value.ndim!=1 or value.size==0 or not all(isinstance(int(x),int) for x in value): raise InvalidUpdateError('protected_data must be a non-empty integer field vector')
        if not self.submission_id or not self.signature: raise InvalidUpdateError('signed submission metadata is required')
        object.__setattr__(self, 'protected_data',value.copy())
