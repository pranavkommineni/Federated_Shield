"""Configuration classes for the federated learning pipeline."""
from dataclasses import dataclass

@dataclass(frozen=True)
class FLConfig:
    """Federated learning configuration parameters."""
    server_address: str = '0.0.0.0:8080'
    num_rounds: int = 5
    min_fit_clients: int = 2
    min_available_clients: int = 2
    min_evaluate_clients: int = 2
    fraction_fit: float = 1.0
    fraction_evaluate: float = 1.0
    local_epochs: int = 1
    batch_size: int = 32
    learning_rate: float = 0.01
    round_timeout: float = 120.0
    use_secure_aggregation: bool = False
