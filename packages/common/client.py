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

    def __init__(self, model: IModel, data: Any = None) -> None:
        self.model = model
        self.data = data
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
        if self.data is not None:
            self.model.train(data=self.data)
        else:
            self.model.train()

        updated_weights = self.model.get_weights()
        events.on_fit_end.fire(updated_weights=updated_weights, context=context)

        # Returns updated weights, mock sample count (10), and metrics
        num_samples = len(self.data.dataset) if self.data and hasattr(self.data, "dataset") else 10
        return updated_weights, num_samples, {}

    def evaluate(
        self, parameters: List[Any], context: RoundContext
    ) -> Tuple[float, int, Dict[str, Any]]:
        """Evaluates model parameters locally."""
        events.on_evaluate_start.fire(parameters=parameters, context=context)

        # Update weights and compute evaluation
        self.model.set_weights(parameters)
        
        if self.data is not None:
            accuracy = self.model.evaluate(data=self.data)
        else:
            accuracy = self.model.evaluate()

        # Convert accuracy to mock validation loss
        loss = 1.0 - accuracy

        events.on_evaluate_end.fire(loss=loss, accuracy=accuracy, context=context)
        num_samples = len(self.data.dataset) if self.data and hasattr(self.data, "dataset") else 10
        return loss, num_samples, {"accuracy": accuracy}
