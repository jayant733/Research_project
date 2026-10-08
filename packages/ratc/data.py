"""Seeded synthetic classification data for the compact demonstration model."""

import hashlib
from typing import Tuple

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from packages.ratc.fleet import ClientSpec, data_shift


def make_loaders(
    spec: ClientSpec,
    seed: int,
    train_size: int = 160,
    test_size: int = 64,
) -> Tuple[DataLoader, DataLoader]:
    """Create a deterministic non-IID train/test pair for one client."""
    train = _dataset(spec, seed, train_size, "train")
    test = _dataset(spec, seed, test_size, "test")
    return (
        DataLoader(train, batch_size=32, shuffle=False),
        DataLoader(test, batch_size=32, shuffle=False),
    )


def _dataset(spec: ClientSpec, seed: int, count: int, split: str) -> TensorDataset:
    digest = hashlib.sha256(f"{seed}|{spec.client_id}|{split}".encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "little"))
    features = rng.normal(0.0, 1.0, size=(count, 8)).astype(np.float32)
    shift = data_shift(spec)
    features[:, 0] += np.float32(shift)
    logits = 1.5 * features[:, 0] - 0.7 * features[:, 1] + (0.25 * shift)
    labels = (logits > 0).astype(np.int64)
    return TensorDataset(torch.from_numpy(features), torch.from_numpy(labels))
