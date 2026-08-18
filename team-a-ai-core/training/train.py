"""Local training loop utilities."""
import logging
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

logger = logging.getLogger(__name__)

def train_one_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, int]:
    """
    Execute one training epoch over local data.

    Returns:
        Tuple of (epoch_loss, sample_count).
    """
    model.train()
    total_samples = 0
    total_loss = 0.0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        batch_size = len(labels)
        total_samples += batch_size
        total_loss += loss.item() * batch_size

    avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
    return avg_loss, total_samples

def train_local_model(
    model: nn.Module,
    train_loader: DataLoader,
    epochs: int = 1,
    learning_rate: float = 0.01,
    device: torch.device | None = None,
) -> tuple[float, int]:
    """
    Train local PyTorch model for multiple epochs.

    Returns:
        Tuple of (average_loss, total_samples).
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model.to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()

    total_samples = 0
    last_epoch_loss = 0.0

    for epoch in range(epochs):
        last_epoch_loss, total_samples = train_one_epoch(
            model, train_loader, optimizer, criterion, device
        )

    return last_epoch_loss, total_samples
