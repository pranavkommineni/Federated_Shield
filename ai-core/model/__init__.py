"""Model architecture, hyperparameters, and weight serialization utilities."""
from .federix_model import FederixNet, create_model
from .model_config import FLConfig
from .serialization import (
    get_parameters,
    set_parameters,
    flatten_weights,
    unflatten_weights,
    get_parameter_shapes,
)

__all__ = [
    "FederixNet",
    "create_model",
    "FLConfig",
    "get_parameters",
    "set_parameters",
    "flatten_weights",
    "unflatten_weights",
    "get_parameter_shapes",
]
