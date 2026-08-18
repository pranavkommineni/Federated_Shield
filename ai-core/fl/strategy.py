"""Custom FL strategy definitions (FederixStrategy, SecureFederixStrategy)."""
import sys
import os
import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.common import (
    Parameters, Scalar, FitRes, EvaluateRes,
    ndarrays_to_parameters, parameters_to_ndarrays,
)
from flwr.server.client_proxy import ClientProxy
import logging
import numpy as np

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from model.model_config import FLConfig
from model.serialization import flatten_weights, unflatten_weights

logger = logging.getLogger(__name__)

class FederixStrategy(FedAvg):
    """Custom FedAvg strategy with logging and round management."""

    def __init__(self, config: FLConfig, **kwargs):
        self.fl_config = config
        super().__init__(
            fraction_fit=config.fraction_fit,
            fraction_evaluate=config.fraction_evaluate,
            min_fit_clients=config.min_fit_clients,
            min_available_clients=config.min_available_clients,
            min_evaluate_clients=config.min_evaluate_clients,
            **kwargs,
        )
        logger.info(f'FederixStrategy initialized: min_fit={config.min_fit_clients}, '
                     f'min_available={config.min_available_clients}, '
                     f'fraction_fit={config.fraction_fit}')

    def aggregate_fit(
        self,
        server_round: int,
        results: list[tuple[ClientProxy, FitRes]],
        failures: list[tuple[ClientProxy, FitRes] | BaseException],
    ) -> tuple[Parameters | None, dict[str, Scalar]]:
        """Aggregate fit results with logging and failure handling."""
        total = len(results) + len(failures)
        logger.info(f'Round {server_round}: received {len(results)}/{total} results, {len(failures)} failures')

        if failures:
            logger.warning(f'Round {server_round}: {len(failures)} client(s) failed')

        if len(results) < self.fl_config.min_fit_clients:
            logger.error(f'Round {server_round}: insufficient results '
                          f'({len(results)}/{self.fl_config.min_fit_clients}). Skipping round.')
            return None, {}

        # Delegate to FedAvg
        aggregated_parameters, metrics = super().aggregate_fit(server_round, results, failures)

        if aggregated_parameters is not None:
            logger.info(f'Round {server_round}: aggregation successful')

        return aggregated_parameters, metrics

    def aggregate_evaluate(
        self,
        server_round: int,
        results: list[tuple[ClientProxy, EvaluateRes]],
        failures: list[tuple[ClientProxy, EvaluateRes] | BaseException],
    ) -> tuple[float | None, dict[str, Scalar]]:
        """Aggregate evaluation results with logging."""
        if not results:
            return None, {}

        # Weighted average of loss
        total_samples = sum(r.num_examples for _, r in results)
        weighted_loss = sum(r.num_examples * r.loss for _, r in results) / total_samples

        # Weighted average of accuracy
        weighted_accuracy = sum(
            r.num_examples * r.metrics.get('accuracy', 0.0) for _, r in results
        ) / total_samples

        logger.info(f'Round {server_round}: eval loss={weighted_loss:.4f}, accuracy={weighted_accuracy:.4f}')

        return weighted_loss, {'accuracy': weighted_accuracy}


def _try_import_secure_aggregation():
    """Attempt to import Team 2's secure aggregation module."""
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        privacy_path = os.path.join(base_dir, 'Privacy-Security')
        if os.path.exists(privacy_path) and privacy_path not in sys.path:
            sys.path.insert(0, privacy_path)

        from secure_aggregation import (
            SecureAggregationProtocol,
            SecureAggregationClient,
            ModelUpdate,
        )
        from secure_aggregation.crypto.pairwise_mask import FIELD_PRIME, SCALE
        return SecureAggregationProtocol, SecureAggregationClient, ModelUpdate, FIELD_PRIME, SCALE
    except ImportError as e:
        logger.error(f"Secure aggregation module not available: {e}")
        return None


class SecureFederixStrategy(FederixStrategy):
    """
    FedAvg strategy with Secure Aggregation protocol.
    """

    def __init__(self, config: FLConfig, **kwargs):
        super().__init__(config, **kwargs)
        sa_imports = _try_import_secure_aggregation()
        if sa_imports is None:
            raise ImportError(
                "SecureFederixStrategy requires secure_aggregation module. "
                "Ensure Privacy-Security/secure_aggregation is available."
            )
        (
            self._SAProtocol,
            self._SAClient,
            self._ModelUpdate,
            self._FIELD_PRIME,
            self._SCALE,
        ) = sa_imports
        logger.info("SecureFederixStrategy initialized with Secure Aggregation")

    def _check_overflow_bounds(self, flat_weights: list[np.ndarray], num_clients: int) -> None:
        """Warn if the sum of weights could overflow the finite field."""
        max_safe = (self._FIELD_PRIME - 1) / (2 * self._SCALE)
        for i, flat in enumerate(flat_weights):
            max_abs = np.max(np.abs(flat))
            worst_case = num_clients * max_abs
            if worst_case > max_safe * 0.9:
                logger.warning(
                    f"Overflow risk: client {i} max|w|={max_abs:.4f}, "
                    f"worst-case sum={worst_case:.4f}, limit={max_safe:.2f}"
                )

    def aggregate_fit(
        self,
        server_round: int,
        results: list[tuple[ClientProxy, FitRes]],
        failures: list[tuple[ClientProxy, FitRes] | BaseException],
    ) -> tuple[Parameters | None, dict[str, Scalar]]:
        """Aggregate fit results using Secure Aggregation protocol."""
        total = len(results) + len(failures)
        logger.info(
            f"Round {server_round} [SECURE]: received {len(results)}/{total} results, "
            f"{len(failures)} failures"
        )

        if failures:
            logger.warning(f"Round {server_round}: {len(failures)} client(s) failed")

        if len(results) < self.fl_config.min_fit_clients:
            logger.error(
                f"Round {server_round}: insufficient results "
                f"({len(results)}/{self.fl_config.min_fit_clients}). Skipping round."
            )
            return None, {}

        round_id = f"round-{server_round}"
        model_version = f"v{server_round}"
        threshold = self.fl_config.min_fit_clients
        num_clients = len(results)

        client_data = {}
        shapes = None
        for i, (proxy, fit_res) in enumerate(results):
            cid = fit_res.metrics.get("cid", f"client_{i}")
            params = parameters_to_ndarrays(fit_res.parameters)
            if shapes is None:
                shapes = [p.shape for p in params]
            flat = flatten_weights(params)
            client_data[cid] = flat

        self._check_overflow_bounds(list(client_data.values()), num_clients)

        try:
            sa_clients = {}
            for cid in client_data:
                sa_clients[cid] = self._SAClient(cid)

            pub_keys = {
                cid: client.agreement_public_key
                for cid, client in sa_clients.items()
            }

            for client in sa_clients.values():
                client.configure_peers(pub_keys)

            protocol = self._SAProtocol(round_id, model_version, threshold)
            for cid, client in sa_clients.items():
                protocol.register_participant(cid, client.verification_key)

            protocol.setup_masks()

            for cid, client in sa_clients.items():
                model_update = self._ModelUpdate(
                    participant_id=cid,
                    round_id=round_id,
                    model_version=model_version,
                    update_data=client_data[cid],
                )
                masked = client.mask_update(model_update)
                protocol.submit_masked_update(masked)

            result = protocol.complete()

            aggregate_avg = result.aggregate_update / num_clients

            params_list = unflatten_weights(aggregate_avg, shapes)
            aggregated_parameters = ndarrays_to_parameters(params_list)

            logger.info(
                f"Round {server_round} [SECURE]: aggregation successful, "
                f"{len(result.contributors)} contributors"
            )

            dropout_info = result.dropout_information
            metrics = {
                "secure_agg": True,
                "contributors": len(result.contributors),
                "missing": len(dropout_info.missing),
                "threshold_met": dropout_info.threshold_met,
            }

            return aggregated_parameters, metrics

        except Exception as e:
            logger.error(
                f"Round {server_round} [SECURE]: aggregation failed: {e}",
                exc_info=True,
            )
            return None, {"secure_agg_error": str(e)}
