"""
Core interfaces for the Training Engine domain.
"""

from abc import ABC, abstractmethod
from typing import Any, List

from packages.training.domain.config import ExperimentConfig
from packages.training.domain.metrics import TrainingResult


class IModel(ABC):
    """Abstract interface defining standard operations for ML models."""

    @abstractmethod
    def get_weights(self) -> List[Any]:
        pass

    @abstractmethod
    def set_weights(self, weights: List[Any]) -> None:
        pass

    @abstractmethod
    def train(self, data: Any = None) -> float:
        pass

    @abstractmethod
    def evaluate(self, data: Any = None) -> float:
        pass


class BaseTrainer(ABC):
    """Abstract interface for a Provider's core training logic."""

    @abstractmethod
    def execute(self, model: IModel, config: ExperimentConfig) -> TrainingResult:
        """Executes the training loop according to the config and returns the result."""
        pass
