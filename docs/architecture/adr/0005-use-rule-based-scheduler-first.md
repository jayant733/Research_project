# ADR 0005: Use Rule-Based TOPSIS Scheduler Before RL Policy

## Status
Approved

## Context
The orchestrator must route heterogeneous clients to three separate privacy tiers (FHE, SecAgg, DP) based on incoming resource vectors. While a Reinforcement Learning (RL) agent can learn optimal policies, it requires significant warm-up time, suffers from cold-start instability, and makes debugging early integrations difficult.

Key criteria:
1. Highly predictable and explainable tier routing.
2. Zero bootstrapping latency or training phase requirements.
3. Stable baseline comparison for scientific evaluations.

## Decision
We decided to implement the **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) rule-based scheduler** as the primary default policy, and treat the Reinforcement Learning agent as a pluggable extension.

## Consequences
*   **Benefits:**
    *   Provides deterministic, mathematically explainable routing decisions based on distance metrics to ideal resource targets.
    *   Saves development complexity during early integrations, as there is no state-action-reward network to train or debug.
    *   Serves as a reliable, non-stochastic baseline for performance comparison.
*   **Trade-offs:**
    *   Relies on static weights and thresholds configured in `scheduler.yaml` that do not adapt dynamically to transient network congestion or server load shifts.
