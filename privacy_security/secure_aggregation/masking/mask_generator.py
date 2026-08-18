from ..models import ModelUpdate, MaskedUpdate
from .mask_manager import MaskManager
def generate_masked_update(update: ModelUpdate, manager: MaskManager) -> MaskedUpdate:
    return MaskedUpdate(update.participant_id, update.round_id, update.model_version, update.update_data + manager.mask_for(update.participant_id, update.update_data.size))
