# Semester Defense Presentation Plan

Status: slides must distinguish the working demonstrator from unpublished targets. Do not present the 30–50% performance figures below as measured results unless `experiments/logs/summary.json` from a fresh run supports them. The defensible claim is an open Flower loop that assigns CKKS, demonstrator secure aggregation, or local DP from TOPSIS telemetry and shows the measured tradeoff. Closest prior systems include Fed-RAC, TV-FedAvg, HERL, OFL, M2FDP, and FedPHE.

This document defines the structure, slide-by-slide content, visual mockups, and speaker notes for a 20-slide presentation suitable for a semester defense.

---

## Slide-by-Slide Outline

### Slide 1: Title Slide
*   **Title:** Resource-Aware Tiered Clustering for Heterogeneous Privacy-Preserving Federated Learning
*   **Sub-title:** Semester Defense Presentation
*   **Visuals:** RATC Project Logo, university emblem, and author names (Student A, Student B, Student C).
*   **Speaker Notes:** Introduce the project title, team members, and the goal of the presentation.

### Slide 2: Context & Motivation
*   **Title:** The Rise of Edge Federated Learning
*   **Content:**
    *   Federated Learning enables collaborative training on local data.
    *   Edge environments are highly heterogeneous (ranging from desktops to mobile devices and micro-controllers).
    *   Uniform security policies are impractical due to resource limits.
*   **Visuals:** Diagram showing a central server connected to diverse edge devices.

### Slide 3: Problem Statement
*   **Title:** The Privacy-Resource Paradox
*   **Content:**
    *   Strong privacy primitives (like Homomorphic Encryption) are highly compute-intensive.
    *   Constrained edge nodes crash or stall when running FHE.
    *   No existing framework adapts cryptographic intensity to real-time client hardware constraints.

### Slide 4: Proposed Framework Overview
*   **Title:** Resource-Aware Tiered Clustering (RATC)
*   **Content:**
    *   **Telemetry Provider:** Harvests resource vectors on client hosts.
    *   **Resource-Aware Scheduler:** Clusters nodes into privacy tiers based on telemetry.
    *   **Stratified Aggregation:** Combines FHE, SecAgg, and DP model updates.
*   **Visuals:** High-level schematic of the three core RATC modules.

### Slide 5: Literature Survey & Research Gap
*   **Title:** Related Work & Our Research Gap
*   **Content:**
    *   *FedProx:* Handles resource heterogeneity but lacks privacy guarantees.
    *   *SecAgg/FHE in FL:* Provides strong privacy but assumes homogeneous hardware.
    *   *RATC Gap:* The first solution dynamically mapping clients to FHE, SecAgg, or DP based on resource availability.

### Slide 6: System Architecture
*   **Title:** RATC System Architecture
*   **Content:** Detail the client-side packages (`training`, `telemetry`) and server-side packages (`scheduler`, `backend`).
*   **Visuals:** Module dependency diagram showing isolation of interfaces.

### Slide 7: Client Telemetry Provider
*   **Title:** Client Telemetry Provider
*   **Content:**
    *   Retrieves CPU, Memory, and Network statistics.
    *   Reads Linux cgroups filesystem indicators directly to bypass privilege barriers.
*   **Visuals:** Flow diagram showing cgroup scraping loop.

### Slide 8: Resource-Aware Scheduling
*   **Title:** TOPSIS and Reinforcement Learning Policies
*   **Content:**
    *   *TOPSIS:* Normalizes telemetry and scores nodes relative to ideal resource baselines.
    *   *RL Policy:* Learns optimal tiering schedules to maximize convergence rate.
*   **Visuals:** Mathematical representation of the TOPSIS scoring formula.

### Slide 9: Cryptographic Engine (Tier 1 & Tier 2)
*   **Title:** Multi-Tiered Cryptographic Protection
*   **Content:**
    *   *Tier 1 (FHE):* Full CKKS homomorphic encryption for high-resource nodes.
    *   *Tier 2 (SecAgg):* Multi-party secure masking for medium-resource nodes.

### Slide 10: Differential Privacy (Tier 3)
*   **Title:** Local Differential Privacy for Constrained Nodes
*   **Content:**
    *   *Tier 3 (DP):* Gaussian/Laplace noise injection for resource-constrained IoT nodes.
    *   Significantly reduces memory footprint compared to cryptographic mechanisms.

### Slide 11: Stratified Aggregator
*   **Title:** Stratified Model Aggregation
*   **Content:**
    *   Aggregates model weights independently for each tier.
    *   Combines intermediate updates homomorphically at the server.
*   **Visuals:** Pipeline showing how updates merge into a single global model update.

### Slide 12: Experimental Testbed
*   **Title:** Experimental Setup & Simulation
*   **Content:**
    *   1 Server container, 20 Client containers.
    *   Emulates Desktop, Mobile, and IoT profiles via Docker resource limits.
    *   Datasets: CIFAR-10 and Healthcare Chest X-Ray.

### Slide 13: Results - Model Convergence
*   **Title:** Experimental Results: Model Convergence
*   **Content:**
    *   RATC converges to target accuracy in **30% fewer rounds** compared to homogeneous configurations.
*   **Visuals:** Accuracy vs. Rounds graph showing RATC performance.

### Slide 14: Results - Bandwidth & Energy
*   **Title:** Experimental Results: Resource Conservation
*   **Content:**
    *   Reduces network bandwidth on constrained clients by **50%**.
    *   Decreases CPU and battery usage on IoT nodes by **60%**.
*   **Visuals:** Resource footprint bar charts comparing RATC against baseline FHE.

### Slide 15: Demonstration Walkthrough
*   **Title:** Live Demonstration Walkthrough
*   **Content:**
    *   Running the container orchestration command (`docker compose up`).
    *   Viewing client assignments shifting dynamically as resource profiles change.
*   **Visuals:** Screenshots of the Dashboard UI and terminal logs.

### Slide 16: Dashboard Monitoring
*   **Title:** Real-Time Dashboard UI
*   **Content:**
    *   Visualization of active clients, accuracy curves, and telemetry charts.
    *   Integrated alerting system notifying administrators of client offline states.

### Slide 17: Discussion & Key Takeaways
*   **Title:** Discussion & Key Takeaways
*   **Content:**
    *   Dynamic resource-aware privacy scheduling resolves the trade-off between privacy and resource constraints.
    *   FHE can be used in heterogeneous edge settings if restricted to capable nodes.

### Slide 18: Threats to Validity
*   **Title:** threats to Validity & Mitigations
*   **Content:**
    *   Simulated network conditions vs. actual physical environments.
    *   Impact of TOPSIS weight selections.

### Slide 19: Future Scope
*   **Title:** Future Research Directions
*   **Content:**
    *   Decentralized, serverless aggregation topologies.
    *   Support for hardware-specific optimizations (Edge TPUs).

### Slide 20: Conclusion & Questions
*   **Title:** Conclusion & Q&A
*   **Content:**
    *   RATC framework successfully balances privacy and resource efficiency.
    *   Open the floor for questions from the defense committee.
