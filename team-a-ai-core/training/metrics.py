"""Metric calculation helpers for federated learning training/evaluation."""
import numpy as np

def compute_accuracy(predictions: np.ndarray, targets: np.ndarray) -> float:
    """Compute classification accuracy between predictions and ground truth targets."""
    if len(targets) == 0:
        return 0.0
    return float(np.mean(predictions == targets))

def compute_metrics(loss: float, accuracy: float, total_samples: int) -> dict[str, float | int]:
    """Format evaluation loss, accuracy, and sample count into a metrics dict."""
    return {
        "loss": float(loss),
        "accuracy": float(accuracy),
        "num_samples": int(total_samples),
    }
