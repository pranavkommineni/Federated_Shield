"""Flower server entrypoint and strategy builder."""
import logging
import os
import sys
import flwr as fl
from flwr.common import ndarrays_to_parameters

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from model.model_config import FLConfig
from model.federix_model import create_model
from model.serialization import get_parameters
from fl.strategy import FederixStrategy, SecureFederixStrategy

logger = logging.getLogger(__name__)

def build_strategy(config: FLConfig) -> FederixStrategy:
    """Build the FL strategy based on configuration."""
    model = create_model()
    initial_parameters = ndarrays_to_parameters(get_parameters(model))

    if config.use_secure_aggregation:
        logger.info("Building SecureFederixStrategy (Team 2 integration)")
        return SecureFederixStrategy(config, initial_parameters=initial_parameters)
    else:
        logger.info("Building FederixStrategy (plain FedAvg)")
        return FederixStrategy(config, initial_parameters=initial_parameters)

def start_fl_server(config: FLConfig | None = None) -> None:
    """Start the Flower federated learning server."""
    if config is None:
        config = FLConfig()

    strategy = build_strategy(config)

    logger.info(f'Starting FL server on {config.server_address} for {config.num_rounds} rounds')

    fl.server.start_server(
        server_address=config.server_address,
        config=fl.server.ServerConfig(num_rounds=config.num_rounds),
        strategy=strategy,
    )

    logger.info('FL server finished')
