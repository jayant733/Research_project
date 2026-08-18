import hashlib
from typing import Any

import numpy as np


class SecAggEngine:
    """Secure Aggregation engine utilizing additive masking."""

    def __init__(self):
        pass

    def generate_mask(self, seed: int, shape: tuple) -> np.ndarray:
        """Generates a pseudo-random mask based on a seed.
        
        Args:
            seed: The shared secret seed.
            shape: The shape of the mask to generate.
            
        Returns:
            A numpy array containing the mask.
        """
        # Create a deterministic PRNG based on the seed
        # Use hashlib to create a strong 32-bit integer seed from the input
        seed_bytes = str(seed).encode('utf-8')
        hash_digest = hashlib.sha256(seed_bytes).digest()
        int_seed = int.from_bytes(hash_digest[:4], byteorder='little')
        
        rng = np.random.RandomState(int_seed)
        
        # Generate uniform noise centered at 0
        mask = rng.uniform(low=-1.0, high=1.0, size=shape)
        return mask.astype(np.float32)
        
    def apply_mask(self, weights: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Applies an additive mask to the weights."""
        if weights.shape != mask.shape:
            raise ValueError(f"Shape mismatch: weights {weights.shape} != mask {mask.shape}")
        return weights + mask
        
    def remove_mask(self, masked_weights: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Removes an additive mask from the weights."""
        if masked_weights.shape != mask.shape:
            raise ValueError(f"Shape mismatch: masked_weights {masked_weights.shape} != mask {mask.shape}")
        return masked_weights - mask
