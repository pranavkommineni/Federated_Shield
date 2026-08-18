from ..exceptions import InvalidParticipantError
def registered(participant_id: str, participants: set[str]) -> None:
    if participant_id not in participants: raise InvalidParticipantError('participant is not registered')
