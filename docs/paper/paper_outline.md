# IEEE Paper Outline

Implementation status: the repository now runs a local Flower demonstrator with TOPSIS tier assignment, CKKS pool aggregation, demonstrator pairwise masking, and accounted local DP. Do not cite numeric speedups from this outline unless they were produced by `scripts/run_experiment.py`. Secure aggregation is not the production Bonawitz protocol. See `docs/design/threat_model.md`.

This document establishes the structural outline for the academic paper presenting the Resource-Aware Tiered Clustering (RATC) framework, formatted in accordance with IEEE Transactions style guidelines.

---

## I. Title Proposal
*   **Target Title:** *Resource-Aware Tiered Clustering for Heterogeneous Privacy-Preserving Federated Learning*
*   **Target Journal:** *IEEE Transactions on Parallel and Distributed Systems* or *IEEE Transactions on Mobile Computing*.

---

## II. Paper Sections

### Abstract
*   Contextualizes the growth of heterogeneous federated learning networks.
*   Highlights the limitations of uniform privacy configurations (e.g. forcing heavy FHE calculations on IoT nodes).
*   Introduces the RATC framework: Dynamic telemetry profiling linked to multi-pool strategies (FHE, SecAgg, DP).
*   Summarizes the core results (e.g., convergence improvements, bandwidth savings, and energy reductions).

### 1. Introduction
*   **Background:** Federated Learning (FL) as a privacy-preserving paradigm.
*   **Problem Statement:** Heterogeneity in edge-device resources (CPU, RAM, battery, network speed) and varying privacy requirements.
*   **Proposed Solution:** A resource-aware orchestrator that dynamically groups clients into tiered privacy pools.
*   **Contributions:**
    1.  Design of a containerized telemetry provider for edge profiling.
    2.  Development of a TOPSIS and RL-based scheduler for tier assignment.
    3.  A stratified aggregation strategy combining homomorphic bridging, secure aggregation, and differential privacy.
    4.  Extensive benchmark evaluations verifying performance.

### 2. Related Work
*   *Federated Learning on Heterogeneous Devices:* Review of FedProx, FedNova, and active client selection policies.
*   *Privacy-Preserving FL:* Discussion of FHE (CKKS), Secure Aggregation, and Local/Global Differential Privacy in FL.
*   *Adaptive Systems:* Critique of existing scheduling solutions that ignore device resource realities.
*   *Research Gap:* Absence of a unified framework that dynamically adapts cryptographic intensity to real-time client hardware indicators.

### 3. Methodology
*   **System Model:** Formal description of the client-server system model.
*   **TOPSIS Scoring Model:** Mathematical formulas for normalizing telemetry vectors and calculating similarity distances.
*   **RL Scheduling Formulation:** Defining the state space (telemetry resources), action space (privacy tiers), and reward functions (convergence speed and resource conservation).
*   **Tiered Privacy Formulations:**
    *   *Tier 1 (High Resource):* CKKS Fully Homomorphic Encryption.
    *   *Tier 2 (Medium Resource):* Secure Aggregation masking.
    *   *Tier 3 (Low Resource):* Local Differential Privacy noise insertion.

### 4. System Architecture
*   **Module Breakdown:** High-level description of client-side (telemetry, training) and server-side (scheduler, aggregator, backend) packages.
*   **Component Lifecycles:** Sequential flow diagrams detailing initialization, active rounds, and teardowns.

### 5. Experiments
*   **Experimental Testbed:** Docker container configuration running simulated clients with constrained profiles.
*   **Datasets Used:** CIFAR-10, MNIST, and Healthcare Chest X-Ray datasets.
*   **Benchmarking Baselines:** Plain FL, homogeneous FHE, and random scheduling assignments.
*   **Measurement Metrics:** Accuracy, latency, bandwidth, CPU, memory, and energy.

### 6. Results
*   **Model Accuracy:** Analysis of convergence accuracy across varying setups.
*   **Communication Overhead:** Evaluation of bandwidth and network payload volume reductions.
*   **Hardware Profiling:** Graphs illustrating CPU/RAM footprints and battery depletion curves.

### 7. Discussion
*   Analyzing the utility-privacy-resource trade-offs.
*   Explaining why tiered clustering accelerates training speed while maintaining accuracy.
*   Implementation lessons in edge-device deployments.

### 8. Threats to Validity
*   *Internal Validity:* Handling client dropouts and networking fluctuations.
*   *External Validity:* Simulating IoT workloads on containerized environments.
*   *Construct Validity:* Influence of TOPSIS weight selections.

### 9. Future Work
*   Transitioning from centralized servers to decentralized peer-to-peer (P2P) orchestration.
*   Integrating hardware-specific hardware accelerators (e.g. Edge TPUs, mobile GPUs).
*   Adding support for active malicious adversary detection.

### 10. References
*   Includes citation placeholders for Flower framework publications, CKKS encryption proofs, differential privacy bounds, and resource scheduling algorithms.
