from abc import ABC, abstractmethod
from typing import Dict

from packages.scheduler.types import ConstraintVector, PrivacyTier
from packages.telemetry.vectors import TelemetryVector


class IScheduler(ABC):
    """Abstract interface defining scheduling operations for privacy tier assignment."""

    @abstractmethod
    def evaluate(
        self,
        telemetry: Dict[str, TelemetryVector],
        constraints: Dict[str, ConstraintVector]
    ) -> Dict[str, PrivacyTier]:
        """Evaluates client telemetry and assigns them to privacy tiers."""
        pass
