"""
Seed manager for reproducibility across random, numpy, and torch.
"""

import random


class SeedManager:
    """Ensures deterministic execution across various libraries."""

    @staticmethod
    def set_seed(seed: int) -> None:
        random.seed(seed)
        try:
            import numpy as np

            np.random.seed(seed)
        except ImportError:
            pass

        try:
            import torch

            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)
                # Enforce deterministic convolutions
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False
        except ImportError:
            pass
