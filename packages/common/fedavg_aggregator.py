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

        reference = updates[0][0]
        tensor_count = len(reference)
        aggregated: List[Any] = []
        for index in range(tensor_count):
            reference_tensor = np.asarray(reference[index])
            weighted_sum = np.zeros(reference_tensor.shape, dtype=np.float64)
            for weights_list, sample_count in updates:
                if len(weights_list) != tensor_count:
                    raise ValueError("Clients returned different numbers of tensors.")
                tensor = np.asarray(weights_list[index])
                if tensor.shape != reference_tensor.shape:
                    raise ValueError(
                        f"Tensor {index} shape {tensor.shape} does not match "
                        f"{reference_tensor.shape}."
                    )
                weighted_sum += tensor.astype(np.float64) * (
                    sample_count / total_samples
                )
            aggregated.append(weighted_sum.astype(reference_tensor.dtype))
        return aggregated
