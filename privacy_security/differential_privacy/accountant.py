"""
Privacy-Security/differential_privacy/accountant.py

Tracks the (epsilon, delta) privacy budget spent by GaussianDP across
federated learning rounds.

NOTE ON THIS IMPLEMENTATION
----------------------------
This wasn't included in the code you pasted, so this is a from-scratch
implementation, not something extracted from an existing file. It uses:

  - Per-round epsilon: the standard analytic Gaussian-mechanism bound,
        eps = sqrt(2 * ln(1.25 / delta)) / noise_multiplier
    which holds whenever sigma >= sqrt(2 ln(1.25/delta))/eps * sensitivity
    (Dwork & Roth, "The Algorithmic Foundations of Differential Privacy").

  - Cross-round composition: basic (additive) composition -- cumulative
    epsilon is the running sum of per-round epsilons.

Basic composition is correct but NOT tight. If/when you need a tighter
bound for a long-running training job (e.g. 50+ rounds against
DP_TARGET_EPSILON = 3.0 from the README config table), swap the
composition step for an RDP / moments-accountant implementation
(e.g. via the `opacus` or `dp-accounting` libraries) -- the public
interface below (`compute_round_epsilon`, `accumulate`) is written so
that swap doesn't require touching noise.py.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class PrivacyAccountant:
    delta: float = 1e-5
    _history: dict[int, float] = field(default_factory=dict, repr=False)
    _running_total: float = field(default=0.0, repr=False)

    def compute_round_epsilon(self, noise_multiplier: float, num_clients: int) -> float:
        """
        Epsilon spent by a single application of the Gaussian mechanism
        with the given noise multiplier, for the fixed self.delta.

        num_clients isn't used in this bound directly (it already shaped
        the noise via sigma = noise_multiplier * clip_norm / num_clients
        in GaussianDP.add_noise); it's accepted here to keep the same
        call signature your pipeline already expects, and so a future
        per-client-sampling-rate accountant can use it without an API
        change.
        """
        if noise_multiplier <= 0:
            raise ValueError("noise_multiplier must be > 0")
        if not (0 < self.delta < 1):
            raise ValueError("delta must be in (0, 1)")
        return math.sqrt(2 * math.log(1.25 / self.delta)) / noise_multiplier

    def accumulate(self, round_number: int, eps_round: float) -> float:
        """
        Adds this round's epsilon to the running total (basic composition)
        and records it, so repeated calls for the same round_number don't
        double count -- re-applying a round overwrites its prior entry.
        """
        self._running_total -= self._history.get(round_number, 0.0)
        self._history[round_number] = eps_round
        self._running_total += eps_round
        return self._running_total

    def spent_so_far(self) -> float:
        """Cumulative epsilon across every round recorded so far."""
        return self._running_total

    def remaining_budget(self, target_epsilon: float) -> float:
        """Convenience for the README's DP_TARGET_EPSILON budget check."""
        return target_epsilon - self._running_total

    def budget_exhausted(self, target_epsilon: float) -> bool:
        return self._running_total >= target_epsilon
