"""
Factories for initializing common mathematical components.
"""

from typing import Any

from packages.training.domain.config import ExperimentConfig
from packages.training.domain.exceptions import TrainingConfigurationError


class OptimizerFactory:
    """Instantiates the required optimizer based on the experiment configuration."""

    @staticmethod
    def create(params: Any, config: ExperimentConfig) -> Any:
        # Avoid direct import at module level to decouple from PyTorch if possible,
        # but since this factory directly creates torch optimizers, we inject torch locally.
        import torch.optim as optim

        name = config.optimizer.upper()
        kwargs = {"lr": config.learning_rate, "weight_decay": config.weight_decay}

        if name == "SGD":
            kwargs["momentum"] = config.momentum
            return optim.SGD(params, **kwargs)
        elif name == "ADAM":
            return optim.Adam(params, **kwargs)
        elif name == "ADAMW":
            return optim.AdamW(params, **kwargs)
        elif name == "RMSPROP":
            kwargs["momentum"] = config.momentum
            return optim.RMSprop(params, **kwargs)
        else:
            raise TrainingConfigurationError(
                f"Unsupported optimizer: {config.optimizer}"
            )


class LRSchedulerFactory:
    """Instantiates the required learning rate scheduler."""

    @staticmethod
    def create(optimizer: Any, config: ExperimentConfig) -> Any:
        import torch.optim.lr_scheduler as lr_scheduler

        name = config.lr_scheduler.upper()
        if name == "NONE":
            return None
        elif name == "STEPLR":
            return lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
        elif name == "COSINEANNEALINGLR":
            return lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs)
        elif name == "REDUCELRONPLATEAU":
            return lr_scheduler.ReduceLROnPlateau(optimizer, mode="min")
        else:
            raise TrainingConfigurationError(
                f"Unsupported LR scheduler: {config.lr_scheduler}"
            )


class LossFactory:
    """Instantiates the required loss function."""

    @staticmethod
    def create(config: ExperimentConfig) -> Any:
        import torch.nn as nn

        name = config.loss_function.upper()
        if name == "CROSSENTROPY":
            return nn.CrossEntropyLoss()
        elif name == "MSE":
            return nn.MSELoss()
        elif name == "BCEWITHLOGITS":
            return nn.BCEWithLogitsLoss()
        else:
            raise TrainingConfigurationError(
                f"Unsupported loss function: {config.loss_function}"
            )
