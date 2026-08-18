from typing import Any

import torch
from opacus.accountants import RDPAccountant


class DPEngine:
    """Differential Privacy engine using Opacus principles."""

    def __init__(self):
        self.accountant = RDPAccountant()

    def apply_dp_noise(self, gradients: torch.Tensor, epsilon: float, delta: float, max_grad_norm: float) -> torch.Tensor:
        """Applies Gaussian noise to gradients for differential privacy.
        
        Args:
            gradients: The gradients to add noise to.
            epsilon: The privacy budget epsilon.
            delta: The privacy budget delta.
            max_grad_norm: The maximum L2 norm of the gradients.
            
        Returns:
            The noisy gradients.
        """
        # 1. Clip gradients
        grad_norm = torch.norm(gradients, p=2)
        clip_coef = max_grad_norm / (grad_norm + 1e-6)
        clip_coef_clamped = torch.clamp(clip_coef, max=1.0)
        clipped_gradients = gradients * clip_coef_clamped

        # 2. Add Gaussian noise
        # In a real Opacus setup, noise_multiplier is derived from epsilon, delta, and steps.
        # For this simplified engine, we use a heuristic noise multiplier.
        # noise_multiplier = sqrt(2 * log(1.25 / delta)) / epsilon
        import math
        noise_multiplier = math.sqrt(2 * math.log(1.25 / delta)) / epsilon
        
        noise = torch.normal(
            mean=0.0,
            std=noise_multiplier * max_grad_norm,
            size=clipped_gradients.size(),
            device=clipped_gradients.device,
            dtype=clipped_gradients.dtype
        )
        
        noisy_gradients = clipped_gradients + noise
        
        # In a full Opacus integration, we'd step the accountant here.
        # self.accountant.step(noise_multiplier=noise_multiplier, sample_rate=...)
        
        return noisy_gradients
