"""PyTorch model definitions for federated learning."""
import torch
import torch.nn as nn
import torch.nn.functional as F

class FederixNet(nn.Module):
    """
    A CNN for CIFAR-10 classification with BatchNorm and Dropout regularization.

    Architecture:
    - Conv2d(in_channels, 16, 3, padding=1) -> BatchNorm2d(16) -> ReLU -> MaxPool2d(2)
    - Conv2d(16, 32, 3, padding=1) -> BatchNorm2d(32) -> ReLU -> MaxPool2d(2)
    - Flatten -> Linear(32*8*8, hidden_dim) -> ReLU -> Dropout(dropout_rate) -> Linear(hidden_dim, num_classes)
    """
    def __init__(
        self,
        in_channels: int = 3,
        num_classes: int = 10,
        hidden_dim: int = 128,
        dropout_rate: float = 0.25,
    ) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, 16, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        self.fc1 = nn.Linear(32 * 8 * 8, hidden_dim)
        self.dropout = nn.Dropout(p=dropout_rate)
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of the network returning logits."""
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

def create_model(
    in_channels: int = 3,
    num_classes: int = 10,
    hidden_dim: int = 128,
    dropout_rate: float = 0.25,
) -> FederixNet:
    """Instantiate and return the FederixNet model."""
    return FederixNet(
        in_channels=in_channels,
        num_classes=num_classes,
        hidden_dim=hidden_dim,
        dropout_rate=dropout_rate,
    )

