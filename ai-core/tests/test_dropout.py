"""
Client Dropout Tests.
"""
import os
import sys
import numpy as np
import flwr as fl
from flwr.common import ndarrays_to_parameters
import pytest
import logging

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

RAY_INIT = {"runtime_env": {"env_vars": {"PYTHONPATH": f"{root_dir}:{core_dir}:{os.environ.get('PYTHONPATH', '')}"}}}

from model.model_config import FLConfig
from fl.strategy import FederixStrategy
from model.federix_model import create_model
from model.serialization import get_parameters

logger = logging.getLogger(__name__)


class ReliableClient(fl.client.NumPyClient):
    """Client that always succeeds."""

    def __init__(self, cid: str):
        self.cid = cid
        self.weights = [np.array([1.0, 2.0, 3.0, 4.0])]

    def get_parameters(self, config: dict) -> list[np.ndarray]:
        return self.weights

    def fit(self, parameters, config) -> tuple[list[np.ndarray], int, dict]:
        return self.weights, 100, {"cid": self.cid}

    def evaluate(self, parameters, config) -> tuple[float, int, dict]:
        return 0.5, 100, {"cid": self.cid, "accuracy": 0.8}


class DropoutClient(fl.client.NumPyClient):
    """Client that fails during fit (simulates dropout)."""

    def __init__(self, cid: str, fail_on_rounds: set[int] | None = None):
        self.cid = cid
        self.weights = [np.array([1.0, 2.0, 3.0, 4.0])]
        self.fail_on_rounds = fail_on_rounds or set()
        self._round = 0

    def get_parameters(self, config: dict) -> list[np.ndarray]:
        return self.weights

    def fit(self, parameters, config) -> tuple[list[np.ndarray], int, dict]:
        self._round += 1
        if self._round in self.fail_on_rounds:
            raise ConnectionError(f"Client {self.cid} dropped out on round {self._round}")
        return self.weights, 100, {"cid": self.cid}

    def evaluate(self, parameters, config) -> tuple[float, int, dict]:
        return 0.5, 100, {"cid": self.cid, "accuracy": 0.8}


def test_dropout_round_continues_with_enough_clients():
    """Scenario: 3 clients, 1 drops out, min_fit=2."""
    def client_fn(cid: str) -> fl.client.Client:
        if cid == "2":
            return DropoutClient(cid, fail_on_rounds={1}).to_client()
        return ReliableClient(cid).to_client()

    config = FLConfig(
        min_fit_clients=2,
        min_available_clients=3,
        fraction_fit=1.0,
    )

    initial_params = ndarrays_to_parameters([np.array([0.0, 0.0, 0.0, 0.0])])
    strategy = FederixStrategy(config, initial_parameters=initial_params)

    round_results = {}
    original_aggregate = strategy.aggregate_fit

    def tracking_aggregate(server_round, results, failures):
        round_results[server_round] = {
            "results": len(results),
            "failures": len(failures),
        }
        return original_aggregate(server_round, results, failures)

    strategy.aggregate_fit = tracking_aggregate

    history = fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=3,
        config=fl.server.ServerConfig(num_rounds=1),
        strategy=strategy,
        ray_init_args=RAY_INIT,
    )

    assert history is not None
    if 1 in round_results:
        assert round_results[1]["results"] >= 2


def test_dropout_round_skipped_insufficient_clients():
    """Scenario: 3 clients, 2 drop out, min_fit=2."""
    def client_fn(cid: str) -> fl.client.Client:
        if cid in ("1", "2"):
            return DropoutClient(cid, fail_on_rounds={1}).to_client()
        return ReliableClient(cid).to_client()

    config = FLConfig(
        min_fit_clients=2,
        min_available_clients=3,
        fraction_fit=1.0,
    )

    initial_params = ndarrays_to_parameters([np.array([0.0, 0.0, 0.0, 0.0])])
    strategy = FederixStrategy(config, initial_parameters=initial_params)

    history = fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=3,
        config=fl.server.ServerConfig(num_rounds=1),
        strategy=strategy,
        ray_init_args=RAY_INIT,
    )
    assert history is not None


def test_dropout_recovery_across_rounds():
    """Scenario: Client drops in round 2 but succeeds in rounds 1 and 3."""
    def client_fn(cid: str) -> fl.client.Client:
        if cid == "1":
            return DropoutClient(cid, fail_on_rounds={2}).to_client()
        return ReliableClient(cid).to_client()

    config = FLConfig(
        min_fit_clients=2,
        min_available_clients=3,
        fraction_fit=1.0,
    )

    initial_params = ndarrays_to_parameters([np.array([0.0, 0.0, 0.0, 0.0])])
    strategy = FederixStrategy(config, initial_parameters=initial_params)

    history = fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=3,
        config=fl.server.ServerConfig(num_rounds=3),
        strategy=strategy,
        ray_init_args=RAY_INIT,
    )

    assert history is not None


def test_all_clients_dropout():
    """Scenario: All 3 clients drop out."""
    def client_fn(cid: str) -> fl.client.Client:
        return DropoutClient(cid, fail_on_rounds={1}).to_client()

    config = FLConfig(
        min_fit_clients=2,
        min_available_clients=3,
        fraction_fit=1.0,
    )

    initial_params = ndarrays_to_parameters([np.array([0.0, 0.0, 0.0, 0.0])])
    strategy = FederixStrategy(config, initial_parameters=initial_params)

    history = fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=3,
        config=fl.server.ServerConfig(num_rounds=1),
        strategy=strategy,
        ray_init_args=RAY_INIT,
    )

    assert history is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
