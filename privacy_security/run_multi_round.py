"""
final_project/run_multi_round.py

Runs the integrated pipeline (pipeline.run_pipeline) for several federated
rounds in a row, feeding each round's resulting global model into the next
round's local training, and stops early if the privacy budget is exhausted.

    python run_multi_round.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from pipeline import (
    ProtectedUpdateStrategy,
    apply_differential_privacy,
    clip_update,
    local_training,
    make_private_data,
    run_secure_aggregation,
    validate_update,
)
from differential_privacy import PrivacyAccountant

DP_TARGET_EPSILON = 8.0  # stop training once cumulative epsilon would exceed this


def run(num_rounds=3, orgs=("Org-A", "Org-B", "Org-C"), dim=4,
        per_client_clip_norm=1.0, agg_clip_norm=1.0, noise_multiplier=1.1,
        delta=1e-5, threshold=2):
    global_model = ProtectedUpdateStrategy(np.zeros(dim))
    accountant = PrivacyAccountant(delta=delta)

    for round_number in range(1, num_rounds + 1):
        round_id, model_version = f"round-{round_number}", "v1"
        print(f"\n{'#'*70}\n# ROUND {round_number}\n{'#'*70}")

        clipped_updates = {}
        for i, org in enumerate(orgs):
            data = make_private_data(org, dim, n_samples=200, seed=round_number * 100 + i)
            raw_update = local_training(global_model.global_weights, data)
            validate_update(raw_update, dim)
            clipped_updates[org] = clip_update(raw_update, per_client_clip_norm)

        agg_result = run_secure_aggregation(round_id, model_version, threshold, clipped_updates)
        dp_result = apply_differential_privacy(
            agg_result, round_number=round_number, clip_norm=agg_clip_norm,
            noise_multiplier=noise_multiplier, delta=delta,
        )

        projected = accountant.accumulate(round_number, dp_result["epsilon_spent_this_round"])
        if projected >= DP_TARGET_EPSILON:
            print(f"Stopping: cumulative epsilon {projected:.4f} would exceed "
                  f"budget {DP_TARGET_EPSILON}.")
            break

        global_model.apply_protected_update(dp_result["private_update"])
        print(f"global model  = {global_model.global_weights.tolist()}")
        print(f"epsilon round = {dp_result['epsilon_spent_this_round']:.4f}   "
              f"cumulative    = {dp_result['cumulative_epsilon']:.4f}")

    print(f"\nFINAL GLOBAL MODEL after available rounds: {global_model.global_weights.tolist()}")
    print(f"Total epsilon spent: {accountant.spent_so_far():.4f} (delta={delta})")
    return global_model.global_weights


if __name__ == "__main__":
    run()
