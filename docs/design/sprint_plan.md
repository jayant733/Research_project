# Sprint Plan

This document maps out the six-month, 6-sprint development roadmap (assuming a team of 3 engineers: Student A, Student B, and Student C, with each sprint lasting exactly 1 month / 4 weeks).

---

## Sprint 1: Project Foundation & Interface Design
*   **Goal:** Establish clean repository interfaces, base configuration structures, environment parameters, and container orchestration frameworks.
*   **Stories:**
    *   `RATC-101`: Core interfaces definition.
    *   `RATC-102`: Configuration and settings mappings.
    *   `RATC-702`: Database and metrics schema design.
*   **Deliverables:**
    *   All core module interfaces (`IScheduler`, `ITelemetryProvider`, etc.) documented and committed.
    *   Template files (`config.yaml`, `.env.example`, `docker-compose.yml`) committed.
*   **Acceptance Criteria:**
    *   All interface files compile and parse without syntax errors.
    *   Docker Compose successfully builds empty placeholder service containers.
*   **Risks:**
    *   Misalignment on interface signatures between the cryptography and orchestration modules.
    *   *Mitigation:* Conduct a joint review of interface contracts before committing.
*   **Buffer:** 3 working days at the end of Sprint 1.
*   **Definition of Done:** Interface specs pass formatting lints; code is committed to the `main` branch.

---

## Sprint 2: Cryptographic Engine & Local Training
*   **Goal:** Build the privacy transformation primitives (FHE/DP/SecAgg) and link them to local PyTorch gradient descent training loops.
*   **Stories:**
    *   `RATC-201`: Homomorphic Encryption pipeline implementation.
    *   `RATC-202`: Differential Privacy noise injection.
    *   `RATC-501`: Local model trainer implementation.
*   **Deliverables:**
    *   `IPrivacyEngine` implementation using CKKS FHE and DP libraries.
    *   `ITrainingEngine` implementation with custom optimizer steps.
*   **Acceptance Criteria:**
    *   Model weights can be homomorphically encrypted and decrypted with noise margins below specified limits.
    *   Local model trains to convergence on simulated dataset partitions.
*   **Risks:**
    *   High memory consumption during FHE calculations leading to Out of Memory (OOM) errors.
    *   *Mitigation:* Profile early using small polynomial modulus degrees.
*   **Buffer:** 5 working days at the end of Sprint 2.
*   **Definition of Done:** Unit tests for FHE and training modules reach >= 80% code coverage.

---

## Sprint 3: Flower Wrapping & Server Orchestration
*   **Goal:** Construct the Flower federated client/server wrappers and design client connection and strategy aggregation logic.
*   **Stories:**
    *   `RATC-502`: Flower client wrapper.
    *   `RATC-503`: Flower server wrapper.
    *   `RATC-203`: Multi-pool aggregations.
*   **Deliverables:**
    *   `IFlowerClient` and `IFlowerServer` wrappers integrated into the system runtime.
    *   Aggregation strategies (`IAggregator`) supporting tiered pooling.
*   **Acceptance Criteria:**
    *   Multi-client connections establish reliably over gRPC channels.
    *   Server successfully executes weight broadcasts and aggregates client responses.
*   **Risks:**
    *   Flower socket timeouts during heavy client weight uploads.
    *   *Mitigation:* Enforce connection retry and dynamic timeout parameters.
*   **Buffer:** 4 working days at the end of Sprint 3.
*   **Definition of Done:** Successful end-to-end plain FL training execution run over 3 client container instances.

---

## Sprint 4: Telemetry Provider & Resource-Aware Scheduler
*   **Goal:** Implement hardware harvesting hooks on clients and build the resource-aware routing scheduler.
*   **Stories:**
    *   `RATC-301`: Hardware metrics harvesting.
    *   `RATC-401`: TOPSIS/RL scheduling policy core.
*   **Deliverables:**
    *   `ITelemetryProvider` daemon reading cgroup endpoints.
    *   `IScheduler` assigning privacy pools based on telemetry inputs.
*   **Acceptance Criteria:**
    *   Clients continuously harvest and report normalized resource vectors.
    *   The scheduler assigns clients to correct privacy tiers based on telemetry thresholds.
*   **Risks:**
    *   Host cgroup query restrictions on target platforms.
    *   *Mitigation:* Implement fallbacks to standard system-level performance library diagnostics.
*   **Buffer:** 4 working days at the end of Sprint 4.
*   **Definition of Done:** Integration tests verify telemetry extraction and correct TOPSIS scoring calculations.

---

## Sprint 5: Integrated Benchmarks & Dashboard Ingestion
*   **Goal:** Integrate all modules into automated simulation pipelines and configure telemetry databases and dashboards.
*   **Stories:**
    *   `RATC-601`: Automated experiment executor.
    *   `RATC-701`: Real-time dashboard interface.
*   **Deliverables:**
    *   `IExperimentRunner` pipeline for automated multi-round testing.
    *   Prometheus/Grafana databases and dashboards tracking system statistics.
*   **Acceptance Criteria:**
    *   Benchmark scripts generate execution statistics logs automatically.
    *   Dashboards plot accuracy, CPU loads, and bandwidth consumption in real-time.
*   **Risks:**
    *   High logging volumes throttling performance during large client scaling benchmarks.
    *   *Mitigation:* Implement asynchronous batch logging handlers.
*   **Buffer:** 6 working days at the end of Sprint 5.
*   **Definition of Done:** Benchmarks run successfully across all three tiers (FHE, SecAgg, DP/Plain).

---

## Sprint 6: Optimization, Validation & Final Defense Prep
*   **Goal:** Polish system performance, perform final stress tests, write IEEE paper draft, and create semester defense slide templates.
*   **Stories:**
    *   `RATC-602`: Performance evaluation and latency analysis.
    *   `RATC-801`: IEEE paper drafting.
    *   `RATC-901`: Semester presentation compiling.
*   **Deliverables:**
    *   Final verified repository code.
    *   Complete IEEE paper manuscript draft.
    *   20-slide semester defense presentation.
*   **Acceptance Criteria:**
    *   No blocking errors in code.
    *   Zero failed unit/integration test cases.
    *   All benchmarks complete and output to evaluation tables.
*   **Risks:**
    *   Discrepancies in experimental metrics compared to initial baseline claims.
    *   *Mitigation:* Run extensive validation tests across diverse hardware profiles.
*   **Buffer:** 7 working days at the end of Sprint 6.
*   **Definition of Done:** Code frozen; all project documentation signed off.
