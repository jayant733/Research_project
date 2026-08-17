"""
Domain configuration structures for experiments.
"""

from dataclasses import dataclass, field
from typing import Optional

from packages.training.domain.policies import DevicePolicy, PrecisionPolicy


@dataclass
class ExperimentConfig:
    """Strongly typed configuration avoiding magic numbers."""

    batch_size: int
    epochs: int
    learning_rate: float
    optimizer: str = "Adam"
    momentum: float = 0.0
    weight_decay: float = 0.0
    loss_function: str = "CrossEntropy"
    lr_scheduler: str = "None"
    precision: PrecisionPolicy = field(default_factory=PrecisionPolicy)
    device: DevicePolicy = field(default_factory=DevicePolicy)
    random_seed: Optional[int] = 42
    checkpoint_directory: str = "./checkpoints"
