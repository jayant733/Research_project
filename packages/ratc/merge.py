"""Pool-level aggregation for plaintext, masked, and encrypted updates."""

import json
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from packages.common.fedavg_aggregator import FedAvgAggregator
from packages.privacy.exceptions import SecAggDropoutError
from packages.privacy.fhe_engine import FHEAuthority, ServerFHEEngine
from packages.privacy.secagg_engine import assert_complete_pool, recover_dropped_mask
from packages.ratc.trust import LOW_TRUST, trust_weight
from packages.ratc.weights import unflatten_weights

Update = Tuple[List[Any], int, Dict[str, Any]]
SKIPPED = {"EXCLUDED", "DROPPED"}


def aggregate_pools(
    updates: Sequence[Update],
    secagg_peers: Sequence[str],
    fhe_engine: ServerFHEEngine | None,
    fhe_authority: FHEAuthority | None,
    trust: Dict[str, float] | None = None,
    notes: Dict[str, Any] | None = None,
) -> Tuple[List[np.ndarray], Dict[str, int]]:
    """Aggregate each privacy pool, then combine pools by sample count."""
    grouped: Dict[str, List[Update]] = {}
    for weights, sample_count, metrics in updates:
        tier = str(metrics.get("tier", "PLAIN"))
        if tier in SKIPPED:
            continue
        grouped.setdefault(tier, []).append((weights, sample_count, metrics))

    pools: List[Tuple[List[np.ndarray], int]] = []
    counts: Dict[str, int] = {}
    for tier, members in grouped.items():
        pooled, sample_count = _aggregate_tier(
            tier, members, secagg_peers, fhe_engine, fhe_authority, trust, notes
        )
        if not pooled or sample_count <= 0:
            continue
        pools.append((pooled, sample_count))
        counts[tier] = len(members)
    if not pools:
        return [], counts
    return FedAvgAggregator().aggregate(pools), counts


def _aggregate_tier(
    tier: str,
    members: Sequence[Update],
    secagg_peers: Sequence[str],
    fhe_engine: ServerFHEEngine | None,
    fhe_authority: FHEAuthority | None,
    trust: Dict[str, float] | None,
    notes: Dict[str, Any] | None,
) -> Tuple[List[np.ndarray], int]:
    if tier == "TIER_1_FHE":
        return _aggregate_fhe(members, fhe_engine, fhe_authority, trust)
    if tier == "TIER_2_SECAGG":
        return _aggregate_secagg(members, secagg_peers, notes)
    return _aggregate_plaintext(members, trust)


def _aggregate_plaintext(
    members: Sequence[Update], trust: Dict[str, float] | None
) -> Tuple[List[np.ndarray], int]:
    fedavg_input = []
    for weights, sample_count, metrics in members:
        client_id = str(metrics.get("client_id", ""))
        multiplier = 1.0 if trust is None else trust_weight(trust.get(client_id, 1.0))
        fedavg_input.append((weights, max(1, int(round(sample_count * multiplier)))))
    sample_count = sum(count for _weights, count in fedavg_input)
    averaged = FedAvgAggregator().aggregate(fedavg_input)
    return [np.asarray(tensor) for tensor in averaged], sample_count


def _aggregate_secagg(
    members: Sequence[Update],
    secagg_peers: Sequence[str],
    notes: Dict[str, Any] | None,
) -> Tuple[List[np.ndarray], int]:
    stripped, share_payloads = _strip_shares(members)
    received = [str(metrics["client_id"]) for _weights, _count, metrics in stripped]
    expected = list(secagg_peers) or received
    if len(received) != len(set(received)):
        raise SecAggDropoutError("Duplicate secure-aggregation client id.")
    extra = _maybe_recover(stripped, share_payloads, expected, received, notes)
    sample_count = sum(count for _weights, count, _metrics in stripped)
    summed = _sum_models(stripped)
    if extra is not None and summed is not None:
        summed = _add(summed, extra)
    if summed is None or sample_count == 0:
        raise SecAggDropoutError("Secure-aggregation pool was empty.")
    averaged = [
        (tensor / float(sample_count)).astype(np.float32) for tensor in summed
    ]
    return averaged, sample_count


def _strip_shares(
    members: Sequence[Update],
) -> Tuple[List[Update], List[Tuple[str, np.ndarray]]]:
    stripped: List[Update] = []
    shares: List[Tuple[str, np.ndarray]] = []
    for weights, sample_count, metrics in members:
        model, recovery = _split_recovery(weights, metrics)
        stripped.append((model, sample_count, metrics))
        if recovery is not None:
            shares.append((str(metrics["client_id"]), recovery))
    return stripped, shares


def _maybe_recover(
    stripped: Sequence[Update],
    share_payloads: Sequence[Tuple[str, np.ndarray]],
    expected: Sequence[str],
    received: Sequence[str],
    notes: Dict[str, Any] | None,
) -> List[np.ndarray] | None:
    missing = sorted(set(expected) - set(received))
    if not missing:
        if notes is not None and notes.get("dropout") is None:
            notes["dropout"] = "none"
        return None
    if not share_payloads:
        assert_complete_pool(expected, received)
    shapes = [tuple(np.asarray(weight).shape) for weight in stripped[0][0]]
    recovered = recover_dropped_mask(share_payloads, missing, expected, shapes)
    if notes is not None:
        notes["dropout"] = "recovered"
        notes["dropped_clients"] = missing
    return recovered


def _sum_models(stripped: Sequence[Update]) -> List[np.ndarray] | None:
    summed = None
    for weights, _count, _metrics in stripped:
        arrays = [np.asarray(weight, dtype=np.float64) for weight in weights]
        summed = arrays if summed is None else _add(summed, arrays)
    return summed


def _aggregate_fhe(
    members: Sequence[Update],
    fhe_engine: ServerFHEEngine | None,
    fhe_authority: FHEAuthority | None,
    trust: Dict[str, float] | None,
) -> Tuple[List[np.ndarray], int]:
    if fhe_engine is None or fhe_authority is None:
        raise RuntimeError("CKKS aggregation was requested without a session.")
    kept = []
    for item in members:
        client_id = str(item[2].get("client_id", ""))
        if trust is not None and trust.get(client_id, 1.0) < LOW_TRUST:
            continue
        kept.append(item)
    if not kept:
        return [], 0
    sample_count = sum(count for _weights, count, _metrics in kept)
    ciphertexts = [
        np.asarray(weights[0], dtype=np.uint8).tobytes() for weights, _c, _m in kept
    ]
    shapes = json.loads(str(kept[0][2]["shapes_json"]))
    length = int(sum(int(np.prod(shape, dtype=int)) for shape in shapes))
    aggregate = fhe_engine.aggregate(ciphertexts, float(sample_count))
    flat = fhe_authority.decrypt(aggregate, length)
    return unflatten_weights(flat, shapes), sample_count


def _split_recovery(
    weights: Sequence[Any], metrics: Dict[str, Any]
) -> Tuple[List[Any], np.ndarray | None]:
    if int(float(metrics.get("has_recovery", 0))) != 1:
        return list(weights), None
    return list(weights[:-1]), np.asarray(weights[-1], dtype=np.int64)


def _add(left: List[np.ndarray], right: List[np.ndarray]) -> List[np.ndarray]:
    if len(left) != len(right):
        raise ValueError("Masked updates have different tensor counts.")
    return [first + second for first, second in zip(left, right)]
