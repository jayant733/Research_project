# ADR 0003: Use Pairwise Masking Secure Aggregation Instead of MPC

## Status
Approved

## Context
Tier 2 nodes (medium resource) require secure model parameter updates without exposing raw weights to the server. While Multi-Party Computation (MPC) schemes (like SPDZ or GC) provide robust security, they introduce high communication round overheads.

Key criteria:
1. Low client-side compute overhead.
2. Capability to handle client dropouts during rounds without failing the aggregation step.
3. Minimal network bandwidth usage.

## Decision
We decided to implement the **Pairwise Masking Secure Aggregation (SecAgg)** protocol (based on Google's SecAgg design) instead of full-circuit MPC.

## Consequences
*   **Benefits:**
    *   Clients only compute additions and lightweight pseudo-random number generator (PRNG) masks.
    *   Maintains the $O(N)$ communication complexity for clients, suitable for edge devices.
    *   Resilient to client dropouts using secret sharing threshold schemes (e.g. Shamir's Secret Sharing) to reconstruct masks for offline clients.
*   **Trade-offs:**
    *   Requires a multi-phase round protocol (Setup, Key Agreement, Masked Input, Unmasking), which increases network round trips compared to simple FedAvg.
