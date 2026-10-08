"""Flatten and restore model tensors for privacy transforms."""

from typing import List, Sequence, Tuple

import numpy as np


def flatten_weights(
    weights: Sequence[np.ndarray],
) -> Tuple[np.ndarray, List[List[int]]]:
    """Return one float64 vector and the original tensor shapes."""
    shapes = [list(weight.shape) for weight in weights]
    if not weights:
        return np.zeros((0,), dtype=np.float64), shapes
    flat = np.concatenate(
        [np.asarray(weight, dtype=np.float64).ravel() for weight in weights]
    )
    return flat, shapes


def unflatten_weights(
    flat: np.ndarray, shapes: Sequence[Sequence[int]]
) -> List[np.ndarray]:
    """Restore float32 tensors from a flat vector."""
    restored: List[np.ndarray] = []
    cursor = 0
    vector = np.asarray(flat, dtype=np.float64).ravel()
    for shape in shapes:
        size = int(np.prod(shape, dtype=int))
        chunk = vector[cursor : cursor + size]
        if chunk.size != size:
            raise ValueError("Flat vector does not match the recorded tensor shapes.")
        restored.append(chunk.reshape(tuple(shape)).astype(np.float32))
        cursor += size
    return restored


def scale_weights(weights: Sequence[np.ndarray], factor: float) -> List[np.ndarray]:
    """Multiply every tensor by a scalar."""
    return [
        (np.asarray(weight, dtype=np.float64) * factor).astype(np.float32)
        for weight in weights
    ]


def add_weights(
    left: Sequence[np.ndarray], right: Sequence[np.ndarray]
) -> List[np.ndarray]:
    """Add two equal-shaped weight lists."""
    if len(left) != len(right):
        raise ValueError("Weight lists have different lengths.")
    summed: List[np.ndarray] = []
    for first, second in zip(left, right):
        if tuple(first.shape) != tuple(second.shape):
            raise ValueError("Weight tensor shapes do not match.")
        summed.append(
            (
                np.asarray(first, dtype=np.float64)
                + np.asarray(second, dtype=np.float64)
            ).astype(np.float32)
        )
    return summed
