# Software Architecture & Interface Specifications

This document defines the software modules, operational lifecycles, and interface designs for the **Resource-Aware Tiered Clustering (RATC)** project. It acts as the contract for all implementation modules.

---

## Part I: Module Specifications

### 1. Scheduler Module (`scheduler/`)
*   **Purpose:** Evaluates client telemetry vectors and data sensitivities to determine client pool assignments.
*   **Owner:** Student C (Orchestration & UI)
*   **Dependencies:** `config`, `logger`.
*   **Public APIs:** `IScheduler` interface.
*   **Internal APIs:** TOPSIS scoring matrices helpers, RL state encoders.
*   **Lifecycle:** Initialized during server startup. Evaluated at the start of every federated round after collecting client telemetry.
*   **Extension Points:** Pluggable scheduling models (heuristics, game theory, deep neural policies).
*   **Error Handling:** Fallback to a rule-based heuristic scheduler if the RL agent fails to evaluate or yields null.

### 2. Telemetry Module (`src/client/telemetry/`)
*   **Purpose:** Profiles hardware resource indicators and network metrics on client hosts.
*   **Owner:** Student A (Infrastructure & Telemetry)
*   **Dependencies:** `logger`, `config`.
*   **Public APIs:** `ITelemetryProvider` interface.
*   **Internal APIs:** System sensor reading hooks, JSON serializer formats.
*   **Lifecycle:** Boots as an asynchronous daemon thread when the client container starts.
*   **Extension Points:** Support for hardware-specific sensor queries (e.g. GPU telemetry).
*   **Error Handling:** Emits a `SensorReadError` and reports baseline template values if the OS prevents cgroups queries.

### 3. Cryptography Module (`crypto/`)
*   **Purpose:** Encapsulates CKKS FHE, SecAgg Diffie-Hellman, and local Differential Privacy.
*   **Owner:** Student B (Cryptography & ML)
*   **Dependencies:** `logger`.
*   **Public APIs:** `IPrivacyEngine` interface.
*   **Internal APIs:** Key generators, CKKS context serializations, modular mask calculations.
*   **Lifecycle:** Instantiated during client initialization before local model loading.
*   **Extension Points:** Pluggable FHE schemes (BGV, BFV) or post-quantum cryptographic primitives.
*   **Error Handling:** Raises `ScaleOutOfRangeError` if CKKS encoding scales exceed noise budgets.

### 4. Flower Wrapper Module (`flower/`)
*   **Purpose:** Binds client local training loops and server aggregation strategies to the Flower framework.
*   **Owner:** Student C (Orchestration & UI)
*   **Dependencies:** `crypto`, `scheduler`, `training`, `logger`.
*   **Public APIs:** `IFlowerClient` and `IFlowerServer` interfaces.
*   **Internal APIs:** Strategy aggregation helpers, client port sockets manager.
*   **Lifecycle:** Active throughout the federated run duration.
*   **Extension Points:** Custom strategies for asynchronous or client-weighted aggregations.
*   **Error Handling:** Handles socket terminations using connection retry limits and logs dropouts to the registry.

### 5. Training Engine Module (`src/client/`)
*   **Purpose:** Executes local gradient descent training loops.
*   **Owner:** Student B (Cryptography & ML)
*   **Dependencies:** `datasets`, `logger`.
*   **Public APIs:** `ITrainingEngine` interface.
*   **Internal APIs:** Optimizer settings, epoch step loops.
*   **Lifecycle:** Triggered during the client's `fit` phase.
*   **Extension Points:** Support for different local optimizers (Adam, FedProx, SGD).
*   **Error Handling:** Catches `OutOfMemoryError` and requests the scheduler to reduce local batch size.
