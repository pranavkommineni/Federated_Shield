from ..exceptions import InvalidUpdateError
def compatible(update, round_id: str, model_version: str, dimension: int | None) -> None:
    if update.round_id != round_id: raise InvalidUpdateError('incorrect round')
    if update.model_version != model_version: raise InvalidUpdateError('incorrect model version')
    if dimension is not None and update.protected_data.size != dimension: raise InvalidUpdateError('inconsistent update dimension')
