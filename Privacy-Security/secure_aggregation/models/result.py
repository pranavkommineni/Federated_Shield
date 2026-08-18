from dataclasses import dataclass
import numpy as np
from .model_update import vector

@dataclass(frozen=True)
class DropoutInformation:
    expected: frozenset[str]; received: frozenset[str]; missing: frozenset[str]; threshold_met: bool

@dataclass(frozen=True)
class AggregationResult:
    round_id: str; model_version: str; aggregate_update: np.ndarray; contributors: tuple[str, ...]; dropout_information: DropoutInformation
    def __post_init__(self): object.__setattr__(self, 'aggregate_update', vector(self.aggregate_update))
