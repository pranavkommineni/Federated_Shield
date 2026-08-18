"""Metric calculation helpers for federated learning training/evaluation."""
import numpy as np

def compute_accuracy(predictions: np.ndarray, targets: np.ndarray) -> float:
    """Compute classification accuracy between predictions and ground truth targets."""
    if len(targets) == 0:
        return 0.0
    return float(np.mean(predictions == targets))

def compute_precision_recall_f1(
    predictions: np.ndarray, targets: np.ndarray, num_classes: int = 10
) -> tuple[float, float, float]:
    """
    Compute macro-averaged precision, recall, and F1-score across classes.

    Args:
        predictions: 1D array of predicted class indices.
        targets: 1D array of ground-truth target indices.
        num_classes: Total number of classes.

    Returns:
        Tuple of (precision, recall, f1_score).
    """
    if len(targets) == 0:
        return 0.0, 0.0, 0.0

    precisions = []
    recalls = []

    for c in range(num_classes):
        tp = np.sum((predictions == c) & (targets == c))
        fp = np.sum((predictions == c) & (targets != c))
        fn = np.sum((predictions != c) & (targets == c))

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        precisions.append(prec)
        recalls.append(rec)

    macro_precision = float(np.mean(precisions))
    macro_recall = float(np.mean(recalls))
    if macro_precision + macro_recall > 0:
        macro_f1 = 2 * (macro_precision * macro_recall) / (macro_precision + macro_recall)
    else:
        macro_f1 = 0.0

    return macro_precision, macro_recall, macro_f1


def compute_metrics(
    loss: float,
    accuracy: float,
    total_samples: int,
    precision: float | None = None,
    recall: float | None = None,
    f1_score: float | None = None,
) -> dict[str, float | int]:
    """Format evaluation loss, accuracy, and optional metrics into a metrics dict."""
    metrics: dict[str, float | int] = {
        "loss": float(loss),
        "accuracy": float(accuracy),
        "num_samples": int(total_samples),
    }
    if precision is not None:
        metrics["precision"] = float(precision)
    if recall is not None:
        metrics["recall"] = float(recall)
    if f1_score is not None:
        metrics["f1_score"] = float(f1_score)
    return metrics

