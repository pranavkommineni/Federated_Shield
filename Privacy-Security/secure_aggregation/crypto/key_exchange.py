from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def derive_pairwise_key(private_key: X25519PrivateKey, peer_public: bytes, round_id: str) -> bytes:
    """Only the two X25519 private-key holders can derive this per-round mask key."""
    shared=private_key.exchange(X25519PublicKey.from_public_bytes(peer_public))
    return HKDF(algorithm=hashes.SHA256(), length=16, salt=None, info=f'secagg:{round_id}'.encode()).derive(shared)
