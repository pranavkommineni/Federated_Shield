"""IID data partitioning utilities for federated learning."""
import logging
import numpy as np
from torch.utils.data import Dataset, Subset
from .non_iid import partition_non_iid

logger = logging.getLogger(__name__)

def partition_iid(dataset: Dataset, num_clients: int) -> list[Subset]:
    """
    Split dataset into equal-sized IID partitions for each client.

    Args:
        dataset: Full training dataset.
        num_clients: Number of clients to partition data across.

    Returns:
        List of Subset objects, one per client.
    """
    total = len(dataset)
    indices = np.random.permutation(total)
    splits = np.array_split(indices, num_clients)

    partitions = [Subset(dataset, split.tolist()) for split in splits]
    logger.info(f"IID partition: {num_clients} clients, sizes={[len(p) for p in partitions]}")
    return partitions


def partition_data(
    dataset: Dataset,
    num_clients: int,
    iid: bool = True,
    alpha: float = 0.5,
) -> list[Subset]:
    """
    Partition dataset for federated learning clients.

    Args:
        dataset: Full training dataset.
        num_clients: Number of clients.
        iid: If True, use IID partitioning. If False, use Dirichlet non-IID.
        alpha: Dirichlet concentration (only used when iid=False).

    Returns:
        List of Subset objects, one per client.
    """
    if iid:
        return partition_iid(dataset, num_clients)
    else:
        return partition_non_iid(dataset, num_clients, alpha=alpha)
