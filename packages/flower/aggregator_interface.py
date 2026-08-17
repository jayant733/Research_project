# packages/flower/aggregator_interface.py
# Technical Explanation: Declares aggregation methods for model parameters combining.

from abc import ABC, abstractmethod
from typing import Any, List, Tuple

import numpy as np


class IAggregator(ABC):
    """Abstract interface defining required custom aggregation procedures."""

    @abstractmethod
    def aggregate_pool(
        self, pool_id: str, updates: List[Tuple[List[np.ndarray[Any, Any]], int]]
    ) -> List[np.ndarray[Any, Any]]:
        """
        Aggregates parameters received from clients within a specific tier.

        Inputs:
            pool_id: ID of the privacy tier (e.g. 'fhe').
            updates: List of client weight parameters and sample count tuples.
        Outputs:
            A single list of aggregated NumPy arrays representing merged weights.
        Exceptions:
            PoolAggregationFailure: Raised if the mathematical averaging fails.
        """
        pass
