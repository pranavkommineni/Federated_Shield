from ..exceptions import ProtocolStateError
from ..models import ProtocolState

class StateMachine:
    def __init__(self): self.state=ProtocolState.INITIALIZED
    def transition(self, *allowed, target: ProtocolState):
        if self.state not in allowed: raise ProtocolStateError(f'invalid transition from {self.state}')
        self.state=target
