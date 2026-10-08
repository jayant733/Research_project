"""Deterministic heterogeneous client fleet and telemetry."""

import hashlib
from dataclasses import dataclass
from typing import Dict, Mapping

import numpy as np

from packages.telemetry.vectors import TelemetryVector

PROFILE_LABELS = {
    "workstation": "Workstation",
    "mobile": "Mobile",
    "iot_device": "IoT",
    "Desktop": "Workstation",
    "Mobile": "Mobile",
    "IoT": "IoT",
}

PROFILE_BASE = {
    "workstation": {
        "cpu_usage": 0.12,
        "memory_usage": 0.22,
        "network_bandwidth": 0.95,
        "battery_level": 1.0,
        "disk_io": 0.15,
        "shift": 0.35,
    },
    "mobile": {
        "cpu_usage": 0.48,
        "memory_usage": 0.55,
        "network_bandwidth": 0.50,
        "battery_level": 0.66,
        "disk_io": 0.28,
        "shift": 0.0,
    },
    "iot_device": {
        "cpu_usage": 0.84,
        "memory_usage": 0.80,
        "network_bandwidth": 0.16,
        "battery_level": 0.24,
        "disk_io": 0.45,
        "shift": -0.35,
    },
}


def canonical_profile(profile: str) -> str:
    """Map dashboard aliases onto the scheduler profile names."""
    if profile in PROFILE_BASE:
        return profile
    label_map = {"Desktop": "workstation", "Mobile": "mobile", "IoT": "iot_device"}
    if profile not in label_map:
        raise ValueError(f"Unknown client profile: {profile}")
    return label_map[profile]


@dataclass(frozen=True)
class ClientSpec:
    """One simulated participant."""

    client_id: str
    profile: str
    sensitivity: float

    def canonical(self) -> "ClientSpec":
        return ClientSpec(
            self.client_id, canonical_profile(self.profile), float(self.sensitivity)
        )


def default_fleet() -> list[ClientSpec]:
    """Six clients spanning the three resource classes."""
    return [
        ClientSpec("ws-1", "workstation", 0.86),
        ClientSpec("ws-2", "workstation", 0.74),
        ClientSpec("mob-1", "mobile", 0.57),
        ClientSpec("mob-2", "mobile", 0.46),
        ClientSpec("iot-1", "iot_device", 0.30),
        ClientSpec("iot-2", "iot_device", 0.16),
    ]


def _stable_jitter(seed: int, client_id: str, round_index: int) -> np.ndarray:
    digest = hashlib.sha256(
        f"{seed}|{client_id}|{round_index}".encode("utf-8")
    ).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "little"))
    return rng.uniform(-0.015, 0.015, size=4)


def _clip(value: float) -> float:
    return float(min(1.0, max(0.0, value)))


def telemetry_for(
    spec: ClientSpec,
    round_index: int,
    seed: int,
    measured_fit_seconds: float | None = None,
) -> TelemetryVector:
    """Build scheduler telemetry from the device profile and optional measured time."""
    profile = canonical_profile(spec.profile)
    base = PROFILE_BASE[profile]
    jitter = _stable_jitter(seed, spec.client_id, round_index)
    progress = max(0, round_index - 1)
    cpu_usage = float(base["cpu_usage"]) + 0.012 * progress + float(jitter[0])
    if measured_fit_seconds is not None:
        measured_pressure = min(1.0, measured_fit_seconds / 3.0)
        cpu_usage = (0.8 * cpu_usage) + (0.2 * measured_pressure)
    battery = float(base["battery_level"]) + float(jitter[3])
    if profile != "workstation":
        battery -= 0.045 * progress
    return TelemetryVector(
        cpu_usage=_clip(cpu_usage),
        memory_usage=_clip(float(base["memory_usage"]) + float(jitter[1])),
        network_bandwidth=_clip(float(base["network_bandwidth"]) + float(jitter[2])),
        battery_level=_clip(battery),
        disk_io=_clip(float(base["disk_io"])),
    )


def data_shift(spec: ClientSpec) -> float:
    """Return the client's label-generating feature shift."""
    return float(PROFILE_BASE[canonical_profile(spec.profile)]["shift"])


def display_profile(profile: str) -> str:
    """Return the label shown in the dashboard."""
    canonical = canonical_profile(profile)
    return PROFILE_LABELS[canonical]


def fleet_by_id(clients: list[ClientSpec]) -> Dict[str, ClientSpec]:
    return {client.client_id: client.canonical() for client in clients}


def sensitivity_map(clients: Mapping[str, ClientSpec]) -> Dict[str, float]:
    return {client_id: client.sensitivity for client_id, client in clients.items()}
