# packages/common/model_interface.py
# Technical Explanation: Declares standard interfaces for model parameter
# management and execution.

from abc import ABC, abstractmethod
from typing import Any, List


class IModel(ABC):
    """Abstract interface defining standard operations for ML models."""

    @abstractmethod
    def get_weights(self) -> List[Any]:
        """
        Retrieves the model weights.

        Outputs:
            A list of tensor/array weights.
        """
        pass

    @abstractmethod
    def set_weights(self, weights: List[Any]) -> None:
        """
        Sets the model weights.

        Inputs:
            weights: List of tensor/array weights to apply.
        """
        pass

    @abstractmethod
    def train(self, data: Any = None) -> float:
        """
        Executes local training on data.

        Inputs:
            data: Local training partition/dataset.
        Outputs:
            The training loss.
        """
        pass

    @abstractmethod
    def evaluate(self, data: Any = None) -> float:
        """
        Evaluates the model performance.

        Inputs:
            data: Local validation partition/dataset.
        Outputs:
            The validation score (accuracy or loss metric).
        """
        pass
