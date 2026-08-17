# packages/common/client_interface.py
# Technical Explanation: Interface defining generic federated client nodes.

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from packages.common.context import RoundContext


class IGenericClient(ABC):
    """Abstract interface for client business operations, decoupled from Flower."""

    @abstractmethod
    def get_parameters(self, context: RoundContext) -> List[Any]:
        """
        Retrieves local weights.

        Inputs:
            context: Environment specifications.
        Outputs:
            Weights list.
        """
        pass

    @abstractmethod
    def fit(
        self, parameters: List[Any], context: RoundContext
    ) -> Tuple[List[Any], int, Dict[str, Any]]:
        """
        Trains model using global weights.

        Inputs:
            parameters: Incoming global weights.
            context: Current round context details.
        Outputs:
            A tuple of (updated weights, sample count, metrics).
        """
        pass

    @abstractmethod
    def evaluate(
        self, parameters: List[Any], context: RoundContext
    ) -> Tuple[float, int, Dict[str, Any]]:
        """
        Evaluates parameters locally.

        Inputs:
            parameters: Incoming weights to validate.
            context: Current round context details.
        Outputs:
            A tuple of (loss, sample count, metrics).
        """
        pass
