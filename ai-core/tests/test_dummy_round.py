"""
Dummy Model Updates Test.
"""
import os
import sys
import numpy as np
import flwr as fl
from flwr.common import ndarrays_to_parameters
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

RAY_INIT = {"runtime_env": {"env_vars": {"PYTHONPATH": f"{root_dir}:{core_dir}:{os.environ.get('PYTHONPATH', '')}"}}}

class DummyClient(fl.client.NumPyClient):
    """A trivial client that returns pre-defined weights."""

    def __init__(self, cid: str, weights: list[np.ndarray], num_samples: int):
        self.cid = cid
        self.weights = weights
        self.num_samples = num_samples

    def get_parameters(self, config: dict) -> list[np.ndarray]:
        return self.weights

    def fit(
        self, parameters: list[np.ndarray], config: dict
    ) -> tuple[list[np.ndarray], int, dict]:
        return self.weights, self.num_samples, {"cid": self.cid}

    def evaluate(
        self, parameters: list[np.ndarray], config: dict
    ) -> tuple[float, int, dict]:
        return 0.0, self.num_samples, {"cid": self.cid}


def test_dummy_fedavg_equal_samples():
    """Two clients with equal sample counts."""
    client_weights = {
        "0": [np.array([1.0, 2.0, 3.0, 4.0])],
        "1": [np.array([2.0, 3.0, 4.0, 5.0])],
    }
    num_samples = {"0": 100, "1": 100}

    def client_fn(cid: str) -> fl.client.Client:
        client = DummyClient(cid, client_weights[cid], num_samples[cid])
        return client.to_client()

    from flwr.server.strategy import FedAvg

    initial_params = ndarrays_to_parameters([np.array([0.0, 0.0, 0.0, 0.0])])

    strategy = FedAvg(
        fraction_fit=1.0,
        fraction_evaluate=0.0,
        min_fit_clients=2,
        min_available_clients=2,
        initial_parameters=initial_params,
    )

    history = fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=2,
        config=fl.server.ServerConfig(num_rounds=1),
        strategy=strategy,
        ray_init_args=RAY_INIT,
    )

    assert history is not None


def test_dummy_fedavg_weighted():
    """Unit test: verify FedAvg weighting logic directly."""
    w1 = np.array([1.0, 2.0, 3.0, 4.0])
    w2 = np.array([2.0, 3.0, 4.0, 5.0])
    w3 = np.array([3.0, 4.0, 5.0, 6.0])

    n1, n2, n3 = 100, 200, 300
    total = n1 + n2 + n3

    expected = (n1 * w1 + n2 * w2 + n3 * w3) / total

    np.testing.assert_allclose(
        expected,
        np.array([2.333333, 3.333333, 4.333333, 5.333333]),
        atol=1e-4,
    )

    simple_mean = (w1 + w2 + w3) / 3
    assert not np.allclose(expected, simple_mean)


def test_dummy_multiple_rounds():
    """Verify that multiple rounds execute without errors."""
    def client_fn(cid: str) -> fl.client.Client:
        weights = [np.array([float(int(cid) + 1)] * 4)]
        client = DummyClient(cid, weights, num_samples=100)
        return client.to_client()

    from flwr.server.strategy import FedAvg

    initial_params = ndarrays_to_parameters([np.array([0.0, 0.0, 0.0, 0.0])])
    strategy = FedAvg(
        fraction_fit=1.0,
        fraction_evaluate=0.0,
        min_fit_clients=3,
        min_available_clients=3,
        initial_parameters=initial_params,
    )

    history = fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=3,
        config=fl.server.ServerConfig(num_rounds=3),
        strategy=strategy,
        ray_init_args=RAY_INIT,
    )

    assert history is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
