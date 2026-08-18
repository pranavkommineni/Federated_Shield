from dataclasses import dataclass, field
from ..models import MaskedUpdate
@dataclass
class AggregationState:
    updates: dict[str, MaskedUpdate] = field(default_factory=dict)
    @property
    def dimension(self): return next(iter(self.updates.values())).protected_data.size if self.updates else None
