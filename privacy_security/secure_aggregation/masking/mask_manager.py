import numpy as np
from ..crypto import PairwiseKeySetup, derive_pairwise_mask

class MaskManager:
    def __init__(self, participant_ids: set[str], round_id: str): self.ids=frozenset(participant_ids); self.round_id=round_id; self.keys=PairwiseKeySetup(participant_ids)
    def mask_for(self, participant_id: str, dimension: int) -> np.ndarray:
        result=np.zeros(dimension)
        for other in self.ids-{participant_id}:
            mask=derive_pairwise_mask(self.keys.seed_for(participant_id, other), self.round_id, dimension)
            result += mask if participant_id < other else -mask
        return result
    def dropout_correction(self, received: set[str], dimension: int) -> np.ndarray:
        correction=np.zeros(dimension)
        for contributor in received:
            for missing in self.ids-received:
                contribution=derive_pairwise_mask(self.keys.seed_for(contributor, missing), self.round_id, dimension)
                correction -= contribution if contributor < missing else -contribution
        return correction
