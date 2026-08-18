from dataclasses import dataclass
from ..exceptions import InvalidParticipantError

@dataclass(frozen=True)
class Participant:
    participant_id: str
    def __post_init__(self):
        if not isinstance(self.participant_id, str) or not self.participant_id.strip():
            raise InvalidParticipantError('participant_id must be a non-empty string')
