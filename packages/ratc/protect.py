"""Apply the tier selected by the server to a freshly trained model."""

import json
import time
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from packages.privacy.dp_engine import DPEngine
from packages.privacy.fhe_engine import PublicFHEClient
from packages.privacy.secagg_engine import SecAggEngine, build_recovery_shares
from packages.ratc.weights import flatten_weights

DP_CLIP_NORM = 0.1
DP_NOISE_MULTIPLIER = 0.5
DP_DELTA = 1e-5


def protect_update(
    global_weights: Sequence[np.ndarray],
    local_weights: Sequence[np.ndarray],
    tier: str,
    client_id: str,
    round_index: int,
    sample_count: int,
    secagg_peers: Sequence[str],
    secagg_secret: str,
    fhe_client: PublicFHEClient | None,
    dp_engine: DPEngine,
    noise_multiplier: float | None = None,
    recovery: bool = False,
) -> Tuple[List[Any], Dict[str, Any]]:
    """Return the wire payload and scalar metrics for one client update."""
    started = time.perf_counter()
    metrics: Dict[str, Any] = {
        "client_id": client_id,
        "tier": tier,
        "epsilon": 0.0,
        "delta": DP_DELTA,
        "update_norm": _update_norm(global_weights, local_weights),
        "has_recovery": 0,
    }
    if tier in {"EXCLUDED", "DROPPED"}:
        payload = [np.asarray(weight, dtype=np.float32) for weight in global_weights]
    elif tier == "TIER_1_FHE":
        payload = _encrypt(local_weights, sample_count, fhe_client)
    elif tier == "TIER_2_SECAGG":
        engine = SecAggEngine(secagg_secret)
        payload = engine.mask_weights(
            local_weights, client_id, secagg_peers, round_index, sample_count
        )
        if recovery:
            payload = [
                *payload,
                build_recovery_shares(engine, client_id, secagg_peers, round_index),
            ]
            metrics["has_recovery"] = 1
    elif tier == "TIER_3_DP_PLAIN":
        payload, epsilon, _update_norm_after_clip = dp_engine.apply_update_noise(
            global_weights,
            local_weights,
            clip_norm=DP_CLIP_NORM,
            noise_multiplier=(
                DP_NOISE_MULTIPLIER if noise_multiplier is None else noise_multiplier
            ),
            delta=DP_DELTA,
        )
        metrics["epsilon"] = float(epsilon)
    else:
        payload = [np.asarray(weight, dtype=np.float32) for weight in local_weights]
        metrics["tier"] = "PLAIN"

    metrics["privacy_seconds"] = float(time.perf_counter() - started)
    metrics["payload_bytes"] = int(sum(np.asarray(part).nbytes for part in payload))
    metrics["shapes_json"] = json.dumps(
        [list(np.asarray(weight).shape) for weight in local_weights]
    )
    return payload, _scalars(metrics)


def _encrypt(
    local_weights: Sequence[np.ndarray],
    sample_count: int,
    fhe_client: PublicFHEClient | None,
) -> List[np.ndarray]:
    if fhe_client is None:
        raise RuntimeError("CKKS public context was not distributed to this client.")
    flat, _shapes = flatten_weights(local_weights)
    ciphertext = fhe_client.encrypt(flat * float(sample_count))
    return [np.frombuffer(ciphertext, dtype=np.uint8).copy()]


def _update_norm(
    global_weights: Sequence[np.ndarray], local_weights: Sequence[np.ndarray]
) -> float:
    if len(global_weights) != len(local_weights):
        return 0.0
    total = 0.0
    for base, updated in zip(global_weights, local_weights):
        updated_array = np.asarray(updated, dtype=np.float64)
        base_array = np.asarray(base, dtype=np.float64)
        delta = updated_array - base_array
        total += float(np.dot(delta.ravel(), delta.ravel()))
    return float(np.sqrt(total))


def _scalars(metrics: Dict[str, Any]) -> Dict[str, Any]:
    clean: Dict[str, Any] = {}
    for key, value in metrics.items():
        if isinstance(value, (np.floating, float)):
            clean[key] = float(value)
        elif isinstance(value, (np.integer, int)):
            clean[key] = int(value)
        else:
            clean[key] = str(value)
    return clean
