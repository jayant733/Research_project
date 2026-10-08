"""Demonstrator pairwise masking. Masks cancel only when the full pool reports."""

import hashlib
from typing import Sequence

import numpy as np

from packages.privacy.exceptions import SecAggDropoutError
from packages.privacy.shamir import (
    join_seed,
    reconstruct_secret,
    share_secret,
    split_seed,
)


class SecAggEngine:
    """Builds pairwise additive masks from a client-held round secret."""

    def __init__(self, secret: str = "ratc-demonstrator-client-secret") -> None:
        self.secret = secret

    def generate_mask(self, seed: int, shape: tuple) -> np.ndarray:
        """Legacy single-seed mask retained for the privacy facade."""
        rng = np.random.default_rng(int(seed) % (2**32))
        return rng.uniform(-1.0, 1.0, size=shape).astype(np.float32)

    def pairwise_masks(
        self,
        client_id: str,
        peers: Sequence[str],
        round_index: int,
        shapes: Sequence[tuple],
    ) -> list[np.ndarray]:
        """Return masks that sum to zero across the complete peer set."""
        masks = [np.zeros(shape, dtype=np.float64) for shape in shapes]
        for peer in peers:
            if peer == client_id:
                continue
            sign = 1.0 if client_id < peer else -1.0
            masks = _accumulate_pair(
                masks, sign, self._pair_seed(round_index, client_id, peer), shapes
            )
        return masks

    def mask_weights(
        self,
        weights: Sequence[np.ndarray],
        client_id: str,
        peers: Sequence[str],
        round_index: int,
        sample_count: int,
    ) -> list[np.ndarray]:
        """Mask sample-scaled weights so the server sum reveals only the total."""
        shapes = [tuple(weight.shape) for weight in weights]
        masks = self.pairwise_masks(client_id, peers, round_index, shapes)
        masked: list[np.ndarray] = []
        for weight, mask in zip(weights, masks):
            scaled = np.asarray(weight, dtype=np.float64) * float(sample_count)
            masked.append((scaled + mask).astype(np.float32))
        return masked

    def _pair_seed(self, round_index: int, left: str, right: str) -> int:
        low, high = sorted((left, right))
        digest = hashlib.sha256(
            f"{self.secret}|{round_index}|{low}|{high}".encode("utf-8")
        ).digest()
        return int.from_bytes(digest[:8], "little")


def _accumulate_pair(
    masks: list[np.ndarray], sign: float, seed: int, shapes: Sequence[tuple]
) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    updated: list[np.ndarray] = []
    for mask, shape in zip(masks, shapes):
        draw = rng.standard_normal(shape)
        updated.append(mask + (sign * draw))
    return updated


def build_recovery_shares(
    engine: "SecAggEngine",
    client_id: str,
    peers: Sequence[str],
    round_index: int,
) -> np.ndarray:
    """Share every pair seed this client knows. The server can rebuild one dropout."""
    ordered = list(peers)
    lookup = {peer: index + 1 for index, peer in enumerate(ordered)}
    xs = list(lookup.values())
    values: list[int] = []
    for peer in ordered:
        if peer == client_id:
            continue
        seed = engine._pair_seed(round_index, client_id, peer)
        low, high = sorted((client_id, peer))
        for limb, part in enumerate(split_seed(seed)):
            shares = share_secret(
                part,
                2,
                xs,
                _share_coefficients(engine.secret, round_index, low, high, limb),
            )
            for x_value, y_value in shares:
                values.extend(
                    [lookup[low], lookup[high], limb, x_value, y_value]
                )
    if not values:
        values = [0, 0, 0, 0, 0]
    return np.asarray(values, dtype=np.int64)


def recover_dropped_mask(
    payloads: Sequence[tuple[str, np.ndarray]],
    missing: Sequence[str],
    peers: Sequence[str],
    shapes: Sequence[tuple],
) -> list[np.ndarray]:
    """Rebuild the masks of missing clients from survivor shares."""
    ordered = list(peers)
    present = {client_id for client_id, _shares in payloads}
    masks = [np.zeros(shape, dtype=np.float64) for shape in shapes]
    for client_id in missing:
        for peer in ordered:
            if peer == client_id:
                continue
            if peer not in present or client_id not in ordered:
                raise SecAggDropoutError(
                    "Mask recovery needs a surviving endpoint for every dropped pair. "
                    f"Missing pair: {client_id}, {peer}."
                )
            seed = _seed_from_uploader(payloads, ordered, client_id, peer)
            sign = 1.0 if client_id < peer else -1.0
            masks = _accumulate_pair(masks, sign, seed, shapes)
    return masks


def _share_coefficients(
    secret: str, round_index: int, low: str, high: str, limb: int
) -> list[int]:
    digest = hashlib.sha256(
        f"{secret}|share|{round_index}|{low}|{high}|{limb}".encode("utf-8")
    ).digest()
    return [int.from_bytes(digest[:8], "little")]


def _seed_from_uploader(
    payloads: Sequence[tuple[str, np.ndarray]],
    peers: Sequence[str],
    left: str,
    right: str,
) -> int:
    low, high = sorted((left, right))
    lookup = {peer: index + 1 for index, peer in enumerate(peers)}
    low_index = lookup[low]
    high_index = lookup[high]
    for uploader, vector in payloads:
        if uploader not in {low, high}:
            continue
        limbs = _limbs_for_pair(vector, low_index, high_index)
        if all(len(limbs[limb]) >= 2 for limb in (0, 1)):
            parts = [
                reconstruct_secret(limbs[limb][:2]) for limb in (0, 1)
            ]
            return join_seed(parts[0], parts[1])
    raise SecAggDropoutError(
        f"Not enough mask shares to recover the pair {low}, {high}."
    )


def _limbs_for_pair(
    vector: np.ndarray, low_index: int, high_index: int
) -> dict[int, list[tuple[int, int]]]:
    values = np.asarray(vector, dtype=np.int64).reshape(-1, 5)
    limbs: dict[int, list[tuple[int, int]]] = {0: [], 1: []}
    seen: set[tuple[int, int]] = set()
    for low_i, high_i, limb, x_value, y_value in values:
        if int(low_i) != low_index or int(high_i) != high_index:
            continue
        point = (int(limb), int(x_value))
        if point in seen:
            continue
        seen.add(point)
        limbs[int(limb)].append((int(x_value), int(y_value)))
    return limbs


def assert_complete_pool(expected: Sequence[str], received: Sequence[str]) -> None:
    """Fail closed when a masked update is missing."""
    missing = sorted(set(expected) - set(received))
    if missing:
        raise SecAggDropoutError(
            "Demonstrator secure aggregation cannot drop clients. Missing: "
            + ", ".join(missing)
        )
