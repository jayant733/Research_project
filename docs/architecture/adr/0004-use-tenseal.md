# ADR 0004: Use TenSEAL for Fully Homomorphic Encryption

## Status
Approved

## Context
Tier 1 (high resource) nodes require Fully Homomorphic Encryption (FHE) using the CKKS scheme to allow the server to aggregate model weights in an encrypted state. We evaluated SEAL wrappers, Pyfhel, and TenSEAL.

Key criteria:
1. Support for CKKS tensor operations (vector/matrix additions and multiplications).
2. Clean Python API backed by high-performance C++ bindings.
3. Thread-safe execution.

## Decision
We decided to adopt the **TenSEAL** library (developed by OpenMined) to implement homomorphic encryption in `IPrivacyEngine` and `IAggregator`.

## Consequences
*   **Benefits:**
    *   Exposes clean APIs to encrypt and aggregate PyTorch-style tensors directly (`bfv_vector`, `ckks_tensor`).
    *   Backed by Microsoft SEAL, ensuring a highly optimized, audited cryptographic backend.
    *   Maintains compatibility with NumPy and PyTorch paradigms.
*   **Trade-offs:**
    *   Brings a large compiled binary footprint due to C++ compilation targets.
    *   FHE parameters (polynomial modulus degree, scale) must be calibrated carefully to prevent noise budgets from overflow.
