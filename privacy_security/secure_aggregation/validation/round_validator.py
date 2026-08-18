from ..exceptions import InvalidRoundError
def matches(value: str, expected: str) -> None:
    if value != expected: raise InvalidRoundError('round_id does not match active round')
