"""Flower client, server, and custom strategy modules."""
from .client import FederixClient
from .server import start_fl_server, build_strategy
from .strategy import FederixStrategy, SecureFederixStrategy
from .simulation import run_fl_simulation, extract_round_metrics, FLSimulationError

__all__ = [
    "FederixClient",
    "start_fl_server",
    "build_strategy",
    "FederixStrategy",
    "SecureFederixStrategy",
    "run_fl_simulation",
    "extract_round_metrics",
    "FLSimulationError",
]

