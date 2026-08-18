"""PyTorch model definitions for federated learning."""
import torch
import torch.nn as nn
import torch.nn.functional as F

class FederixNet(nn.Module):
    """
    A small CNN for CIFAR-10 classification.
    
    Architecture:
    - Conv2d(3, 16, 3, padding=1) -> ReLU -> MaxPool2d(2)
    - Conv2d(16, 32, 3, padding=1) -> ReLU -> MaxPool2d(2)
    - Flatten -> Linear(32*8*8, 128) -> ReLU -> Linear(128, 10)
    
    This model has approximately 62K parameters.
    """
    def __init__(self) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(32 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of the network returning logits."""
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

def create_model() -> FederixNet:
    """Instantiate and return the FederixNet model."""
    return FederixNet()
