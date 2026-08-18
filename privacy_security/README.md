# Final Integrated Private-FL Pipeline

Implements the full pipeline:

```
Private Data → Local Training → Model Update → Validation →
Update Clipping → Secure Aggregation → Differential Privacy →
Protected Update → Flower Server → Global Model
```

## Contents
- `secure_aggregation/` — your uploaded pairwise-masking secure aggregation package (unchanged).
- `differential_privacy/` — your uploaded central Gaussian-DP + epsilon accountant package (unchanged).
- `pipeline.py` — **the integration layer.** Adds the two missing stages
  (local training with per-client update clipping, and a Flower server
  strategy) and wires every stage together end to end for one round.
- `run_multi_round.py` — runs the pipeline across several FL rounds,
  tracking cumulative epsilon and stopping before the privacy budget
  (`DP_TARGET_EPSILON`) is exceeded.

## Run it
```bash
pip install -r secure_aggregation/requirements.txt
pip install flwr
python pipeline.py           # single round, verbose stage-by-stage output
python run_multi_round.py    # multiple rounds with a privacy budget
```

## Stage-by-stage mapping

| Diagram stage | Implemented by |
|---|---|
| Private Data | `make_private_data()` — synthetic per-org dataset, never leaves the client function |
| Local Training | `local_training()` — local gradient steps from current global weights, returns a delta |
| Model Update | `secure_aggregation.ModelUpdate` dataclass |
| Validation | `validate_update()` — shape/finite checks (mirrors `validation/update_validator.py`) |
| Update Clipping | `clip_update()` — **per-client** L2 clip, done before masking |
| Secure Aggregation | `run_secure_aggregation()` — pairwise masking via `SecureAggregationClient` + `SecureAggregationProtocol`; the server only ever reconstructs the sum |
| Differential Privacy | `apply_differential_privacy()` — `GaussianDP.apply()`: re-clips the aggregate, adds `N(0, σ²)` noise, tracks (ε, δ) via `PrivacyAccountant` |
| Protected Update | the `private_update` array returned by `GaussianDP.apply()` |
| Flower Server | `ProtectedUpdateStrategy(flwr.server.strategy.Strategy)` — a real `flwr` `Strategy` subclass; folds the protected update into Flower's parameter bookkeeping so a normal `flwr` deployment (client manager, `start_server`, checkpointing) works around it unmodified |
| Global Model | `ProtectedUpdateStrategy.global_weights` after `apply_protected_update()` |

## Important caveat carried over from the DP module
`differential_privacy/noise.py`'s own docstring flags that its noise
calibration (`sigma = noise_multiplier * clip_norm / num_clients`) assumes
**per-client clipping happens before aggregation** — that's exactly why
`clip_update()` is applied to each org's raw update *before* it's masked
and submitted to secure aggregation, not just once on the aggregate
afterward. The DP module's own re-clip after secure aggregation is kept
as defense in depth, per the original module's design.

## Privacy budget
`run_multi_round.py` uses `PrivacyAccountant` (basic/additive composition)
to track cumulative epsilon and halts training once continuing would
exceed `DP_TARGET_EPSILON`. Swap in a tighter RDP/moments accountant for
long-running jobs, as noted in `differential_privacy/accountant.py`.
