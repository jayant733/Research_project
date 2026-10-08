"""Privacy primitive tests."""

import numpy as np

from packages.privacy.dp_engine import DPEngine
from packages.privacy.fhe_engine import FHESession
from packages.privacy.secagg_engine import SecAggEngine
from packages.ratc.weights import flatten_weights, unflatten_weights


def test_pairwise_masks_cancel() -> None:
    engine = SecAggEngine("test-secret")
    peers = ["a", "b", "c"]
    shapes = [(2, 2), (3,)]
    masks = [engine.pairwise_masks(peer, peers, 4, shapes) for peer in peers]
    for index in range(len(shapes)):
        total = sum(client[index] for client in masks)
        np.testing.assert_allclose(total, 0.0, atol=1e-8)


def test_dp_noise_changes_update_and_reports_epsilon() -> None:
    engine = DPEngine()
    base = [np.zeros((4,), dtype=np.float32)]
    local = [np.array([0.2, -0.1, 0.05, 0.0], dtype=np.float32)]
    noised, epsilon, update_norm = engine.apply_update_noise(
        base, local, clip_norm=0.1, noise_multiplier=0.8
    )
    assert update_norm > 0
    assert epsilon > 0
    assert not np.allclose(noised[0], local[0])


def test_fhe_weighted_average_roundtrip() -> None:
    session = FHESession()
    first = [np.full((8,), 0.2, dtype=np.float32)]
    second = [np.full((8,), 0.6, dtype=np.float32)]
    flat_first, shapes = flatten_weights(first)
    flat_second, _ = flatten_weights(second)
    aggregated = session.server_engine.aggregate(
        [
            session.client().encrypt(flat_first * 2),
            session.client().encrypt(flat_second * 2),
        ],
        total_samples=4,
    )
    decrypted = session.authority.decrypt(aggregated, flat_first.size)
    restored = unflatten_weights(decrypted, shapes)
    np.testing.assert_allclose(restored[0], 0.4, atol=1e-4)
