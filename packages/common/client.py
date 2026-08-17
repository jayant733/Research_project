# packages/common/client.py
# Technical Explanation: Implements the generic client business logic.
# Completely decoupled from Flower classes. Uses injected IModel implementations
# and dispatches logs/status parameters via the global events emitter system.

from typing import Any, Dict, List, Tuple

from packages.common.client_interface import IGenericClient
from packages.common.context import RoundContext
from packages.common.events import events
from packages.common.model_interface import IModel


class GenericClient(IGenericClient):
    """Core client engine delegating weights modification to injected models."""

    def __init__(self, model: IModel) -> None:
        self.model = model
        events.on_client_init.fire(model=model)

    def get_parameters(self, context: RoundContext) -> List[Any]:
        """Exposes model weights."""
        events.on_get_parameters.fire(context=context)
        return self.model.get_weights()

    def fit(
        self, parameters: List[Any], context: RoundContext
    ) -> Tuple[List[Any], int, Dict[str, Any]]:
        """Updates local weights, runs train loop, and returns results."""
        events.on_fit_start.fire(parameters=parameters, context=context)

        # 1. Update model weights
        self.model.set_weights(parameters)

        # 2. Trigger model local training loop
        self.model.train()

        updated_weights = self.model.get_weights()
        events.on_fit_end.fire(updated_weights=updated_weights, context=context)

        # Returns updated weights, mock sample count (10), and metrics
        return updated_weights, 10, {}

    def evaluate(
        self, parameters: List[Any], context: RoundContext
    ) -> Tuple[float, int, Dict[str, Any]]:
        """Evaluates model parameters locally."""
        events.on_evaluate_start.fire(parameters=parameters, context=context)

        # Update weights and compute evaluation
        self.model.set_weights(parameters)
        accuracy = self.model.evaluate()

        # Convert accuracy to mock validation loss
        loss = 1.0 - accuracy

        events.on_evaluate_end.fire(loss=loss, accuracy=accuracy, context=context)
        return loss, 10, {"accuracy": accuracy}
