from ..exceptions import InsufficientParticipantsError
def require_threshold(received_count: int, threshold: int) -> None:
    if received_count < threshold: raise InsufficientParticipantsError(f'{received_count} protected updates received; threshold is {threshold}')
