"""Dirichlet non-IID data distribution simulation."""
import logging
import numpy as np
import torch
from torch.utils.data import Dataset, Subset

logger = logging.getLogger(__name__)

def partition_non_iid(
    dataset: Dataset,
    num_clients: int,
    alpha: float = 0.5,
    num_classes: int = 10,
) -> list[Subset]:
    """
    Split dataset into non-IID partitions using Dirichlet allocation.

    Lower alpha -> more non-IID (each client gets fewer classes).
    Higher alpha -> more IID-like distribution.

    Args:
        dataset: Full training dataset.
        num_clients: Number of clients.
        alpha: Dirichlet concentration parameter.
        num_classes: Number of classes in the dataset.

    Returns:
        List of Subset objects, one per client.
    """
    # Group indices by label
    label_indices: dict[int, list[int]] = {c: [] for c in range(num_classes)}
    for idx in range(len(dataset)):
        _, label = dataset[idx]
        if isinstance(label, torch.Tensor):
            label = label.item()
        label_indices[label].append(idx)

    # Dirichlet allocation
    client_indices: list[list[int]] = [[] for _ in range(num_clients)]

    for c in range(num_classes):
        indices = np.array(label_indices[c])
        np.random.shuffle(indices)

        # Draw proportions from Dirichlet
        proportions = np.random.dirichlet([alpha] * num_clients)
        # Scale to actual counts
        proportions = (proportions * len(indices)).astype(int)
        # Fix rounding: assign remainder to random client
        remainder = len(indices) - proportions.sum()
        if remainder > 0:
            proportions[np.random.randint(num_clients)] += remainder

        # Distribute
        pointer = 0
        for client_id in range(num_clients):
            count = proportions[client_id]
            client_indices[client_id].extend(indices[pointer:pointer + count].tolist())
            pointer += count

    partitions = [Subset(dataset, idxs) for idxs in client_indices]

    sizes = [len(p) for p in partitions]
    logger.info(f"Non-IID partition (alpha={alpha}): {num_clients} clients, sizes={sizes}")
    return partitions
