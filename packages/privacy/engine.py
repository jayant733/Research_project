"""Facade that selects a privacy backend for a named tier."""

from typing import Any, Optional

import numpy as np

from packages.privacy.dp_engine import DPEngine
from packages.privacy.fhe_engine import ClientFHEEngine
from packages.privacy.interfaces import IPrivacyEngine
from packages.privacy.secagg_engine import SecAggEngine


class PrivacyEngine(IPrivacyEngine):
    """Dispatch helper retained for single-tier client construction."""

    def __init__(self, tier_name: str, fhe_poly_modulus_degree: int = 8192) -> None:
        self.tier_name = tier_name
        self.fhe_engine: Optional[ClientFHEEngine] = None
        self.dp_engine: Optional[DPEngine] = None
        self.secagg_engine: Optional[SecAggEngine] = None
        if self.tier_name == "TIER_1_FHE":
            self.fhe_engine = ClientFHEEngine(
                poly_modulus_degree=fhe_poly_modulus_degree
            )
        elif self.tier_name == "TIER_2_SECAGG":
            self.secagg_engine = SecAggEngine()
        elif self.tier_name == "TIER_3_DP_PLAIN":
            self.dp_engine = DPEngine()
        else:
            raise ValueError(f"Unknown privacy tier: {self.tier_name}")

    def encrypt_weights(self, weights: Any) -> Any:
        if self.fhe_engine is not None:
            return self.fhe_engine.encrypt_weights(np.asarray(weights))
        return weights

    def decrypt_weights(self, ciphertext: Any, secret_key: Any = None) -> Any:
        del secret_key
        if self.fhe_engine is None:
            return ciphertext
        raise NotImplementedError(
            "Pass the original shape to decrypt_weights_with_shape."
        )

    def decrypt_weights_with_shape(self, ciphertext: Any, original_shape: tuple) -> Any:
        if self.fhe_engine is not None:
            return self.fhe_engine.decrypt_weights(ciphertext, original_shape)
        return ciphertext

    def apply_dp_noise(
        self, gradients: Any, epsilon: float, delta: float, max_grad_norm: float
    ) -> Any:
        if self.dp_engine is not None:
            return self.dp_engine.apply_dp_noise(
                np.asarray(gradients), epsilon, delta, max_grad_norm
            )
        return gradients

    def generate_mask(self, seed: int, shape: tuple) -> Any:
        if self.secagg_engine is not None:
            return self.secagg_engine.generate_mask(seed, shape)
        return None
