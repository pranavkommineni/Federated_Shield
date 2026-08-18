from dataclasses import dataclass

@dataclass(frozen=True)
class SecureAggregationConfig:
    threshold: int
    max_vector_length: int = 1_000_000
