"""Small classifier used by the local CPU demonstration."""

import torch
from torch import nn


class CompactMLP(nn.Module):
    """A compact network that fits in one CKKS ciphertext."""

    def __init__(
        self, input_dim: int = 8, hidden_dim: int = 16, num_classes: int = 2
    ) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        hidden = torch.relu(self.fc1(features))
        return self.fc2(hidden)
