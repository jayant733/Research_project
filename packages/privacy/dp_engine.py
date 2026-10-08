"""Clip model updates and account for Gaussian noise with Opacus."""

import math
from typing import List, Sequence, Tuple

import numpy as np
from opacus.accountants import RDPAccountant

from packages.ratc.weights import unflatten_weights


class DPEngine:
    """Applies the Gaussian mechanism to a model update and tracks epsilon."""

    def __init__(self) -> None:
        self.accountant = RDPAccountant()
        self.rounds = 0

    def apply_update_noise(
        self,
        global_weights: Sequence[np.ndarray],
        local_weights: Sequence[np.ndarray],
        clip_norm: float = 0.1,
        noise_multiplier: float = 0.5,
        delta: float = 1e-5,
        sample_rate: float = 1.0,
    ) -> Tuple[List[np.ndarray], float, float]:
        """Return a noised model, the composed epsilon, and the update norm."""
        delta_flat, shapes = _delta_flat(global_weights, local_weights)
        update_norm = float(np.linalg.norm(delta_flat))
        clip_scale = min(1.0, float(clip_norm) / (update_norm + 1e-12))
        clipped = delta_flat * clip_scale
        noise = np.random.normal(0.0, noise_multiplier * clip_norm, size=clipped.shape)
        noisy_delta = clipped + noise
        restored = unflatten_weights(noisy_delta, shapes)
        noised_weights = [
            (
                np.asarray(base, dtype=np.float64) + np.asarray(delta, dtype=np.float64)
            ).astype(np.float32)
            for base, delta in zip(global_weights, restored)
        ]
        self.accountant.step(
            noise_multiplier=float(noise_multiplier), sample_rate=float(sample_rate)
        )
        self.rounds += 1
        epsilon = float(self.accountant.get_epsilon(delta=float(delta)))
        return noised_weights, epsilon, update_norm

    def apply_dp_noise(
        self,
        gradients: np.ndarray,
        epsilon: float,
        delta: float,
        max_grad_norm: float,
    ) -> np.ndarray:
        """Clip one vector and add Gaussian noise calibrated to a target epsilon."""
        vector = np.asarray(gradients, dtype=np.float64)
        norm = float(np.linalg.norm(vector))
        scale = min(1.0, max_grad_norm / (norm + 1e-12))
        clipped = vector * scale
        sigma = max_grad_norm * math.sqrt(2.0 * math.log(1.25 / delta)) / epsilon
        return (clipped + np.random.normal(0.0, sigma, size=clipped.shape)).astype(
            np.float32
        )


def _delta_flat(
    global_weights: Sequence[np.ndarray], local_weights: Sequence[np.ndarray]
) -> Tuple[np.ndarray, List[List[int]]]:
    if len(global_weights) != len(local_weights):
        raise ValueError("Global and local models have different tensor counts.")
    pieces: List[np.ndarray] = []
    shapes: List[List[int]] = []
    for base, updated in zip(global_weights, local_weights):
        if tuple(base.shape) != tuple(updated.shape):
            raise ValueError("Global and local tensor shapes differ.")
        pieces.append(
            np.asarray(updated, dtype=np.float64).ravel()
            - np.asarray(base, dtype=np.float64).ravel()
        )
        shapes.append(list(base.shape))
    if not pieces:
        return np.zeros((0,), dtype=np.float64), shapes
    return np.concatenate(pieces), shapes
