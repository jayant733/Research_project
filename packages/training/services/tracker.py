"""
Local experiment tracking managing timestamps and configurations.
"""

import platform
import sys
import time
import uuid
from typing import Optional

from packages.training.domain.config import ExperimentConfig
from packages.training.domain.metadata import ExperimentMetadata


class ExperimentTracker:
    """Manages the experiment lifecycle."""

    def __init__(self):
        self.metadata: Optional[ExperimentMetadata] = None
        self.config_snapshot: Optional[ExperimentConfig] = None
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def start_experiment(self, config: ExperimentConfig) -> None:
        self.start_time = time.time()
        self.config_snapshot = config

        # PyTorch might not be installed in the domain layer,
        # but we can try to fetch its version gracefully.
        torch_version = None
        cuda_version = None
        try:
            import torch

            torch_version = torch.__version__
            if torch.cuda.is_available():
                cuda_version = torch.version.cuda
        except ImportError:
            pass

        self.metadata = ExperimentMetadata(
            experiment_id=str(uuid.uuid4()),
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            git_commit=None,  # would run subprocess for git rev-parse HEAD
            hostname=platform.node(),
            operating_system=platform.platform(),
            python_version=sys.version.split(" ")[0],
            torch_version=torch_version,
            cuda_version=cuda_version,
        )

    def end_experiment(self) -> None:
        self.end_time = time.time()

    @property
    def duration(self) -> float:
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.time() - self.start_time
