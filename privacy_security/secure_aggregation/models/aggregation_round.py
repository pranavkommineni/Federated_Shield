from dataclasses import dataclass, field
from enum import Enum

class ProtocolState(str, Enum):
    INITIALIZED='initialized'; PARTICIPANTS_REGISTERED='participants_registered'; KEY_SETUP='key_setup'; MASK_SETUP='mask_setup'; COLLECTING_UPDATES='collecting_updates'; DROPOUT_CHECK='dropout_check'; MASK_RECONSTRUCTION='mask_reconstruction'; AGGREGATION='aggregation'; COMPLETED='completed'; FAILED='failed'

@dataclass
class AggregationRound:
    round_id: str
    model_version: str
    threshold: int
    participant_ids: set[str] = field(default_factory=set)
    state: ProtocolState = ProtocolState.INITIALIZED
