import torch.nn as nn
import torch.nn.functional as F

from packages.training.services.registries import model_registry


class FederatedCNN(nn.Module):
    """A standard CNN for CIFAR-10 federated learning."""
    def __init__(self):
        super(FederatedCNN, self).__init__()
        # Input channels = 3, output channels = 32
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        
        # 32x32 -> pool -> 16x16 -> pool -> 8x8 -> pool -> 4x4
        # 64 channels * 4 * 4 = 1024
        self.fc1 = nn.Linear(1024, 64)
        self.fc2 = nn.Linear(64, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 1024)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

model_registry.register("FederatedCNN", FederatedCNN)
