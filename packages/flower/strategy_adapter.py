# packages/flower/strategy_adapter.py
# Technical Explanation: Implements Strategy Adapter. Subclasses FedAvg to handle
# conversions between Flower Parameters/Scalars and standard List/Dict types.

from typing import Any, Dict, List, Optional, Tuple, Union

import flwr as fl
from flwr.common import (
    EvaluateRes,
    FitRes,
    Parameters,
    Scalar,
    ndarrays_to_parameters,
    parameters_to_ndarrays,
)
from flwr.server.client_proxy import ClientProxy

from packages.common.strategy_interface import IFederationStrategy


class FlowerStrategyAdapter(fl.server.strategy.FedAvg):
    """Adapts IFederationStrategy to Flower strategy interfaces."""

    def __init__(self, generic_strategy: IFederationStrategy, **kwargs: Any) -> None:
        self.generic_strategy = generic_strategy
        super().__init__(**kwargs)

    def initialize_parameters(self, client_manager: Any) -> Optional[Parameters]:
        """Initializes parameter variables using the generic strategy."""
        weights = self.generic_strategy.initialize_parameters()
        if not weights:
            return None
        return ndarrays_to_parameters(weights)

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        """Extracts NumPy arrays and delegates to the generic strategy."""
        generic_results = []
        for _, fit_res in results:
            weights = parameters_to_ndarrays(fit_res.parameters)
            generic_results.append((weights, fit_res.num_examples))

        aggregated_weights = self.generic_strategy.aggregate_fit(generic_results)
        if not aggregated_weights:
            return None, {}

        return ndarrays_to_parameters(aggregated_weights), {}

    def aggregate_evaluate(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, EvaluateRes]],
        failures: List[Union[Tuple[ClientProxy, EvaluateRes], BaseException]],
    ) -> Tuple[Optional[float], Dict[str, Scalar]]:
        """Maps evaluation results from clients and aggregates them."""
        generic_results = []
        for _, eval_res in results:
            generic_results.append((eval_res.loss, eval_res.num_examples))

        loss, accuracy = self.generic_strategy.aggregate_evaluate(generic_results)
        return loss, {"accuracy": accuracy}
