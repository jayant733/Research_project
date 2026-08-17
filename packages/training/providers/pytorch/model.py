"""
PyTorch-specific implementations of the IModel interface.
"""

from typing import Any, List

import torch
import torch.nn as nn

from packages.training.domain.interfaces import IModel
from packages.training.services.registries import model_registry


class TorchModel(IModel):
    """Wraps a PyTorch nn.Module to adhere to the IModel interface."""

    def __init__(self, module: nn.Module):
        self.module = module

    def get_weights(self) -> List[Any]:
        return [val.cpu().numpy() for _, val in self.module.state_dict().items()]

    def set_weights(self, weights: List[Any]) -> None:
        state_dict = self.module.state_dict()
        keys = list(state_dict.keys())
        for i, key in enumerate(keys):
            state_dict[key] = torch.tensor(weights[i])
        self.module.load_state_dict(state_dict, strict=True)

    def train(self, data: Any = None) -> float:
        # Core training logic is typically delegated to the Trainer,
        # but if called directly as per legacy interfaces, it raises or delegates.
        raise NotImplementedError("Direct model.train() is deprecated. Use a Trainer.")

    def evaluate(self, data: Any = None) -> float:
        raise NotImplementedError(
            "Direct model.evaluate() is deprecated. Use a Trainer."
        )


class SimpleMLP(nn.Module):
    """A standard Simple MLP model for testing and baselines."""

    def __init__(self, input_dim: int = 20, hidden_dim: int = 64, num_classes: int = 2):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x):
        return self.network(x)


# Register models
model_registry.register("SimpleMLP", SimpleMLP)
