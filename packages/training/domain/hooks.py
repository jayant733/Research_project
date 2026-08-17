"""
Empty abstract interfaces for future research extensions (Milestone 5+).
Prevents architectural rewrites when introducing external orchestration.
"""

from abc import ABC


class PrivacyEngineHook(ABC):
    """Extension point for Differential Privacy and Secure Aggregation."""

    pass


class SchedulerHook(ABC):
    """Extension point for Resource-Aware Scheduling routing."""

    pass


class FederationHook(ABC):
    """Extension point for Flower Federated Learning integrations."""

    pass


class TelemetryHook(ABC):
    """Extension point for System Telemetry scraping (e.g., Prometheus)."""

    pass
