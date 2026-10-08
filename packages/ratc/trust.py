"""Heuristic trust from update size and telemetry agreement."""

from typing import Dict, Mapping

from packages.telemetry.vectors import TelemetryVector

LOW_TRUST = 0.45


def trust_weight(trust: float) -> float:
    """Down-weight a client once trust falls below the routing threshold."""
    if trust < LOW_TRUST:
        return 0.15
    return max(0.15, min(1.0, float(trust)))


def telemetry_gap(expected: TelemetryVector, reported: Mapping[str, float]) -> float:
    keys = ("cpu_usage", "memory_usage", "network_bandwidth", "battery_level")
    total = 0.0
    for key in keys:
        total += abs(float(getattr(expected, key)) - float(reported.get(key, 0.0)))
    return total / len(keys)


def next_trust(
    previous: float,
    update_norm: float,
    median_norm: float,
    telemetry_gap_value: float = 0.0,
) -> tuple[float, str]:
    """Move trust toward the observation and name the anomaly, if any."""
    if telemetry_gap_value > 0.35:
        updated = (0.25 * previous) + (0.75 * 0.2)
        return updated, "telemetry"
    if update_norm < 1e-3:
        updated = (0.25 * previous) + (0.75 * 0.1)
        return updated, "freerider"
    if median_norm > 0 and update_norm > 8.0 * max(median_norm, 1e-6):
        updated = (0.25 * previous) + (0.75 * 0.16)
        return updated, "poison"
    updated = min(1.0, (0.85 * previous) + (0.15 * 0.98))
    return updated, ""


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def initial_trust(client_ids: list[str]) -> Dict[str, float]:
    return {client_id: 1.0 for client_id in client_ids}
