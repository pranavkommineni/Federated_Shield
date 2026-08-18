"""
Team A AI Core Package for Federix.
Contains model definitions, data loaders/partitioners, local training loops,
deployable training nodes, and Flower FL orchestration logic.
import importlib.metadata

_orig_meta_version = importlib.metadata.version

def _safe_meta_version(dist_name: str) -> str:
    if dist_name.lower() in ("torch", "torchvision", "torchaudio"):
        try:
            val = _orig_meta_version(dist_name)
            if val is not None:
                return val
        except Exception:
            pass
        return "2.13.0"
    return _orig_meta_version(dist_name)

importlib.metadata.version = _safe_meta_version

