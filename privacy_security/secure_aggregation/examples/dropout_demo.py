from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from secure_aggregation import (
    ModelUpdate,
    SecureAggregationClient,
    SecureAggregationProtocol,
)
from secure_aggregation.exceptions import DropoutRecoveryError


def run():
    orgs = ("Organization A", "Organization B", "Organization C", "Organization D")
    clients = {org: SecureAggregationClient(org) for org in orgs}
    public = {org: client.agreement_public_key for org, client in clients.items()}
    for client in clients.values():
        client.configure_peers(public)

    protocol = SecureAggregationProtocol("dropout-1", "v1", 2)
    for org, client in clients.items():
        protocol.register_participant(org, client.verification_key)
    protocol.setup_masks()

    # Organization C drops out here: it never submits a masked update.
    for org, data in [
        ("Organization A", [2, 3]),
        ("Organization B", [4, 5]),
        ("Organization D", [1, 2]),
    ]:
        protocol.submit_masked_update(
            clients[org].mask_update(ModelUpdate(org, "dropout-1", "v1", data))
        )

    try:
        result = protocol.complete()
        print("Recovered aggregate:", result.aggregate_update.tolist())
        print("Missing:", sorted(result.dropout_information.missing))
    except DropoutRecoveryError as error:
        # Dropout is *detected* correctly, but the aggregator does not yet
        # consume client-supplied recovery shares to reconstruct the missing
        # participant's mask - see SecureAggregator.aggregate() in
        # aggregation/aggregator.py. Recovery share generation already exists
        # client-side (SecureAggregationClient.recovery_shares /
        # receive_recovery_share), it's just never wired up server-side.
        print("Dropout was detected but could not be recovered:", error)
        info = protocol.aggregator.check_participants()
        print("Received:", sorted(info.received))
        print("Missing:", sorted(info.missing))


if __name__ == "__main__":
    run()
