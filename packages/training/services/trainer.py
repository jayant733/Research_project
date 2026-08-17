"""
Core Trainer orchestration logic. Binds config, tracker, callbacks, and the provider.
"""


from typing import Any

from packages.training.domain.config import ExperimentConfig
from packages.training.domain.interfaces import IModel
from packages.training.domain.metrics import TrainingResult
from packages.training.services.callbacks import CallbackManager
from packages.training.services.registries import provider_registry
from packages.training.services.seed import SeedManager
from packages.training.services.tracker import ExperimentTracker


class TrainingSession:
    """
    Orchestrates the training lifecycle independent of the provider.
    """

    def __init__(self, config: ExperimentConfig, callbacks: CallbackManager):
        self.config = config
        self.callbacks = callbacks
        self.tracker = ExperimentTracker()

    def execute(
        self, model: IModel, provider_name: str = "pytorch", **provider_kwargs: Any
    ) -> TrainingResult:
        if self.config.random_seed is not None:
            SeedManager.set_seed(self.config.random_seed)

        self.tracker.start_experiment(self.config)
        self.callbacks.on_train_start(self)

        # Resolve the trainer provider dynamically
        trainer = provider_registry.get_trainer(
            provider_name, config=self.config, callbacks=self.callbacks
        )

        # Execute provider-specific training loop
        result = trainer.execute(model, self.config, **provider_kwargs)

        # Inject metadata into the result
        result.metadata = self.tracker.metadata

        self.callbacks.on_train_end(self)
        self.tracker.end_experiment()

        return result
