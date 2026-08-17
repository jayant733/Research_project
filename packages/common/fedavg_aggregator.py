# packages/common/fedavg_aggregator.py
# Technical Explanation: Implements standard Federated Averaging algorithm.
# Calculates sample-weighted averages of incoming client parameter updates.

from typing import Any, List, Tuple

import numpy as np

from packages.common.aggregator_interface import IAggregator


class FedAvgAggregator(IAggregator):
    """Calculates weighted averages of model weights."""

    def aggregate(self, updates: List[Tuple[List[Any], int]]) -> List[Any]:
        """Weighted average aggregation implementation."""
        if not updates:
            return []

        # Calculate total sample count
        total_samples = sum(sample_count for _, sample_count in updates)
        if total_samples == 0:
            return []

        # Compute weighted average
        # We assume each update has a single weights array (mock model weights list)
        weighted_sum = np.zeros_like(updates[0][0][0])

        for weights_list, sample_count in updates:
            weighted_sum += weights_list[0] * (sample_count / total_samples)

        return [weighted_sum]
