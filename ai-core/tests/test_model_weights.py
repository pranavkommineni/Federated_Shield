"""
Real Model Weight Tests.

Verifies that:
1. flatten_weights / unflatten_weights roundtrip preserves values
2. get_parameters / set_parameters roundtrip preserves model state
3. FederixNet produces the expected number of parameters
"""
import os
import sys
import numpy as np
import torch
import pytest

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from model.federix_model import create_model, FederixNet
from model.serialization import (
    get_parameters,
    set_parameters,
    flatten_weights,
    unflatten_weights,
    get_parameter_shapes,
)


def test_model_creation():
    """FederixNet instantiates and produces logits of correct shape."""
    model = create_model()
    assert isinstance(model, FederixNet)

    x = torch.randn(4, 3, 32, 32)
    out = model(x)
    assert out.shape == (4, 10), f"Expected (4, 10), got {out.shape}"


def test_get_set_parameters_roundtrip():
    """get_parameters -> set_parameters preserves model weights exactly."""
    model1 = create_model()
    model2 = create_model()

    params1 = get_parameters(model1)

    set_parameters(model2, params1)
    params2 = get_parameters(model2)

    for p1, p2 in zip(params1, params2):
        np.testing.assert_array_equal(p1, p2)


def test_flatten_unflatten_roundtrip():
    """flatten -> unflatten preserves shapes and values."""
    model = create_model()
    params = get_parameters(model)
    shapes = get_parameter_shapes(model)

    flat = flatten_weights(params)
    assert flat.ndim == 1
    assert flat.dtype == np.float64

    total_elements = sum(np.prod(s) for s in shapes)
    assert flat.shape[0] == total_elements

    restored = unflatten_weights(flat, shapes)
    assert len(restored) == len(params)
    for original, recovered in zip(params, restored):
        np.testing.assert_allclose(recovered, original, atol=1e-7)


def test_flatten_unflatten_preserves_through_model():
    """Full cycle: model -> get -> flatten -> unflatten -> set -> get -> compare."""
    model = create_model()
    original_params = get_parameters(model)
    shapes = get_parameter_shapes(model)

    flat = flatten_weights(original_params)
    reconstructed = unflatten_weights(flat, shapes)
    set_parameters(model, reconstructed)
    final_params = get_parameters(model)

    for orig, final in zip(original_params, final_params):
        np.testing.assert_allclose(final, orig, atol=1e-7)


def test_parameter_count():
    """FederixNet should have approximately expected parameter count."""
    model = create_model()
    total = sum(p.numel() for p in model.parameters())
    assert total > 1000, f"Model too small: {total} parameters"
    assert total < 500_000, f"Model too large: {total} parameters"


def test_weights_change_after_training():
    """Verify that a single training step actually changes the model weights."""
    model = create_model()
    params_before = [p.copy() for p in get_parameters(model)]

    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    criterion = torch.nn.CrossEntropyLoss()

    x = torch.randn(8, 3, 32, 32)
    y = torch.randint(0, 10, (8,))

    model.train()
    optimizer.zero_grad()
    loss = criterion(model(x), y)
    loss.backward()
    optimizer.step()

    params_after = get_parameters(model)

    any_changed = any(
        not np.array_equal(before, after)
        for before, after in zip(params_before, params_after)
    )
    assert any_changed, "No parameters changed after training step"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
