import numpy as np
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from ..dropout import detect, require_threshold
from ..exceptions import DuplicateSubmissionError, InvalidParticipantError, InvalidUpdateError, DropoutRecoveryError
from ..crypto.pairwise_mask import FIELD_PRIME, decode, derive_pairwise_mask
from ..crypto.secret_sharing import reconstruct_secret
from ..client import payload
from ..models import AggregationResult, MaskedUpdate, Participant
from ..validation import compatible, registered
from .aggregation_state import AggregationState

class SecureAggregator:
    """Receives only masked vectors and returns a sum, not a FedAvg average."""
    def __init__(self, round_id: str, model_version: str, threshold: int):
        self.round_id,self.model_version,self.threshold=round_id,model_version,threshold; self.participants={}; self.verification_keys={}; self.state=AggregationState(); self._started=False; self._submission_ids=set()
    def register_participant(self, participant: Participant, verification_key: bytes) -> None:
        if self._started: raise InvalidParticipantError('registration is closed')
        if participant.participant_id in self.participants: raise DuplicateSubmissionError('duplicate participant')
        self.participants[participant.participant_id]=participant; self.verification_keys[participant.participant_id]=verification_key
    def start_round(self) -> None:
        if not 2 <= self.threshold <= len(self.participants): raise InvalidParticipantError('threshold must be between 2 and registered participants')
        self._started=True
    def submit_masked_update(self, update: MaskedUpdate) -> None:
        registered(update.participant_id, set(self.participants))
        if update.participant_id in self.state.updates: raise DuplicateSubmissionError('duplicate submission')
        if update.submission_id in self._submission_ids: raise DuplicateSubmissionError('replayed submission id')
        compatible(update, self.round_id, self.model_version, self.state.dimension)
        try: Ed25519PublicKey.from_public_bytes(self.verification_keys[update.participant_id]).verify(update.signature,payload(update,update.protected_data,update.submission_id))
        except InvalidSignature as error: raise InvalidUpdateError('invalid masked-update signature') from error
        self.state.updates[update.participant_id]=update; self._submission_ids.add(update.submission_id)
    def check_participants(self): return detect(set(self.participants), set(self.state.updates), self.threshold)
    def aggregate(self) -> AggregationResult:
        if not self._started or not self.state.updates: raise RuntimeError('no aggregation inputs')
        information=self.check_participants(); require_threshold(len(information.received), self.threshold)
        if information.missing:
            raise DropoutRecoveryError('dropout aggregation requires client-supplied threshold recovery shares')
        protected_sum=np.asarray([0]*self.state.dimension,dtype=object)
        for update in self.state.updates.values(): protected_sum=np.mod(protected_sum+update.protected_data,FIELD_PRIME)
        return AggregationResult(self.round_id,self.model_version,decode(protected_sum),tuple(sorted(information.received)),information)
