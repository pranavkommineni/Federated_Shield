"""Client-only plaintext and private-key boundary for the prototype."""
import secrets
import numpy as np
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from .crypto.key_exchange import derive_pairwise_key
from .crypto.pairwise_mask import encode, derive_pairwise_mask, FIELD_PRIME
from .crypto.secret_sharing import split_secret
from .models import ModelUpdate, MaskedUpdate

def payload(update, protected, submission_id):
    return b'|'.join([update.participant_id.encode(),update.round_id.encode(),update.model_version.encode(),submission_id.encode(),b','.join(str(int(x)).encode() for x in protected)])

class SecureAggregationClient:
    def __init__(self, participant_id: str):
        self.participant_id=participant_id; self._agreement=X25519PrivateKey.generate(); self._signing=Ed25519PrivateKey.generate(); self._peers={}; self._shares={}
    @property
    def agreement_public_key(self): return self._agreement.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    @property
    def verification_key(self): return self._signing.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    def configure_peers(self, public_keys: dict[str, bytes]): self._peers={key:value for key,value in public_keys.items() if key!=self.participant_id}
    def recovery_shares(self, recipient_ids: list[str], threshold: int, round_id: str):
        result={}
        for peer in self._peers:
            key=derive_pairwise_key(self._agreement,self._peers[peer],round_id)
            for recipient,share in zip(recipient_ids,split_secret(key,threshold,len(recipient_ids))): result[(peer,recipient)]=share
        return result
    def receive_recovery_share(self, owner: str, share): self._shares.setdefault(owner,[]).append(share)
    def recovery_share_for(self, owner: str): return self._shares.get(owner,[])
    def mask_update(self, update: ModelUpdate) -> MaskedUpdate:
        if update.participant_id!=self.participant_id: raise ValueError('client may mask only its own update')
        protected=encode(update.update_data)
        for peer,public in self._peers.items():
            mask=derive_pairwise_mask(derive_pairwise_key(self._agreement,public,update.round_id),update.round_id,update.update_data.size)
            protected=np.mod(protected + (mask if self.participant_id<peer else -mask),FIELD_PRIME)
        submission_id=secrets.token_urlsafe(18); signature=self._signing.sign(payload(update,protected,submission_id))
        return MaskedUpdate(update.participant_id,update.round_id,update.model_version,protected,submission_id,signature)
