"""
Domain policies for defining device targets and precision modes.
"""

from dataclasses import dataclass


@dataclass
class PrecisionPolicy:
    """
    Defines the precision mode used by the training engine.
    Modes: "FP32", "AMP", "BF16"
    """

    mode: str = "FP32"

    def __post_init__(self):
        self.mode = self.mode.upper()
        if self.mode not in {"FP32", "AMP", "BF16"}:
            from packages.training.domain.exceptions import TrainingConfigurationError

            raise TrainingConfigurationError(f"Invalid precision mode: {self.mode}")


@dataclass
class DevicePolicy:
    """
    Defines the device selection logic and fallback order.
    Default order: CUDA -> MPS -> CPU.
    """

    preferred_device: str = "CUDA"
    fallback_order: tuple = ("CUDA", "MPS", "CPU")

    def __post_init__(self):
        self.preferred_device = self.preferred_device.upper()
        if self.preferred_device not in {"CUDA", "MPS", "CPU"}:
            from packages.training.domain.exceptions import TrainingConfigurationError

            raise TrainingConfigurationError(
                f"Invalid preferred device: {self.preferred_device}"
            )
