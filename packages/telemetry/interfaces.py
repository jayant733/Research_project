from abc import ABC, abstractmethod


class ITelemetryProvider(ABC):
    """Abstract interface defining operations for hardware metrics harvesting."""

    @abstractmethod
    def harvest_metrics(self) -> 'TelemetryVector':
        """Harvests hardware metrics into a normalized vector."""
        pass

    @abstractmethod
    def get_battery_status(self) -> float:
        """Returns the remaining battery capacity scaled between 0.0 and 1.0."""
        pass
