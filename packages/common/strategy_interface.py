# packages/common/strategy_interface.py
# Technical Explanation: Interface defining global strategy callbacks.

from abc import ABC, abstractmethod
from typing import Any, List, Tuple


class IFederationStrategy(ABC):
    """Abstract interface defining required custom strategy workflows."""

    @abstractmethod
    def initialize_parameters(self) -> List[Any]:
        """
        Initializes global model parameters on the server.

        Outputs:
            A list of initialized weights.
        """
        pass

    @abstractmethod
    def aggregate_fit(self, results: List[Tuple[List[Any], int]]) -> List[Any]:
        """
        Processes client training updates and aggregates them.

        Inputs:
            results: List of tuples containing client parameters and sample count.
        Outputs:
            A single list of aggregated weights.
        """
        pass

    @abstractmethod
    def aggregate_evaluate(
        self, results: List[Tuple[float, int]]
    ) -> Tuple[float, float]:
        """
        Processes client evaluation results and aggregates them.

        Inputs:
            results: List of tuples containing loss and sample count.
        Outputs:
            A tuple of (average loss, average accuracy/score metrics).
        """
        pass
