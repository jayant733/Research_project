"""
Callback system allowing extensible hooks into the training loop.
"""

from abc import ABC
from typing import Any, List


class TrainerCallback(ABC):
    """Base interface for all callbacks."""

    def on_train_start(self, trainer: Any, **kwargs) -> None:
        pass

    def on_epoch_begin(self, trainer: Any, epoch: int, **kwargs) -> None:
        pass

    def on_batch_begin(self, trainer: Any, batch: int, **kwargs) -> None:
        pass

    def on_batch_end(self, trainer: Any, batch: int, logs: dict, **kwargs) -> None:
        pass

    def on_epoch_end(self, trainer: Any, epoch: int, logs: dict, **kwargs) -> None:
        pass

    def on_train_end(self, trainer: Any, **kwargs) -> None:
        pass


class CallbackManager:
    """Manages execution of a list of callbacks."""

    def __init__(self, callbacks: List[TrainerCallback] = None):
        self.callbacks = callbacks or []

    def on_train_start(self, trainer: Any, **kwargs) -> None:
        for cb in self.callbacks:
            cb.on_train_start(trainer, **kwargs)

    def on_epoch_begin(self, trainer: Any, epoch: int, **kwargs) -> None:
        for cb in self.callbacks:
            cb.on_epoch_begin(trainer, epoch, **kwargs)

    def on_batch_begin(self, trainer: Any, batch: int, **kwargs) -> None:
        for cb in self.callbacks:
            cb.on_batch_begin(trainer, batch, **kwargs)

    def on_batch_end(self, trainer: Any, batch: int, logs: dict, **kwargs) -> None:
        for cb in self.callbacks:
            cb.on_batch_end(trainer, batch, logs, **kwargs)

    def on_epoch_end(self, trainer: Any, epoch: int, logs: dict, **kwargs) -> None:
        for cb in self.callbacks:
            cb.on_epoch_end(trainer, epoch, logs, **kwargs)

    def on_train_end(self, trainer: Any, **kwargs) -> None:
        for cb in self.callbacks:
            cb.on_train_end(trainer, **kwargs)


class LoggingCallback(TrainerCallback):
    """Logs epoch metrics."""

    def __init__(self, logger: Any):
        self.logger = logger

    def on_epoch_end(self, trainer: Any, epoch: int, logs: dict, **kwargs) -> None:
        self.logger.info(f"Epoch {epoch} finished. Metrics: {logs}")


class MetricsCallback(TrainerCallback):
    """Tracks metrics history."""

    def __init__(self, history: Any):
        self.history = history

    def on_epoch_end(self, trainer: Any, epoch: int, logs: dict, **kwargs) -> None:
        # Assume history is an instance of MetricsHistory
        from packages.training.domain.metrics import TrainingMetrics

        metrics = TrainingMetrics(
            loss=logs.get("loss", 0.0),
            accuracy=logs.get("accuracy", 0.0),
            epoch=epoch,
            step=logs.get("step", 0),
            training_time=logs.get("training_time", 0.0),
            throughput=logs.get("throughput", 0.0),
            device=logs.get("device", "unknown"),
            gpu_memory=logs.get("gpu_memory", 0),
            reserved_memory=logs.get("reserved_memory", 0),
        )
        self.history.epoch_metrics.append(metrics)


class CheckpointCallback(TrainerCallback):
    """Triggers checkpoint saving."""

    def __init__(self, checkpoint_manager: Any):
        self.checkpoint_manager = checkpoint_manager

    def on_epoch_end(self, trainer: Any, epoch: int, logs: dict, **kwargs) -> None:
        # Logic to decide if we should save, e.g. every N epochs or if loss improved
        self.checkpoint_manager.save_checkpoint(trainer, epoch, logs)
