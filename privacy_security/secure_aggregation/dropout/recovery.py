from ..exceptions import DropoutRecoveryError
def authorize_recovery(threshold: int, survivor_count: int) -> None:
    if survivor_count < threshold: raise DropoutRecoveryError('dropout recovery threshold not met')
