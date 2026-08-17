"""
Domain-specific custom exceptions for the GPU Training Engine.
These exceptions avoid leaking provider-specific errors into the domain logic.
"""


class DeviceInitializationError(Exception):
    """Raised when the requested device (CUDA, MPS, etc.) cannot be initialized or accessed."""

    pass


class CheckpointError(Exception):
    """Raised when saving, loading, or validating a checkpoint fails."""

    pass


class ModelInitializationError(Exception):
    """Raised when the requested model cannot be instantiated or registered."""

    pass


class TrainingConfigurationError(Exception):
    """Raised when ExperimentConfig parameters are invalid or incompatible."""

    pass


class MixedPrecisionError(Exception):
    """Raised when mixed precision (AMP/BF16) is requested but unsupported or misconfigured."""

    pass
