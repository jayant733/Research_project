"""
Reusable dataset generator for integration testing independent of real data.
"""

from typing import Any


class SyntheticDatasetGenerator:
    """Generates synthetic datasets for tests to maintain reproducibility."""

    @staticmethod
    def create_classification_dataset(
        samples: int = 1000, features: int = 20, classes: int = 2, seed: int = 42
    ) -> Any:
        import torch
        from torch.utils.data import TensorDataset

        torch.manual_seed(seed)
        X = torch.randn(samples, features)
        y = torch.randint(0, classes, (samples,))
        return TensorDataset(X, y)

    @staticmethod
    def create_regression_dataset(
        samples: int = 1000, features: int = 20, seed: int = 42
    ) -> Any:
        import torch
        from torch.utils.data import TensorDataset

        torch.manual_seed(seed)
        X = torch.randn(samples, features)
        # Linear relation with noise
        weights = torch.randn(features, 1)
        y = X.mm(weights) + torch.randn(samples, 1) * 0.1
        return TensorDataset(X, y)
