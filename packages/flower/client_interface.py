# packages/flower/client_interface.py
# Technical Explanation: Declares standard interfaces for the Flower Client wrapper.

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

import numpy as np


class IFlowerClient(ABC):
    """Abstract interface defining required behaviors for federated client nodes."""

    @abstractmethod
    def get_parameters(self, config: Dict[str, Any]) -> List[np.ndarray[Any, Any]]:
        """
        Retrieves the local model parameters.

        Inputs:
            config: Key-value settings dictionary from the server.
        Outputs:
            A list of NumPy arrays representing model weights.
        Exceptions:
            None.
        """
        pass

    @abstractmethod
    def fit(
        self, parameters: List[np.ndarray[Any, Any]], config: Dict[str, Any]
    ) -> Tuple[List[np.ndarray[Any, Any]], int, Dict[str, Any]]:
        """
        Trains the local model using the parameters sent by the server.

        Inputs:
            parameters: Global model parameters list.
            config: Training configurations dictionary.
        Outputs:
            A tuple of (updated parameters list, training sample count,
            metrics dictionary).
        Exceptions:
            TrainingInterruptException: Raised if training fails.
        """
        pass

    @abstractmethod
    def evaluate(
        self, parameters: List[np.ndarray[Any, Any]], config: Dict[str, Any]
    ) -> Tuple[float, int, Dict[str, Any]]:
        """
        Evaluates the parameters sent by the server on local validation datasets.

        Inputs:
            parameters: Model parameters to evaluate.
            config: Evaluation configurations dictionary.
        Outputs:
            A tuple of (loss value, evaluation sample count, metrics dictionary).
        Exceptions:
            None.
        """
        pass
