"""Integration test for single-GPU multi-org FL simulation."""
import os
import sys
import pytest

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from fl.simulation import run_fl_simulation

def test_mock_fl_simulation():
    """Verify mock LLM simulation runs end-to-end for 2 rounds across 2 org clients."""
    history = run_fl_simulation(
        num_rounds=2,
        num_clients=2,
        use_secure_agg=False,
        model_type="qwen",
        mock_model=True,
        local_epochs=1,
    )
    assert history is not None
    assert len(history.losses_distributed) == 2


def test_mock_secure_fl_simulation():
    """Verify mock secure aggregation FL simulation runs end-to-end."""
    history = run_fl_simulation(
        num_rounds=2,
        num_clients=2,
        use_secure_agg=True,
        model_type="qwen",
        mock_model=True,
        local_epochs=1,
    )
    assert history is not None
    assert len(history.losses_distributed) == 2
