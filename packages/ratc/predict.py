"""One-step telemetry extrapolation from the last two observations."""

from typing import Sequence

from packages.telemetry.vectors import TelemetryVector


def predict_telemetry(history: Sequence[TelemetryVector]) -> TelemetryVector:
    """Extend the latest change by one step and clip every coordinate."""
    if not history:
        raise ValueError("Prediction requires at least one telemetry sample.")
    if len(history) == 1:
        return history[-1]
    last = history[-1]
    previous = history[-2]
    return TelemetryVector(
        cpu_usage=_step(last.cpu_usage, previous.cpu_usage),
        memory_usage=_step(last.memory_usage, previous.memory_usage),
        network_bandwidth=_step(last.network_bandwidth, previous.network_bandwidth),
        battery_level=_step(last.battery_level, previous.battery_level),
        disk_io=_step(last.disk_io, previous.disk_io),
    )


def _step(latest: float, previous: float) -> float:
    return float(min(1.0, max(0.0, latest + (latest - previous))))
