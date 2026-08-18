"""Flower client implementation for Federix FL pipeline."""
import logging
import os
import sys
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import flwr as fl

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from model.model_config import FLConfig
from model.serialization import get_parameters, set_parameters

logger = logging.getLogger(__name__)

class FederixClient(fl.client.NumPyClient):
    """Flower client for federated learning with FederixNet."""

    def __init__(self, cid: str, model: nn.Module, train_loader: DataLoader, test_loader: DataLoader, config: FLConfig):
        self.cid = cid
        self.model = model
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

    def get_parameters(self, config: dict) -> list[np.ndarray]:
        """Return current model parameters."""
        return get_parameters(self.model)

    def set_parameters(self, parameters: list[np.ndarray]) -> None:
        """Set model parameters from server."""
        set_parameters(self.model, parameters)

    def fit(self, parameters: list[np.ndarray], config: dict) -> tuple[list[np.ndarray], int, dict]:
        """Train model on local data and return updated parameters."""
        self.set_parameters(parameters)
        self.model.train()
        optimizer = torch.optim.SGD(self.model.parameters(), lr=self.config.learning_rate)
        criterion = nn.CrossEntropyLoss()

        total_samples = 0
        total_loss = 0.0
        for epoch in range(self.config.local_epochs):
            for batch in self.train_loader:
                images, labels = batch
                images, labels = images.to(self.device), labels.to(self.device)
                optimizer.zero_grad()
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                total_samples += len(labels)
                total_loss += loss.item() * len(labels)

        avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
        logger.info(f'Client {self.cid}: trained on {total_samples} samples, loss={avg_loss:.4f}')

        return get_parameters(self.model), total_samples, {'cid': self.cid, 'loss': avg_loss}

    def evaluate(self, parameters: list[np.ndarray], config: dict) -> tuple[float, int, dict]:
        """Evaluate model on local test data."""
        self.set_parameters(parameters)
        self.model.eval()
        criterion = nn.CrossEntropyLoss()

        total_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for batch in self.test_loader:
                images, labels = batch
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                total_loss += loss.item() * len(labels)
                _, predicted = torch.max(outputs, 1)
                correct += (predicted == labels).sum().item()
                total += len(labels)

        avg_loss = total_loss / total if total > 0 else 0.0
        accuracy = correct / total if total > 0 else 0.0
        logger.info(f'Client {self.cid}: eval loss={avg_loss:.4f}, accuracy={accuracy:.4f}')

        return avg_loss, total, {'cid': self.cid, 'accuracy': accuracy}
