from abc import ABC, abstractmethod
from typing import Any


class IPrivacyEngine(ABC):
    """Abstract interface defining standard operations for privacy transformations."""

    @abstractmethod
    def encrypt_weights(self, weights: Any) -> Any:
        """Homomorphically encrypts model weights."""
        pass

    @abstractmethod
    def decrypt_weights(self, ciphertext: Any, secret_key: Any) -> Any:
        """Decrypts homomorphically encrypted weights."""
        pass

    @abstractmethod
    def apply_dp_noise(self, gradients: Any, epsilon: float, delta: float, max_grad_norm: float) -> Any:
        """Applies differential privacy noise to gradients."""
        pass

    @abstractmethod
    def generate_mask(self, seed: int, shape: tuple) -> Any:
        """Generates a pseudo-random mask for Secure Aggregation."""
        pass
