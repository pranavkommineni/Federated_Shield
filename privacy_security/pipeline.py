"""
final_project/pipeline.py

Final integrated Private-FL pipeline:

    Private Data -> Local Training -> Model Update -> Validation ->
    Update Clipping -> Secure Aggregation -> Differential Privacy ->
    Protected Update -> Flower Server -> Global Model

Stitches together the two prototypes you uploaded:
  - secure_aggregation/  (pairwise-masking secure aggregation)
  - differential_privacy/ (central Gaussian DP + epsilon accounting)

and wraps them in the two stages that were missing to close the loop:
  - client-side local training + per-client update clipping
    (the "per-client clipping" step that differential_privacy/noise.py's
    own docstring flags as required for the sigma math to be a real
    DP-FedAvg guarantee)
  - a Flower (flwr) server strategy that consumes the already-clipped,
    securely-aggregated, DP-noised vector and turns it into the new
    global model.

Run directly:
    python pipeline.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from secure_aggregation import (
    ModelUpdate,
    SecureAggregationClient,
    SecureAggregationProtocol,
)
from secure_aggregation.exceptions import InvalidUpdateError
from differential_privacy import GaussianDP

import flwr as fl
from flwr.server.strategy import Strategy
from flwr.server.client_proxy import ClientProxy
from flwr.common import (
    FitRes,
    Parameters,
    ndarrays_to_parameters,
    parameters_to_ndarrays,
)


# --------------------------------------------------------------------------
# Stage 1: Private Data  &  Stage 2: Local Training
# --------------------------------------------------------------------------

@dataclass
class LocalDataset:
    """Stand-in for a participant's private, never-shared local data."""
    x: np.ndarray
    y: np.ndarray


def make_private_data(org: str, dim: int, n_samples: int, seed: int) -> LocalDataset:
    """Simulates each organization's private local dataset (never leaves the client)."""
    rng = np.random.default_rng(seed)
    true_w = np.linspace(0.5, 1.5, dim)
    x = rng.normal(size=(n_samples, dim))
    y = x @ true_w + rng.normal(scale=0.1, size=n_samples)
    return LocalDataset(x, y)


def local_training(global_weights: np.ndarray, data: LocalDataset, lr: float = 0.05,
                    epochs: int = 20) -> np.ndarray:
    """
    Trains a local linear model starting from the current global weights and
    returns the *update* (delta), i.e. what secure aggregation will protect.
    Private data (data.x, data.y) never leaves this function.
    """
    w = global_weights.copy()
    n = data.x.shape[0]
    for _ in range(epochs):
        preds = data.x @ w
        grad = data.x.T @ (preds - data.y) / n
        w -= lr * grad
    return w - global_weights  # the model update


# --------------------------------------------------------------------------
# Stage 3: Model Update wrapper -> Stage 4: Validation -> Stage 5: Update Clipping
# --------------------------------------------------------------------------

def validate_update(update_vector: np.ndarray, expected_dim: int) -> None:
    """Sanity/schema validation before anything touches the network."""
    v = np.asarray(update_vector, dtype=np.float64)
    if v.ndim != 1 or v.size != expected_dim:
        raise InvalidUpdateError(f"expected a flat vector of size {expected_dim}")
    if not np.isfinite(v).all():
        raise InvalidUpdateError("update contains NaN/Inf values")


def clip_update(update_vector: np.ndarray, clip_norm: float) -> np.ndarray:
    """
    Per-client L2-norm clipping, applied BEFORE secure aggregation.
    This is the piece differential_privacy/noise.py explicitly calls out as
    a prerequisite: GaussianDP's sigma = noise_multiplier * clip_norm / num_clients
    only gives a real per-round DP-FedAvg guarantee if each client already
    clipped locally, so a single large contributor can't dominate the sum.
    """
    v = np.asarray(update_vector, dtype=np.float64)
    norm = np.linalg.norm(v)
    scale = min(1.0, clip_norm / (norm + 1e-12))
    return v * scale


# --------------------------------------------------------------------------
# Stage 6: Secure Aggregation
# --------------------------------------------------------------------------

def run_secure_aggregation(round_id: str, model_version: str, threshold: int,
                            clipped_updates: Dict[str, np.ndarray]):
    """
    Runs the full pairwise-masking secure-aggregation protocol over the
    already-validated, already-clipped per-org update vectors. The server
    (SecureAggregationProtocol/SecureAggregator) only ever sees masked
    ciphertext-like vectors, never a raw per-org update.
    """
    orgs = list(clipped_updates.keys())
    clients = {org: SecureAggregationClient(org) for org in orgs}
    public_keys = {org: c.agreement_public_key for org, c in clients.items()}
    for c in clients.values():
        c.configure_peers(public_keys)

    protocol = SecureAggregationProtocol(round_id, model_version, threshold)
    for org, c in clients.items():
        protocol.register_participant(org, c.verification_key)
    protocol.setup_masks()

    for org, vector in clipped_updates.items():
        update = ModelUpdate(org, round_id, model_version, vector)
        masked = clients[org].mask_update(update)
        protocol.submit_masked_update(masked)

    return protocol.complete()  # -> AggregationResult (server sees only the sum)


# --------------------------------------------------------------------------
# Stage 7: Differential Privacy -> Stage 8: Protected Update
# --------------------------------------------------------------------------

def apply_differential_privacy(aggregation_result, round_number: int,
                                clip_norm: float, noise_multiplier: float,
                                delta: float) -> dict:
    """
    Central DP on top of the secure-aggregation sum: re-clips the (already
    per-client-clipped) aggregate for defense in depth, adds calibrated
    Gaussian noise, and tracks the (epsilon, delta) privacy budget spent.
    Output ("private_update") is the Protected Update that leaves this
    trust boundary and is the only thing the Flower server ever sees.
    """
    dp = GaussianDP(clip_norm=clip_norm, noise_multiplier=noise_multiplier, delta=delta)
    num_clients = len(aggregation_result.contributors)
    return dp.apply(aggregation_result, round_number=round_number, num_clients=num_clients)


# --------------------------------------------------------------------------
# Stage 9: Flower Server -> Stage 10: Global Model
# --------------------------------------------------------------------------

class ProtectedUpdateStrategy(Strategy):
    """
    A minimal flwr Strategy that does NOT run flwr's own aggregation.
    Real per-client fit() results never reach this class in plaintext --
    by the time Flower is involved, the round has already gone through
    local_training -> validate_update -> clip_update -> secure aggregation
    -> differential privacy upstream. This strategy's job is only to fold
    the resulting Protected Update into Flower's global-model bookkeeping,
    so the rest of a normal flwr deployment (client selection, historical
    metrics, checkpointing) works unmodified.
    """

    def __init__(self, initial_weights: np.ndarray):
        super().__init__()
        self.global_weights = initial_weights.copy()

    def initialize_parameters(self, client_manager):
        return ndarrays_to_parameters([self.global_weights])

    def apply_protected_update(self, protected_update: np.ndarray) -> np.ndarray:
        """Global model = global model + protected (clipped, DP-noised) update."""
        self.global_weights = self.global_weights + protected_update
        return self.global_weights

    # Required Strategy overrides for a fully-conformant flwr server;
    # unused because aggregation already happened upstream of Flower.
    def configure_fit(self, server_round, parameters, client_manager):
        return []

    def aggregate_fit(self, server_round, results: List[tuple], failures):
        return ndarrays_to_parameters([self.global_weights]), {}

    def configure_evaluate(self, server_round, parameters, client_manager):
        return []

    def aggregate_evaluate(self, server_round, results, failures):
        return None, {}

    def evaluate(self, server_round, parameters):
        return None


# --------------------------------------------------------------------------
# End-to-end run
# --------------------------------------------------------------------------

def run_pipeline(orgs=("Org-A", "Org-B", "Org-C"), dim=4, round_number=1,
                  per_client_clip_norm=1.0, agg_clip_norm=1.0,
                  noise_multiplier=1.1, delta=1e-5, threshold=2, seed=0):
    round_id, model_version = f"round-{round_number}", "v1"
    global_model = ProtectedUpdateStrategy(np.zeros(dim))

    print("=" * 70)
    print(f"ROUND {round_number}")
    print("=" * 70)

    # 1-2: Private Data + Local Training
    clipped_updates: Dict[str, np.ndarray] = {}
    for i, org in enumerate(orgs):
        data = make_private_data(org, dim, n_samples=200, seed=seed + i)
        raw_update = local_training(global_model.global_weights, data)

        # 4: Validation
        validate_update(raw_update, dim)

        # 5: Update Clipping (per-client, pre-secure-aggregation)
        clipped = clip_update(raw_update, per_client_clip_norm)
        clipped_updates[org] = clipped
        print(f"[{org}] raw update norm={np.linalg.norm(raw_update):.3f} "
              f"-> clipped norm={np.linalg.norm(clipped):.3f}")

    # 6: Secure Aggregation
    agg_result = run_secure_aggregation(round_id, model_version, threshold, clipped_updates)
    print(f"\n[Secure Aggregation] server saw only masked vectors; "
          f"sum released = {agg_result.aggregate_update.tolist()}")
    print(f"[Secure Aggregation] contributors = {agg_result.contributors}")

    # 7-8: Differential Privacy -> Protected Update
    dp_result = apply_differential_privacy(
        agg_result, round_number=round_number, clip_norm=agg_clip_norm,
        noise_multiplier=noise_multiplier, delta=delta,
    )
    protected_update = dp_result["private_update"]
    print(f"\n[Differential Privacy] protected update = {protected_update.tolist()}")
    print(f"[Differential Privacy] epsilon this round = {dp_result['epsilon_spent_this_round']:.4f}, "
          f"cumulative epsilon = {dp_result['cumulative_epsilon']:.4f}, delta = {dp_result['delta']}")

    # 9-10: Flower Server -> Global Model
    new_global = global_model.apply_protected_update(protected_update)
    print(f"\n[Flower Server] global model updated -> {new_global.tolist()}")
    return new_global, dp_result


if __name__ == "__main__":
    weights, dp_info = run_pipeline()
    print("\n" + "=" * 70)
    print("FINAL GLOBAL MODEL:", weights.tolist())
    print("PRIVACY SPENT: epsilon =", round(dp_info["cumulative_epsilon"], 4),
          " delta =", dp_info["delta"])
