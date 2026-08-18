"""
Privacy-Security/differential_privacy/noise.py

Central Differential Privacy: clips and adds calibrated Gaussian noise to
the output of Secure Aggregation, per README.md's pipeline
(Secure Aggregation -> Differential Privacy -> Global Model Store).

WHY THIS ISN'T A LINE-FOR-LINE COPY OF THE PASTED SNIPPET
------------------------------------------------------------
The version you pasted operates on `Dict[str, torch.Tensor]`. This repo
has no torch dependency (see requirements.txt: numpy, pytest,
cryptography, pycryptodome) and `SecureAggregator.aggregate()` -- the
actual upstream call in aggregation/aggregator.py -- returns an
`AggregationResult` whose `aggregate_update` field is a single flat
`numpy.ndarray` (a masked-and-summed vector, not an average, and not a
dict of named layers -- see models/result.py).

The logic is otherwise identical: clip the global L2 norm, add
N(0, sigma^2) noise with sigma = noise_multiplier * clip_norm /
num_clients, and account epsilon/delta through PrivacyAccountant.

IMPORTANT PRIVACY CAVEAT (carried over honestly, not silently fixed)
-----------------------------------------------------------------------
SecureAggregator.aggregate() returns a *sum* of per-participant masked
updates, not an average. The sensitivity math baked into `add_noise`
(sigma shrinks with num_clients) assumes you're privatizing an *average*
of per-client-clipped updates -- the standard DP-FedAvg construction,
where each client independently clips to `clip_norm` before submission
and the server divides by num_clients. If per-client clipping isn't
already happening before secure aggregation (e.g. in each org's
training_node), then clipping the *summed* aggregate here to
`clip_norm` is a different (weaker) guarantee than DP-FedAvg's, because
a single large contributor can still dominate the sum before this
global clip is applied. Flag this to Team A / whoever owns per-client
clipping in team-a-ai-core/training_node before relying on the ε
reported here as a real per-round guarantee.
"""

from __future__ import annotations

import numpy as np

from .accountant import PrivacyAccountant

try:  # only used for a nicer type hint / duck-typed input support
    from ..secure_aggregation.models import AggregationResult
except ImportError:  # pragma: no cover - keeps this module importable standalone
    AggregationResult = None  # type: ignore[assignment]


class GaussianDP:
    def __init__(self, clip_norm: float = 1.0, noise_multiplier: float = 1.1,
                 delta: float = 1e-5):
        self.clip_norm = clip_norm
        self.noise_multiplier = noise_multiplier
        self.delta = delta
        self.accountant = PrivacyAccountant(delta=delta)

    def clip(self, update: np.ndarray) -> np.ndarray:
        """Clip the aggregated update's global L2 norm to self.clip_norm."""
        vector = np.asarray(update, dtype=np.float64)
        norm = np.linalg.norm(vector)
        scale = min(1.0, self.clip_norm / (norm + 1e-12))
        return vector * scale

    def add_noise(self, update: np.ndarray, num_clients: int) -> np.ndarray:
        """Add Gaussian noise calibrated to sensitivity / num_clients."""
        if num_clients <= 0:
            raise ValueError("num_clients must be > 0")
        sigma = (self.noise_multiplier * self.clip_norm) / num_clients
        noise = np.random.normal(loc=0.0, scale=sigma, size=update.shape)
        return update + noise

    def apply(self, aggregated_update, round_number: int, num_clients: int) -> dict:
        """
        aggregated_update: either the raw numpy vector coming out of
        SecureAggregator.aggregate().aggregate_update, or an
        AggregationResult itself (this method will pull .aggregate_update
        off it automatically).
        """
        vector = getattr(aggregated_update, "aggregate_update", aggregated_update)

        clipped = self.clip(vector)
        private_update = self.add_noise(clipped, num_clients)

        eps_round = self.accountant.compute_round_epsilon(
            noise_multiplier=self.noise_multiplier, num_clients=num_clients
        )
        cumulative_eps = self.accountant.accumulate(round_number, eps_round)

        return {
            "private_update": private_update,
            "epsilon_spent_this_round": eps_round,
            "cumulative_epsilon": cumulative_eps,
            "delta": self.delta,
        }
