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

    def __init__(self, model: IModel, data: Any = None, test_data: Any = None) -> None:
        self.model = model
        self.data = data
        self.test_data = data if test_data is None else test_data
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
        epochs = int(context.config.get("epochs", 1))
        learning_rate = float(context.config.get("lr", 0.01))
        self._train(epochs, learning_rate)

        updated_weights = self.model.get_weights()
        events.on_fit_end.fire(updated_weights=updated_weights, context=context)

        # Returns updated weights, mock sample count (10), and metrics
        num_samples = (
            len(self.data.dataset)
            if self.data and hasattr(self.data, "dataset")
            else 10
        )
        return updated_weights, num_samples, {}

    def evaluate(
        self, parameters: List[Any], context: RoundContext
    ) -> Tuple[float, int, Dict[str, Any]]:
        """Evaluates model parameters locally."""
        events.on_evaluate_start.fire(parameters=parameters, context=context)

        # Update weights and compute evaluation
        self.model.set_weights(parameters)

        if self.test_data is not None:
            accuracy = self.model.evaluate(data=self.test_data)
        else:
            accuracy = self.model.evaluate()

        # Convert accuracy to mock validation loss
        loss = 1.0 - accuracy

        events.on_evaluate_end.fire(loss=loss, accuracy=accuracy, context=context)
        num_samples = (
            len(self.data.dataset)
            if self.data and hasattr(self.data, "dataset")
            else 10
        )
        return loss, num_samples, {"accuracy": accuracy}

    def _train(self, epochs: int, learning_rate: float) -> None:
        """Train with optional epoch settings, falling back for simple models."""
        if self.data is None:
            self.model.train()
            return
        try:
            self.model.train(data=self.data, epochs=epochs, lr=learning_rate)
        except TypeError:
            self.model.train(data=self.data)
