"""Seeded client misbehavior used by the experiment scenarios."""

from typing import Dict, List, Sequence

import numpy as np

from packages.ratc.fleet import ClientSpec


def scenario_targets(clients: Sequence[ClientSpec], scenario: str) -> Dict[str, str]:
    """Pick the victim for a scenario. Dropout is chosen after assignment."""
    if scenario in {"", "none", "dropout"}:
        return {}
    ordered = sorted(clients, key=lambda client: client.client_id)

    def first(profile: str) -> str:
        return next(client.client_id for client in ordered if client.profile == profile)

    if scenario == "poison":
        return {first("mobile"): "poison"}
    if scenario == "freerider":
        return {first("iot_device"): "freerider"}
    if scenario == "telemetry":
        return {first("iot_device"): "telemetry"}
    raise ValueError(f"Unknown scenario '{scenario}'.")


def apply_weight_attack(
    global_weights: Sequence[np.ndarray],
    local_weights: Sequence[np.ndarray],
    attack: str,
) -> List[np.ndarray]:
    """Scale an update or replace it with the unchanged global model."""
    if attack == "poison":
        return [
            (
                np.asarray(base, dtype=np.float64)
                + 12.0
                * (
                    np.asarray(updated, dtype=np.float64)
                    - np.asarray(base, dtype=np.float64)
                )
            ).astype(np.float32)
            for base, updated in zip(global_weights, local_weights)
        ]
    if attack == "freerider":
        return [np.array(base, copy=True) for base in global_weights]
    return [np.asarray(weight) for weight in local_weights]
