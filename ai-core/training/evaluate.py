"""Local and global model evaluation utilities."""
import logging
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

logger = logging.getLogger(__name__)

def evaluate_model(
    model: nn.Module,
    test_loader: DataLoader,
    device: torch.device | None = None,
) -> tuple[float, float, int]:
    """
    Evaluate PyTorch model on a dataset.

    Returns:
        Tuple of (average_loss, accuracy, total_samples).
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model.to(device)
    model.eval()
    criterion = nn.CrossEntropyLoss()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * len(labels)
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == labels).sum().item()
            total += len(labels)

    avg_loss = total_loss / total if total > 0 else 0.0
    accuracy = correct / total if total > 0 else 0.0

    return avg_loss, accuracy, total
