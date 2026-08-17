# Repository Structure

This document designs the directory structure, package responsibilities, code ownership, dependencies, and extension points for the RATC repository.

---

## 1. Directory Tree Structure

```
c:/Users/jayan/Videos/Research_project/
├── .env.example                    # Template environment variables file
├── docker-compose.yml              # Multi-container service definition file
├── Architecture.md                 # System overview specification
├── docs/                           # Documentation root
│   ├── research/                   # Academic and literature surveys
│   ├── design/                     # Architectural design files
│   ├── experiments/                # Experiment details and plans
│   ├── paper/                      # Publication drafts
│   └── presentations/              # Slides for semester defense
├── config/                         # Configuration templates and profiles
│   ├── scheduler_config.yaml       # Scheduler criteria
│   ├── telemetry_config.yaml       # Telemetry polling settings
│   ├── monitoring_config.yaml      # Scraping and alerts configuration
│   ├── logging_config.json         # Python logging configurations
│   ├── experiment_config.json      # Experiment parameters
│   └── profiles/                   # Run profile overrides
│       ├── development.yaml        # Local debugging parameters
│       └── production.yaml         # Secure deployment parameters
├── src/                            # Source code root
│   ├── client/                     # Client-side packages
│   │   ├── __init__.py
│   │   ├── training/               # Local training loop modules
│   │   │   ├── __init__.py
│   │   │   ├── interface.py        # ITrainingEngine
│   │   │   └── engine.py           # PyTorch implementation
│   │   └── telemetry/              # System hardware diagnostics
│   │       ├── __init__.py
│   │       ├── interface.py        # ITelemetryProvider
│   │       └── provider.py         # OS sensor reading routines
│   ├── server/                     # Server-side packages
│   │   ├── __init__.py
│   │   ├── scheduler/              # Tier clustering and scheduling
│   │   │   ├── __init__.py
│   │   │   ├── interface.py        # IScheduler
│   │   │   └── scheduler.py        # TOPSIS/RL algorithms
│   │   └── backend/                # Dashboard database and UI APIs
│   │       ├── __init__.py
│   │       ├── interface.py        # IDashboardService
│   │       └── service.py          # Dashboard endpoints
│   ├── crypto/                     # Security and cryptographic utilities
│   │   ├── __init__.py
│   │   ├── interface.py            # IPrivacyEngine
│   │   └── engine.py               # FHE / LDP implementations
│   ├── flower/                     # Flower wrapper integration
│   │   ├── __init__.py
│   │   ├── client_interface.py     # IFlowerClient
│   │   ├── server_interface.py     # IFlowerServer
│   │   ├── aggregator_interface.py # IAggregator
│   │   ├── client_wrapper.py       # Client Flower hooks
│   │   ├── server_wrapper.py       # Server Flower hooks
│   │   └── aggregator.py           # Stratified aggregation
│   └── utils/                      # Shared helper scripts
│       ├── __init__.py
│       ├── config_loader.py        # IConfigurationLoader implementation
│       └── logger.py               # ILogger implementation
├── experiments/                    # Run scripts and log directories
│   ├── interface.py                # IExperimentRunner
│   ├── runner.py                   # Simulation orchestrator
│   └── logs/                       # Benchmarking results outputs (CSV)
└── tests/                          # Automated tests suite
    ├── unit/                       # Isolated component tests
    ├── integration/                # Multi-module flow tests
    └── performance/                # Memory and throughput tests
```

---

## 2. Ownership Map

*   **Student A (Infrastructure & Telemetry):**
    *   `src/client/telemetry/`
    *   `config/telemetry_config.yaml`
    *   `tests/performance/`
    *   `docker-compose.yml`
*   **Student B (Cryptography & ML):**
    *   `src/crypto/`
    *   `src/client/training/`
    *   `config/profiles/`
    *   `tests/unit/`
*   **Student C (Orchestration & UI):**
    *   `src/server/scheduler/`
    *   `src/server/backend/`
    *   `src/flower/`
    *   `config/scheduler_config.yaml`
    *   `experiments/`

---

## 3. Package Responsibilities & Dependencies

| Package | Responsibility | Direct Dependencies |
| :--- | :--- | :--- |
| `src/utils/` | Shared loading, parsing, and logging behaviors | None |
| `src/crypto/` | Core privacy transformations (FHE, DP, Secure Masking) | `src/utils/` |
| `src/client/training/` | Executing local epochs and loss computations | `src/utils/` |
| `src/client/telemetry/` | Gathering real-time device sensor readings | `src/utils/` |
| `src/server/scheduler/` | Scoring client nodes and dividing them into privacy tiers | `src/utils/` |
| `src/flower/` | Standardizing client/server routines to Flower protocols | `src/crypto/`, `src/client/training/`, `src/server/scheduler/` |
| `src/server/backend/` | Storing run statistics and serving dashboard indicators | `src/utils/` |
| `experiments/` | Automating multi-round simulation configurations | All modules |

---

## 4. Extension Points

1.  **Scheduling Policies:**
    *   *Where:* Add custom implementations inheriting from `IScheduler` in `src/server/scheduler/`.
2.  **Telemetry Profilers:**
    *   *Where:* Extend `ITelemetryProvider` in `src/client/telemetry/` to add platform-specific checks (e.g., Windows Registry, macOS sysctl).
3.  **Cryptographic Primitives:**
    *   *Where:* Extend `IPrivacyEngine` in `src/crypto/` to implement alternative cryptosystems (e.g., BGV or BFV).
4.  **Local Optimizers:**
    *   *Where:* Extend training parameter mappings in `ITrainingEngine` within `src/client/training/` to introduce novel optimizers (e.g. FedNova, FedAdagrad).
