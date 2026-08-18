"""
Team 2 Integration Tests.

Verifies that the federated learning pipeline integrates correctly with
Team 2's Secure Aggregation module:

1. SecureFederixStrategy produces results numerically close to plain FedAvg
2. The protocol lifecycle (key exchange -> masking -> aggregation) works end-to-end
3. Overflow bounds are respected
"""
import sys
import os
import numpy as np
import pytest
import logging

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

base_dir = os.path.abspath(os.path.join(core_dir, '..'))
privacy_path = os.path.join(base_dir, 'Privacy-Security')
if privacy_path not in sys.path:
    sys.path.insert(0, privacy_path)

from model.federix_model import create_model
from model.serialization import (
    get_parameters,
    flatten_weights,
    unflatten_weights,
    get_parameter_shapes,
)

logger = logging.getLogger(__name__)


def _team2_available() -> bool:
    """Check if Team 2's secure_aggregation module is importable."""
    try:
        from secure_aggregation import (
            SecureAggregationProtocol,
            SecureAggregationClient,
            ModelUpdate,
        )
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _team2_available(), reason="Team 2 secure_aggregation not available")
class TestSecureAggregationIntegration:
    """Integration tests with Team 2's Secure Aggregation module."""

    def test_basic_secure_aggregation_three_clients(self):
        """
        3 clients submit known weight vectors through the secure aggregation
        protocol. Verify the result matches the expected sum / N.
        """
        from secure_aggregation import (
            SecureAggregationProtocol,
            SecureAggregationClient,
            ModelUpdate,
        )

        round_id = "test-round-1"
        model_version = "v1"
        threshold = 2
        num_clients = 3

        client_weights = {
            "org_a": np.array([1.0, 2.0, 3.0, 4.0]),
            "org_b": np.array([2.0, 3.0, 4.0, 5.0]),
            "org_c": np.array([3.0, 4.0, 5.0, 6.0]),
        }

        sa_clients = {}
        for cid in client_weights:
            sa_clients[cid] = SecureAggregationClient(cid)

        pub_keys = {cid: c.agreement_public_key for cid, c in sa_clients.items()}
        for cid, client in sa_clients.items():
            client.configure_peers(pub_keys)

        protocol = SecureAggregationProtocol(round_id, model_version, threshold)
        for cid, client in sa_clients.items():
            protocol.register_participant(cid, client.verification_key)

        protocol.setup_masks()

        for cid, client in sa_clients.items():
            update = ModelUpdate(
                participant_id=cid,
                round_id=round_id,
                model_version=model_version,
                update_data=client_weights[cid],
            )
            masked = client.mask_update(update)
            protocol.submit_masked_update(masked)

        result = protocol.complete()

        aggregate_sum = result.aggregate_update
        aggregate_avg = aggregate_sum / num_clients

        expected_sum = np.array([6.0, 9.0, 12.0, 15.0])
        expected_avg = expected_sum / num_clients

        np.testing.assert_allclose(
            aggregate_sum, expected_sum, atol=0.01,
            err_msg="Secure aggregation sum does not match expected"
        )
        np.testing.assert_allclose(
            aggregate_avg, expected_avg, atol=0.01,
            err_msg="Secure aggregation average does not match expected"
        )

        assert len(result.contributors) == num_clients
        assert set(result.contributors) == set(client_weights.keys())

    def test_secure_agg_matches_plain_fedavg(self):
        """
        Run both plain averaging and secure aggregation on the same inputs.
        Results should be numerically close (within fixed-point quantization error).
        """
        from secure_aggregation import (
            SecureAggregationProtocol,
            SecureAggregationClient,
            ModelUpdate,
        )

        round_id = "test-round-comparison"
        model_version = "v1"
        threshold = 2

        np.random.seed(42)
        client_data = {
            "client_0": np.random.randn(20) * 0.1,
            "client_1": np.random.randn(20) * 0.1,
            "client_2": np.random.randn(20) * 0.1,
        }
        num_clients = len(client_data)

        plain_avg = sum(client_data.values()) / num_clients

        sa_clients = {cid: SecureAggregationClient(cid) for cid in client_data}
        pub_keys = {cid: c.agreement_public_key for cid, c in sa_clients.items()}
        for client in sa_clients.values():
            client.configure_peers(pub_keys)

        protocol = SecureAggregationProtocol(round_id, model_version, threshold)
        for cid, client in sa_clients.items():
            protocol.register_participant(cid, client.verification_key)
        protocol.setup_masks()

        for cid, client in sa_clients.items():
            update = ModelUpdate(
                participant_id=cid,
                round_id=round_id,
                model_version=model_version,
                update_data=client_data[cid],
            )
            masked = client.mask_update(update)
            protocol.submit_masked_update(masked)

        result = protocol.complete()
        secure_avg = result.aggregate_update / num_clients

        np.testing.assert_allclose(
            secure_avg, plain_avg, atol=1e-4,
            err_msg="Secure aggregation result diverges from plain FedAvg"
        )

    def test_overflow_bounds_check(self):
        """
        Verify that model weights stay within the safe range for the
        finite field (FIELD_PRIME = 2^31 - 1, SCALE = 1_000_000).
        """
        from secure_aggregation.crypto.pairwise_mask import FIELD_PRIME, SCALE

        model = create_model()
        params = get_parameters(model)
        flat = flatten_weights(params)

        max_abs = np.max(np.abs(flat))
        max_safe_sum = (FIELD_PRIME - 1) / (2 * SCALE)

        logger.info(f"Max |weight| = {max_abs:.6f}")
        logger.info(f"Max safe per-element sum = {max_safe_sum:.2f}")

        worst_case_sum = 10 * max_abs
        assert worst_case_sum < max_safe_sum, (
            f"Potential overflow: 10 * {max_abs:.4f} = {worst_case_sum:.4f} "
            f"> safe limit {max_safe_sum:.2f}"
        )

    def test_per_round_key_rotation(self):
        """
        Verify that different round_ids produce different masks
        (replay protection).
        """
        from secure_aggregation import (
            SecureAggregationClient,
            ModelUpdate,
        )

        cids = ["alice", "bob"]
        weights = np.array([1.0, 2.0, 3.0])

        masked_round1 = None
        masked_round2 = None

        for round_id, store in [("round-1", "r1"), ("round-2", "r2")]:
            clients = {cid: SecureAggregationClient(cid) for cid in cids}
            pub_keys = {cid: c.agreement_public_key for cid, c in clients.items()}
            for c in clients.values():
                c.configure_peers(pub_keys)

            update = ModelUpdate(
                participant_id="alice",
                round_id=round_id,
                model_version="v1",
                update_data=weights.copy(),
            )
            masked = clients["alice"].mask_update(update)

            if store == "r1":
                masked_round1 = masked.protected_data
            else:
                masked_round2 = masked.protected_data

        assert not np.array_equal(masked_round1, masked_round2), (
            "Same masks for different rounds - key rotation not working"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
