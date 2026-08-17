# ADR 0002: Use Opacus for Local Differential Privacy

## Status
Approved

## Context
For Tier 3 (resource-constrained edge nodes), we must apply Local Differential Privacy (LDP) to prevent information leakage through local model updates. This requires bounding gradients and injecting calibrated noise.

Key criteria:
1. Native integration with PyTorch models and optimizers.
2. Mathematically verified privacy budgeting ($\epsilon$, $\delta$ accountant).
3. Optimized execution speeds for gradient clipping on edge CPU/GPU resources.

## Decision
We decided to adopt the **Opacus** library (developed by Meta) to enforce Local Differential Privacy inside `ITrainingEngine`.

## Consequences
*   **Benefits:**
    *   Integrates directly with PyTorch's optimizer hooks via a wrapper class (`PrivacyEngine`).
    *   Includes a mathematically rigorous Renyi Differential Privacy (RDP) accountant.
    *   Handles batch-level gradient clipping efficiently.
*   **Trade-offs:**
    *   Adds slight memory overhead during backward passes due to per-sample gradient tracking.
    *   Requires wrapping standard PyTorch DataLoader datasets to prevent batches from leaking privacy dimensions.
