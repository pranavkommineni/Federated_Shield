"""
Org-side deployable training node entrypoint.

Initializes local model, data loader, and client instance for deployment.
"""
import logging
from typing import Optional
import flwr as fl

from ..model.federix_model import create_model, FederixNet
from ..model.model_config import FLConfig
from ..fl.client import FederixClient

logger = logging.getLogger(__name__)

class TrainingNode:
    """Deployable organization-side FL training node wrapper."""

    def __init__(
        self,
        node_id: str,
        server_address: str = "127.0.0.1:8080",
        config: Optional[FLConfig] = None,
    ):
        self.node_id = node_id
        self.server_address = server_address
        self.config = config or FLConfig(server_address=server_address)
        self.model = create_model()

    def start(self, train_loader, test_loader) -> None:
        """Start the training node client and connect to the FL server."""
        client = FederixClient(
            cid=self.node_id,
            model=self.model,
            train_loader=train_loader,
            test_loader=test_loader,
            config=self.config,
        )
        logger.info(f"Starting TrainingNode {self.node_id}, connecting to {self.server_address}")
        fl.client.start_client(
            server_address=self.server_address,
            client=client.to_client(),
        )
