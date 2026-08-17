# packages/common/mock_model.py
# Technical Explanation: Implements the mock model logic.
# Stores local weights and mocks training steps by incrementing weights.

from typing import Any, List

import numpy as np

from packages.common.model_interface import IModel


class MockModel(IModel):
    """Mock model containing mock weights list [1.0, 2.0, 3.0] for verification."""

    def __init__(self) -> None:
        self.weights = [np.array([1.0, 2.0, 3.0], dtype=np.float32)]

    def get_weights(self) -> List[np.ndarray[Any, Any]]:
        """Returns the current mock weights."""
        return self.weights

    def set_weights(self, weights: List[np.ndarray[Any, Any]]) -> None:
        """Sets the current mock weights."""
        self.weights = weights

    def train(self, data: Any = None) -> float:
        """Mocks the training loop by incrementing each parameter array by 1.0."""
        self.weights = [self.weights[0] + 1.0]
        return 0.1  # Mock training loss

    def evaluate(self, data: Any = None) -> float:
        """Mocks evaluation returning static score."""
        return 0.95  # Mock accuracy
