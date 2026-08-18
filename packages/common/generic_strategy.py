# packages/common/generic_strategy.py
# Technical Explanation: Implements the generic federation strategy.
# Employs dependency injection to delegate parameter merging to an IAggregator.

from typing import Any, List, Tuple

from packages.common.aggregator_interface import IAggregator
from packages.common.events import events
from packages.common.strategy_interface import IFederationStrategy


class GenericStrategy(IFederationStrategy):
    """A provider-agnostic strategy routing aggregates to injected aggregators."""

    def __init__(self, initial_parameters: List[Any], aggregator: IAggregator) -> None:
        self.initial_parameters = initial_parameters
        self.aggregator = aggregator

    def initialize_parameters(self) -> List[Any]:
        """Returns baseline server weights."""
        return self.initial_parameters

    def aggregate_fit(self, results: List[Tuple[List[Any], int]]) -> List[Any]:
        """Delegates parameters aggregation to the injected aggregator."""
        events.on_aggregate_start.fire(results=results)
        aggregated = self.aggregator.aggregate(results)
        events.on_aggregate_end.fire(aggregated=aggregated)
        return aggregated

    def aggregate_evaluate(
        self, results: List[Tuple[float, int]]
    ) -> Tuple[float, float]:
        """Averages metric parameters returned by client nodes."""
        if not results:
            return 0.0, 0.0

        total_samples = sum(sample_count for _, sample_count in results)
        if total_samples == 0:
            return 0.0, 0.0

        weighted_loss = (
            sum(loss * sample_count for loss, sample_count in results) / total_samples
        )
        # Return weighted loss, and 0.0 for accuracy since metrics aren't currently propagated
        return weighted_loss, 0.0
