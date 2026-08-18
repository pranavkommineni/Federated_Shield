# Secure Aggregation

This module is Team 2 Member 1's boundary between local model-update production and the aggregate update supplied to the Differential Privacy module. It never trains a model, performs FedAvg, exposes an API, or applies Differential Privacy.

## Round flow

Organizations register public verification keys with the server. Each `SecureAggregationClient` owns its plaintext `ModelUpdate` and private X25519/Ed25519 keys, produces a signed `MaskedUpdate`, and submits that protected value to the server. Pairwise masks derive from client-only X25519 agreements; the server has no mask manager or client private keys.

`ModelUpdate -> SecureAggregationProtocol -> AggregationResult.aggregate_update`

The state machine is `INITIALIZED -> PARTICIPANTS_REGISTERED -> KEY_SETUP -> MASK_SETUP -> COLLECTING_UPDATES -> DROPOUT_CHECK -> MASK_RECONSTRUCTION -> AGGREGATION -> COMPLETED`; failures become `FAILED`.

## Dropout and threshold

The detector compares registered and received participants. A round fails safely below its threshold. Above threshold, the prototype's trusted recovery boundary calculates an aggregate correction for masks involving missing clients. This models the place where a production protocol uses encrypted, threshold-reconstructable secret shares.

## Public API

```python
from secure_aggregation import ModelUpdate, SecureAggregationProtocol

protocol = SecureAggregationProtocol('round-1', 'v1', threshold=2)
for participant in ('Organization A', 'Organization B', 'Organization C'):
    protocol.register_participant(participant)
protocol.setup_masks()
protocol.submit(ModelUpdate('Organization A', 'round-1', 'v1', [2, 3]))
protocol.submit(ModelUpdate('Organization B', 'round-1', 'v1', [4, 5]))
result = protocol.complete()
```

Team 1 creates `ModelUpdate`. Team 2 Member 2 consumes `result.aggregate_update`. Team 3 can call `SecureAggregationProtocol` from its future transport layer without this package depending on FastAPI.

## Tests, demos, benchmark

Install `requirements.txt`, then run from the parent directory:

```bash
PYTHONPATH=. python -m pytest -q secure_aggregation/tests
PYTHONPATH=. python secure_aggregation/examples/basic_demo.py
PYTHONPATH=. python secure_aggregation/examples/dropout_demo.py
PYTHONPATH=. python secure_aggregation/scripts/run_benchmark.py
```

The tests cover model validation, protected input behavior, pairwise cancellation through aggregation, duplicate submission, threshold failure, and dropout recovery. The benchmark prints actual setup, masking, aggregation, and total elapsed times for 3, 5, and 10 organizations.

## Security assumptions and limitations

The goal is protection against a curious server that receives signed protected vectors. Client-side X25519 derives pairwise keys, Ed25519 authenticates submissions, and each submission has a cryptographically random replay-resistant identifier. Vectors use fixed-point encoding in a finite field; values must remain in the documented field range.

This is a prototype, not production cryptography. It does not include authenticated ECDH key exchange, encrypted share distribution, verifiable secret sharing, malicious-client defenses, finite-field quantization, persistent replay protection, or a formal security audit. A server colluding with the trusted recovery service can undermine individual-update protection. Dropout recovery is limited to a threshold-satisfied round.
