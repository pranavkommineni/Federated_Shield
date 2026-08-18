from time import perf_counter
from secure_aggregation import (
    ModelUpdate,
    SecureAggregationClient,
    SecureAggregationProtocol,
)


def benchmark(count):
    start = perf_counter()

    org_ids = [f"org-{index}" for index in range(count)]
    clients = {org: SecureAggregationClient(org) for org in org_ids}
    public = {org: client.agreement_public_key for org, client in clients.items()}
    for client in clients.values():
        client.configure_peers(public)

    p = SecureAggregationProtocol("bench", "v1", 2)
    for org, client in clients.items():
        p.register_participant(org, client.verification_key)
    p.setup_masks()
    setup = perf_counter()

    for org in org_ids:
        index = int(org.split("-")[1])
        update = ModelUpdate(org, "bench", "v1", [float(index)] * 100)
        p.submit_masked_update(clients[org].mask_update(update))
    masked = perf_counter()

    p.complete()
    end = perf_counter()

    return {
        "participants": count,
        "setup_seconds": setup - start,
        "masking_seconds": masked - setup,
        "aggregation_seconds": end - masked,
        "total_seconds": end - start,
    }


if __name__ == "__main__":
    for count in (3, 5, 10):
        print(benchmark(count))
