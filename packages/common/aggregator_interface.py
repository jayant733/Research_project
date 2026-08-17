# packages/common/aggregator_interface.py
# Technical Explanation: Interface specification for model parameter
# aggregation strategies.

from abc import ABC, abstractmethod
from typing import Any, List, Tuple


class IAggregator(ABC):
    """Abstract interface defining required custom aggregation procedures."""

    @abstractmethod
    def aggregate(self, updates: List[Tuple[List[Any], int]]) -> List[Any]:
        """
        Aggregates parameters received from multiple client nodes.

        Inputs:
            updates: List of client weight parameters and sample count tuples.
        Outputs:
            A single list of aggregated weights.
        """
        pass
