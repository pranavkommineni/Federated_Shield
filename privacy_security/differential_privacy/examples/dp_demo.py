"""
Privacy-Security/differential_privacy/examples/dp_demo.py

Runs the full Team-B pipeline end to end, on your own terminal:

    Secure Aggregation  ->  Differential Privacy  ->  (epsilon/delta report)

This is the actual integration point: SecureAggregationProtocol.complete()
returns an AggregationResult, and that AggregationResult is fed directly
into GaussianDP.apply() -- nothing in between, no HTTP hop, matching
README.md's "SECURE AGGREGATION -> DIFFERENTIAL PRIVACY" arrow.

Run it with:
    python Privacy-Security/differential_privacy/examples/dp_demo.py
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from secure_aggregation import (
    ModelUpdate,
    SecureAggregationClient,
    SecureAggregationProtocol,
)
from differential_privacy import GaussianDP


def run():
    # --- Step 1: Secure Aggregation (same setup as secure_aggregation/examples/basic_demo.py) ---
    orgs = ("Organization A", "Organization B", "Organization C")
    clients = {org: SecureAggregationClient(org) for org in orgs}
    public_keys = {org: client.agreement_public_key for org, client in clients.items()}
    for client in clients.values():
        client.configure_peers(public_keys)

    round_id, model_version, threshold = "round-1", "v1", 2
    protocol = SecureAggregationProtocol(round_id, model_version, threshold)
    for org, client in clients.items():
        protocol.register_participant(org, client.verification_key)
    protocol.setup_masks()

    # Each org's local (already-per-client-clipped, in a real deployment)
    # model update vector.
    org_updates = {
        "Organization A": [2.0, 3.0],
        "Organization B": [4.0, 5.0],
        "Organization C": [1.0, 2.0],
    }
    for org, vector in org_updates.items():
        update = ModelUpdate(org, round_id, model_version, vector)
        protocol.submit_masked_update(clients[org].mask_update(update))

    aggregation_result = protocol.complete()
    print("Secure Aggregation result (server only ever saw masked vectors):")
    print("  raw aggregate:", aggregation_result.aggregate_update.tolist())

    # --- Step 2: Differential Privacy, straight off the AggregationResult ---
    dp = GaussianDP(clip_norm=1.0, noise_multiplier=1.1, delta=1e-5)
    dp_result = dp.apply(
        aggregation_result,
        round_number=1,
        num_clients=len(aggregation_result.contributors),
    )

    print("\nDifferential Privacy result:")
    print("  private update      :", dp_result["private_update"].tolist())
    print("  epsilon this round   :", round(dp_result["epsilon_spent_this_round"], 4))
    print("  cumulative epsilon   :", round(dp_result["cumulative_epsilon"], 4))
    print("  delta                :", dp_result["delta"])


if __name__ == "__main__":
    run()
