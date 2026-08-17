# ADR 0001: Use Flower Framework for Federated Learning Orchestration

## Status
Approved

## Context
The Resource-Aware Tiered Clustering (RATC) project requires a federated learning (FL) framework to coordinate communication and model weight exchanges between a central server and multiple heterogeneous clients. We evaluated options including custom socket wrappers, PySyft, and Flower.

Key criteria for the selection:
1. Support for heterogeneous and resource-constrained edge runtimes.
2. Capability to plug in custom strategies for client selection and tiered aggregation.
3. Clean gRPC socket management.
4. Minimal performance overhead.

## Decision
We decided to adopt the **Flower (flwr)** framework to orchestrate our federated training rounds.

## Consequences
*   **Benefits:**
    *   Provides standardized client/server abstractions (`NumPyClient`, `Strategy`).
    *   Saves development time on custom networking wrappers and socket drop-out handling.
    *   Native gRPC support guarantees efficient serialization and transport of model weights.
*   **Trade-offs:**
    *   Binds client training loops and server strategy hooks to the Flower lifecycle execution order.
    *   Requires wrapping existing client/server parameters to match NumPy array lists.
