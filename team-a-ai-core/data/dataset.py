"""Dataset loading and DataLoader construction utilities."""
import logging
import torch
from torch.utils.data import DataLoader, Dataset, Subset
import torchvision
import torchvision.transforms as transforms

logger = logging.getLogger(__name__)

def load_cifar10(data_dir: str = "./data") -> tuple[Dataset, Dataset]:
    """
    Download and load the CIFAR-10 dataset.

    Args:
        data_dir: Directory to store/load dataset files.

    Returns:
        Tuple of (train_dataset, test_dataset).
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
    ])

    train_dataset = torchvision.datasets.CIFAR10(
        root=data_dir, train=True, download=True, transform=transform,
    )
    test_dataset = torchvision.datasets.CIFAR10(
        root=data_dir, train=False, download=True, transform=transform,
    )

    logger.info(f"CIFAR-10 loaded: {len(train_dataset)} train, {len(test_dataset)} test samples")
    return train_dataset, test_dataset


def create_data_loaders(
    train_partition: Subset,
    test_dataset: Dataset,
    batch_size: int = 32,
) -> tuple[DataLoader, DataLoader]:
    """
    Create train and test DataLoaders for a single client.

    Args:
        train_partition: Client's training data subset.
        test_dataset: Shared test dataset.
        batch_size: Batch size for both loaders.

    Returns:
        Tuple of (train_loader, test_loader).
    """
    train_loader = DataLoader(train_partition, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader
