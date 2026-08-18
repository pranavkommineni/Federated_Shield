"""
FedAvg + Multiple Clients (Weighted Averaging) Tests.
"""
import os
import sys
import numpy as np
import flwr as fl
from flwr.common import ndarrays_to_parameters, parameters_to_ndarrays
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

class WeightedDummyClient(fl.client.NumPyClient):
    """Client that returns pre-set weights and a specific sample count."""

    def __init__(self, cid: str, weights: list[np.ndarray], num_samples: int):
        self.cid = cid
        self.weights = weights
        self.num_samples = num_samples

    def get_parameters(self, config: dict) -> list[np.ndarray]:
        return self.weights

    def fit(self, parameters, config) -> tuple[list[np.ndarray], int, dict]:
        return self.weights, self.num_samples, {"cid": self.cid}

    def evaluate(self, parameters, config) -> tuple[float, int, dict]:
        return 0.0, self.num_samples, {"cid": self.cid}


def test_weighted_fedavg_three_clients():
    """
    Client 0: 100 samples, weights [1, 2, 3, 4]
    Client 1: 200 samples, weights [2, 3, 4, 5]
    Client 2: 300 samples, weights [3, 4, 5, 6]

    Weighted FedAvg = (100*[1,2,3,4] + 200*[2,3,4,5] + 300*[3,4,5,6]) / 600
    """
    configs = {
        "0": {"weights": [np.array([1.0, 2.0, 3.0, 4.0])], "samples": 100},
        "1": {"weights": [np.array([2.0, 3.0, 4.0, 5.0])], "samples": 200},
        "2": {"weights": [np.array([3.0, 4.0, 5.0, 6.0])], "samples": 300},
    }

    def client_fn(cid: str) -> fl.client.Client:
        cfg = configs[cid]
        return WeightedDummyClient(cid, cfg["weights"], cfg["samples"]).to_client()

    initial_params = ndarrays_to_parameters([np.array([0.0, 0.0, 0.0, 0.0])])

    from flwr.server.strategy import FedAvg

    aggregated_result = {}

    class CaptureFedAvg(FedAvg):
        def aggregate_fit(self, server_round, results, failures):
            params, metrics = super().aggregate_fit(server_round, results, failures)
            if params is not None:
                aggregated_result["params"] = parameters_to_ndarrays(params)
            return params, metrics

    strategy = CaptureFedAvg(
        fraction_fit=1.0,
        fraction_evaluate=0.0,
        min_fit_clients=3,
        min_available_clients=3,
        initial_parameters=initial_params,
    )

    fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=3,
        config=fl.server.ServerConfig(num_rounds=1),
        strategy=strategy,
        ray_init_args={"runtime_env": {"env_vars": {"PYTHONPATH": f"{root_dir}:{core_dir}:{os.environ.get('PYTHONPATH', '')}"}}},
    )

    assert "params" in aggregated_result, "Aggregation did not produce parameters"
    result = aggregated_result["params"][0]

    w1 = np.array([1.0, 2.0, 3.0, 4.0])
    w2 = np.array([2.0, 3.0, 4.0, 5.0])
    w3 = np.array([3.0, 4.0, 5.0, 6.0])
    expected = (100 * w1 + 200 * w2 + 300 * w3) / 600

    np.testing.assert_allclose(result, expected, atol=1e-5,
        err_msg="FedAvg did not weight by sample count correctly")


def test_equal_weights_equals_simple_mean():
    """When all clients have the same sample count, FedAvg = simple mean."""
    configs = {
        "0": {"weights": [np.array([1.0, 2.0])], "samples": 100},
        "1": {"weights": [np.array([3.0, 4.0])], "samples": 100},
    }

    def client_fn(cid: str) -> fl.client.Client:
        cfg = configs[cid]
        return WeightedDummyClient(cid, cfg["weights"], cfg["samples"]).to_client()

    from flwr.server.strategy import FedAvg

    aggregated = {}

    class CaptureFedAvg(FedAvg):
        def aggregate_fit(self, server_round, results, failures):
            params, metrics = super().aggregate_fit(server_round, results, failures)
            if params is not None:
                aggregated["params"] = parameters_to_ndarrays(params)
            return params, metrics

    strategy = CaptureFedAvg(
        fraction_fit=1.0,
        fraction_evaluate=0.0,
        min_fit_clients=2,
        min_available_clients=2,
        initial_parameters=ndarrays_to_parameters([np.array([0.0, 0.0])]),
    )

    fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=2,
        config=fl.server.ServerConfig(num_rounds=1),
        strategy=strategy,
        ray_init_args={"runtime_env": {"env_vars": {"PYTHONPATH": f"{root_dir}:{core_dir}:{os.environ.get('PYTHONPATH', '')}"}}},
    )

    result = aggregated["params"][0]
    expected = np.array([2.0, 3.0])
    np.testing.assert_allclose(result, expected, atol=1e-5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
