from ..aggregation import SecureAggregator
from ..models import MaskedUpdate, Participant, ProtocolState
from .state_machine import StateMachine

class SecureAggregationProtocol:
    def __init__(self, round_id: str, model_version: str, threshold: int): self.aggregator=SecureAggregator(round_id,model_version,threshold); self.machine=StateMachine()
    @property
    def state(self): return self.machine.state
    def register_participant(self, participant_id: str, verification_key: bytes):
        self.machine.transition(ProtocolState.INITIALIZED,ProtocolState.PARTICIPANTS_REGISTERED,target=ProtocolState.PARTICIPANTS_REGISTERED); self.aggregator.register_participant(Participant(participant_id),verification_key)
    def setup_masks(self):
        self.machine.transition(ProtocolState.PARTICIPANTS_REGISTERED,target=ProtocolState.KEY_SETUP); self.machine.transition(ProtocolState.KEY_SETUP,target=ProtocolState.MASK_SETUP); self.aggregator.start_round(); self.machine.transition(ProtocolState.MASK_SETUP,target=ProtocolState.COLLECTING_UPDATES)
    def submit_masked_update(self, update: MaskedUpdate):
        self.machine.transition(ProtocolState.COLLECTING_UPDATES,target=ProtocolState.COLLECTING_UPDATES); self.aggregator.submit_masked_update(update)
    def complete(self):
        try:
            self.machine.transition(ProtocolState.COLLECTING_UPDATES,target=ProtocolState.DROPOUT_CHECK); self.machine.transition(ProtocolState.DROPOUT_CHECK,target=ProtocolState.MASK_RECONSTRUCTION); self.machine.transition(ProtocolState.MASK_RECONSTRUCTION,target=ProtocolState.AGGREGATION); result=self.aggregator.aggregate(); self.machine.transition(ProtocolState.AGGREGATION,target=ProtocolState.COMPLETED); return result
        except Exception:
            self.machine.state=ProtocolState.FAILED; raise
