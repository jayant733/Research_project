from typing import Any

from packages.privacy.dp_engine import DPEngine
from packages.privacy.fhe_engine import ClientFHEEngine
from packages.privacy.interfaces import IPrivacyEngine
from packages.privacy.secagg_engine import SecAggEngine


class PrivacyEngine(IPrivacyEngine):
    """Facade for all privacy transformations, dispatching based on tier."""

    def __init__(self, tier_name: str, fhe_poly_modulus_degree: int = 8192):
        self.tier_name = tier_name
        self.fhe_engine = None
        self.dp_engine = None
        self.secagg_engine = None
        
        # Initialize the specific engine based on the assigned tier
        if self.tier_name == "TIER_1_FHE":
            self.fhe_engine = ClientFHEEngine(poly_modulus_degree=fhe_poly_modulus_degree)
        elif self.tier_name == "TIER_2_SECAGG":
            self.secagg_engine = SecAggEngine()
        elif self.tier_name == "TIER_3_DP_PLAIN":
            self.dp_engine = DPEngine()
        else:
            raise ValueError(f"Unknown privacy tier: {self.tier_name}")

    def encrypt_weights(self, weights: Any) -> Any:
        """Encrypts weights if in FHE tier, else returns unchanged."""
        if self.fhe_engine:
            return self.fhe_engine.encrypt_weights(weights)
        return weights

    def decrypt_weights(self, ciphertext: Any, secret_key: Any = None) -> Any:
        """Decrypts weights if in FHE tier."""
        if self.fhe_engine:
            # We assume shape is passed implicitly or managed by the client adapter
            # For simplicity, we just pass None and expect the caller to reshape.
            # In a real system, shape metadata must accompany the ciphertext.
            raise NotImplementedError("Direct decryption via facade requires shape metadata.")
        return ciphertext
        
    def decrypt_weights_with_shape(self, ciphertext: Any, original_shape: tuple) -> Any:
        if self.fhe_engine:
            return self.fhe_engine.decrypt_weights(ciphertext, original_shape)
        return ciphertext

    def apply_dp_noise(self, gradients: Any, epsilon: float, delta: float, max_grad_norm: float) -> Any:
        """Applies DP noise if in DP tier, else returns unchanged."""
        if self.dp_engine:
            return self.dp_engine.apply_dp_noise(gradients, epsilon, delta, max_grad_norm)
        return gradients

    def generate_mask(self, seed: int, shape: tuple) -> Any:
        """Generates a mask if in SecAgg tier."""
        if self.secagg_engine:
            return self.secagg_engine.generate_mask(seed, shape)
        return None
