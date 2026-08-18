import numpy as np
import pytest
from differential_privacy import GaussianDP, PrivacyAccountant


def test_clip_shrinks_large_vector_to_clip_norm():
    dp = GaussianDP(clip_norm=1.0, noise_multiplier=1.1, delta=1e-5)
    clipped = dp.clip(np.array([10.0, 20.0, 5.0]))
    assert np.linalg.norm(clipped) == pytest.approx(1.0, abs=1e-9)


def test_clip_leaves_small_vector_unchanged():
    dp = GaussianDP(clip_norm=5.0, noise_multiplier=1.1, delta=1e-5)
    vector = np.array([1.0, 1.0])
    np.testing.assert_allclose(dp.clip(vector), vector)


def test_add_noise_changes_values_but_keeps_shape():
    dp = GaussianDP(clip_norm=1.0, noise_multiplier=1.1, delta=1e-5)
    vector = np.zeros(5)
    noised = dp.add_noise(vector, num_clients=10)
    assert noised.shape == vector.shape
    assert not np.allclose(noised, vector)


def test_add_noise_rejects_zero_clients():
    dp = GaussianDP()
    with pytest.raises(ValueError):
        dp.add_noise(np.zeros(3), num_clients=0)


def test_apply_accepts_raw_vector():
    dp = GaussianDP(clip_norm=1.0, noise_multiplier=1.1, delta=1e-5)
    result = dp.apply(np.array([3.0, 4.0]), round_number=1, num_clients=5)
    assert result["private_update"].shape == (2,)
    assert result["delta"] == 1e-5
    assert result["epsilon_spent_this_round"] > 0


def test_apply_accepts_aggregation_result_via_duck_typing():
    class FakeAggregationResult:
        aggregate_update = np.array([1.0, 2.0, 3.0])
        contributors = ("org_a", "org_b")

    dp = GaussianDP(clip_norm=1.0, noise_multiplier=1.1, delta=1e-5)
    result = dp.apply(FakeAggregationResult(), round_number=1, num_clients=2)
    assert result["private_update"].shape == (3,)


def test_cumulative_epsilon_composes_additively_across_rounds():
    dp = GaussianDP(clip_norm=1.0, noise_multiplier=1.1, delta=1e-5)
    r1 = dp.apply(np.array([1.0, 1.0]), round_number=1, num_clients=5)
    r2 = dp.apply(np.array([1.0, 1.0]), round_number=2, num_clients=5)
    assert r2["cumulative_epsilon"] == pytest.approx(
        r1["epsilon_spent_this_round"] + r2["epsilon_spent_this_round"]
    )


def test_reapplying_same_round_number_does_not_double_count():
    dp = GaussianDP(clip_norm=1.0, noise_multiplier=1.1, delta=1e-5)
    dp.apply(np.array([1.0, 1.0]), round_number=1, num_clients=5)
    dp.apply(np.array([1.0, 1.0]), round_number=2, num_clients=5)
    total_before = dp.accountant.spent_so_far()
    dp.apply(np.array([1.0, 1.0]), round_number=1, num_clients=5)  # re-run round 1
    assert dp.accountant.spent_so_far() == pytest.approx(total_before)


def test_accountant_budget_helpers():
    accountant = PrivacyAccountant(delta=1e-5)
    eps = accountant.compute_round_epsilon(noise_multiplier=1.1, num_clients=5)
    accountant.accumulate(round_number=1, eps_round=eps)
    assert accountant.remaining_budget(target_epsilon=eps + 1.0) == pytest.approx(1.0)
    assert not accountant.budget_exhausted(target_epsilon=eps + 1.0)
    assert accountant.budget_exhausted(target_epsilon=eps)


def test_default_noise_multiplier_exceeds_readme_target_epsilon_in_one_round():
    """
    Documents a real gap, not a bug: with noise_multiplier=1.1, delta=1e-5
    (this repo's defaults) and *basic* composition, a single round's
    epsilon already exceeds README.md's DP_TARGET_EPSILON=3.0 budget for
    the whole training lifetime. That's expected for basic composition
    over many rounds -- it's a strong hint that a tighter accountant
    (RDP / moments accountant) is needed before running real multi-round
    training against that target, not that this accountant is broken.
    """
    accountant = PrivacyAccountant(delta=1e-5)
    eps_round = accountant.compute_round_epsilon(noise_multiplier=1.1, num_clients=5)
    assert eps_round > 3.0
