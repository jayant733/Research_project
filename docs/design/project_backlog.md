# Project Backlog

This document organizes the project roadmap into a professional Jira backlog, categorized by Epics, Features, Stories, Tasks, and Subtasks.

---

## MoSCoW Classification Summary
*   **Must Have:** Core Flower wrappers, basic local training, cryptography engine (FHE/DP/SecAgg), configuration load, and logging interfaces.
*   **Should Have:** Resource-aware scheduler (TOPSIS/RL policies), telemetry providers (cgroup metrics), and benchmark experiment runners.
*   **Could Have:** Real-time Web Dashboard service, Prometheus/Grafana setups, and Slack alerting metrics configurations.
*   **Won't Have (for Phase 1):** Multi-cloud node deployments, Kubernetes auto-scaling, and decentralized blockchain ledger logging.

---

## 1. Backlog Hierarchy

### Epic 1: Project Foundation & Interface Contract (MoSCoW: Must Have)
*   **Feature 1.1: Core System Interfaces**
    *   **Story RATC-101:** Interface Definitions
        *   *Description:* Declare all 11 abstract base interfaces (`IScheduler`, `ITelemetryProvider`, etc.) in the project directories.
        *   *Story Points:* 5
        *   *Priority:* High
        *   *Owner:* Student C
        *   *Risk:* Low
        *   *Status:* Done
        *   *Dependencies:* None
        *   **Task RATC-101-T1:** Create interface files under `scheduler/`, `crypto/`, `flower/`, `monitoring/`, `backend/`, and `config/`. (Owner: Student C | SP: 2 | Status: Done)
        *   **Task RATC-101-T2:** Document docstrings mapping inputs, outputs, exceptions, and responsibilities. (Owner: Student C | SP: 3 | Status: Done)

    *   **Story RATC-102: System Configurations**
        *   *Description:* Setup configuration YAML, JSON, ENV, and profiles files schemas.
        *   *Story Points:* 3
        *   *Priority:* High
        *   *Owner:* Student C
        *   *Risk:* Low
        *   *Status:* To Do
        *   *Dependencies:* RATC-101
        *   **Task RATC-102-T1:** Define `config.yaml`, `scheduler.yaml`, and `telemetry.yaml`. (Owner: Student C | SP: 1 | Status: To Do)
        *   **Task RATC-102-T2:** Setup development and production profile overrides. (Owner: Student C | SP: 2 | Status: To Do)

---

### Epic 2: Cryptography & Security Engine (MoSCoW: Must Have)
*   **Feature 2.1: Privacy Transformations & Key Management**
    *   **Story RATC-201: Homomorphic Encryption (FHE) Pipeline**
        *   *Description:* Integrate CKKS FHE scheme to encrypt local model weights.
        *   *Story Points:* 8
        *   *Priority:* Blocker
        *   *Owner:* Student B
        *   *Risk:* High
        *   *Dependencies:* RATC-101
        *   *Status:* To Do
        *   **Task RATC-201-T1:** Initialize FHE Context matching CKKS scheme. (Owner: Student B | SP: 3 | Status: To Do)
        *   **Task RATC-201-T2:** Implement local weights encryption methods. (Owner: Student B | SP: 5 | Status: To Do)
    
    *   **Story RATC-202: Differential Privacy (DP) Noise**
        *   *Description:* Inject Gaussian and Laplace noise gradients to enforce Local Differential Privacy.
        *   *Story Points:* 5
        *   *Priority:* High
        *   *Owner:* Student B
        *   *Risk:* Medium
        *   *Dependencies:* RATC-101
        *   *Status:* To Do
        *   **Task RATC-202-T1:** Implement clipping mechanism for local updates. (Owner: Student B | SP: 2 | Status: To Do)
        *   **Task RATC-202-T2:** Write noise application functions using seed configurations. (Owner: Student B | SP: 3 | Status: To Do)

---

### Epic 3: Telemetry & Monitoring Infrastructure (MoSCoW: Should Have)
*   **Feature 3.1: Hardware Profiling Daemon**
    *   **Story RATC-301: Linux Cgroups Resource Harvester**
        *   *Description:* Extract client-side CPU share allocations and memory consumption from system cgroup endpoints.
        *   *Story Points:* 5
        *   *Priority:* High
        *   *Owner:* Student A
        *   *Risk:* Medium
        *   *Dependencies:* RATC-101
        *   *Status:* To Do
        *   **Task RATC-301-T1:** Program sysfs file readers for battery capacity and network device bandwidth. (Owner: Student A | SP: 3 | Status: To Do)
        *   **Task RATC-301-T2:** Standardize metric data structures into `TelemetryVector` formats. (Owner: Student A | SP: 2 | Status: To Do)

---

### Epic 4: Resource-Aware Scheduler (MoSCoW: Should Have)
*   **Feature 4.1: Client Tier Assigner**
    *   **Story RATC-401: TOPSIS Decision Matrix Core**
        *   *Description:* Evaluate client telemetry using TOPSIS algorithm vectors to assign nodes to Privacy Tiers.
        *   *Story Points:* 8
        *   *Priority:* High
        *   *Owner:* Student C
        *   *Risk:* Medium
        *   *Dependencies:* RATC-301
        *   *Status:* To Do
        *   **Task RATC-401-T1:** Program telemetry normalization scoring matrix. (Owner: Student C | SP: 4 | Status: To Do)
        *   **Task RATC-401-T2:** Implement tier classification logic using configured thresholds. (Owner: Student C | SP: 4 | Status: To Do)

---

### Epic 5: Flower Wrapper & Federated Loops (MoSCoW: Must Have)
*   **Feature 5.1: Client-Server Wrappers**
    *   **Story RATC-501: Federated Client Node**
        *   *Description:* Wrap local PyTorch training routines inside Flower's client class.
        *   *Story Points:* 5
        *   *Priority:* Blocker
        *   *Owner:* Student C
        *   *Risk:* Low
        *   *Dependencies:* RATC-101, RATC-201
        *   *Status:* To Do
        *   **Task RATC-501-T1:** Define local model parameters loading hooks. (Owner: Student C | SP: 2 | Status: To Do)
        *   **Task RATC-501-T2:** Implement model evaluation loops on local partitions. (Owner: Student C | SP: 3 | Status: To Do)

---

## 2. Detailed Jira Backlog Reference Table

| Issue ID | Summary | Type | SP | Priority | MoSCoW | Owner | Risk | Dependencies | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RATC-101** | Interface Definitions | Story | 5 | High | Must Have | Student C | Low | None | Done |
| **RATC-102** | System Configurations | Story | 3 | High | Must Have | Student C | Low | RATC-101 | To Do |
| **RATC-201** | Homomorphic Encryption (FHE) | Story | 8 | Blocker | Must Have | Student B | High | RATC-101 | To Do |
| **RATC-202** | Differential Privacy (DP) | Story | 5 | High | Must Have | Student B | Medium | RATC-101 | To Do |
| **RATC-301** | Linux Cgroups Harvester | Story | 5 | High | Should Have | Student A | Medium | RATC-101 | To Do |
| **RATC-401** | TOPSIS Decision Matrix Core | Story | 8 | High | Should Have | Student C | Medium | RATC-301 | To Do |
| **RATC-501** | Federated Client Node | Story | 5 | Blocker | Must Have | Student C | Low | RATC-101, RATC-201 | To Do |
| **RATC-601** | Simulation Benchmark Runner | Story | 5 | Medium | Should Have | Student A | Medium | RATC-501, RATC-401 | To Do |
| **RATC-701** | Real-Time Dashboard UI | Story | 8 | Low | Could Have | Student C | Medium | RATC-101 | To Do |
| **RATC-702** | Prometheus Scraping Setup | Story | 3 | Low | Could Have | Student A | Low | RATC-301 | To Do |
