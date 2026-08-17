"""
Domain-specific metadata structures tracking experimental execution contexts.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExperimentMetadata:
    """Tracks environmental execution context for reproducibility."""

    experiment_id: str
    timestamp: str
    git_commit: Optional[str]
    hostname: str
    operating_system: str
    python_version: str
    torch_version: Optional[str]
    cuda_version: Optional[str]
