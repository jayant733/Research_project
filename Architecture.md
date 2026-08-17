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

---

## Part II: Interface Specifications

### 1. `IScheduler`
*   **Responsibilities:** Evaluates telemetry and outputs target routing assignments.
*   **Methods:**
    *   `evaluate(telemetry: Map<String, TelemetryVector>, constraints: Map<String, ConstraintVector>) -> Map<String, PrivacyTier>`
*   **Inputs:**
    *   `telemetry`: A map linking client IDs to their continuous telemetry resource values.
    *   `constraints`: A map linking client IDs to data sensitivity and privacy compliance rules.
*   **Outputs:**
    *   A map linking client IDs to target privacy pools (Tier 1: FHE, Tier 2: SecAgg, Tier 3: DP/Plain).
*   **Exceptions:**
    *   `InvalidTelemetryError`: Thrown if telemetry fields are missing or out of range.
    *   `NoActiveClientsError`: Thrown if the client map is empty.

### 2. `ITelemetryProvider`
*   **Responsibilities:** Interfaces with system metrics.
*   **Methods:**
    *   `harvest_metrics() -> TelemetryVector`
    *   `get_battery_status() -> Float`
*   **Inputs:** None.
*   **Outputs:**
    *   `TelemetryVector`: Normalized resources vector.
    *   `Float`: Battery percentage value $[0.0, 1.0]$.
*   **Exceptions:**
    *   `SensorReadError`: Thrown if system telemetry paths are blocked.

### 3. `IAggregator`
*   **Responsibilities:** Executes sub-pool aggregates and FHE merging.
*   **Methods:**
    *   `aggregate_pool(pool_id: String, updates: List<ModelUpdate>) -> PoolAggregate`
    *   `homomorphic_bridge(aggregates: Map<String, PoolAggregate>) -> EncryptedAggregate`
*   **Inputs:**
    *   `pool_id`: Pool identifier tag.
    *   `updates`: Received client updates from a specific pool.
    *   `aggregates`: Outputs from the independent pools.
*   **Outputs:**
    *   `PoolAggregate`: Combined parameters for a specific pool.
    *   `EncryptedAggregate`: Final merged ciphertext.
*   **Exceptions:**
    *   `CryptographicMismatchError`: Thrown if encrypted updates use different parameters.
    *   `PoolAggregationFailure`: Thrown if the aggregate summation fails.

### 4. `IFlowerClient`
*   **Responsibilities:** Handles connection routing and client lifecycles.
*   **Methods:**
    *   `fit(parameters: List<Array>) -> Pair<List<Array>, Integer>`
    *   `evaluate(parameters: List<Array>) -> Pair<Float, Float>`
*   **Inputs:**
    *   `parameters`: Weights from server.
*   **Outputs:**
    *   Updated parameters and metric outcomes.
*   **Exceptions:**
    *   `ClientConnectionTimeout`: Thrown if the connection to the server fails.
    *   `TrainingInterruptException`: Thrown if training is interrupted.

### 5. `IFlowerServer`
*   **Responsibilities:** Orchestrates server listener sockets.
*   **Methods:**
    *   `start_listeners() -> Void`
    *   `broadcast_round(round_idx: Integer) -> Void`
*   **Inputs:**
    *   `round_idx`: Target training round count index.
*   **Outputs:** None.
*   **Exceptions:**
    *   `SocketBindingError`: Thrown if server ports are already in use.

### 6. `IPrivacyEngine`
*   **Responsibilities:** Implements privacy transformations.
*   **Methods:**
    *   `encrypt_weights(weights: Vector) -> Ciphertext`
    *   `apply_dp_noise(gradients: Tensor) -> Tensor`
    *   `generate_mask(seed: Integer) -> Vector`
*   **Inputs:**
    *   `weights`/`gradients`: Model parameters.
    *   `seed`: Prng seed.
*   **Outputs:**
    *   Cryptographically modified parameter vectors.
*   **Exceptions:**
    *   `ScaleOutOfRangeError`: Thrown if CKKS scales are out of range.
    *   `DecryptionFailure`: Thrown if decryption keys fail.

### 7. `ITrainingEngine`
*   **Responsibilities:** Executes local SGD iterations.
*   **Methods:**
    *   `train_epoch(model: Model, loader: DataLoader) -> Float`
    *   `evaluate_model(model: Model, loader: DataLoader) -> Pair<Float, Float>`
*   **Inputs:**
    *   `model`: Target PyTorch graph.
    *   `loader`: Partition data iterator.
*   **Outputs:**
    *   Training loss and evaluation metrics.
*   **Exceptions:**
    *   `OutOfMemoryError`: Thrown if the GPU/CPU memory is full.
    *   `DatasetNotLoadedError`: Thrown if the dataset loader is uninitialized.

### 8. `IExperimentRunner`
*   **Responsibilities:** Automates simulation runs.
*   **Methods:**
    *   `run_benchmark(config: ExperimentConfig) -> FilePath`
*   **Inputs:**
    *   `config`: Specific configuration for the experiment run.
*   **Outputs:**
    *   `FilePath`: Path to saved performance csv metrics logs.
*   **Exceptions:**
    *   `ConfigurationMismatchError`: Thrown if config file contains invalid parameters.

### 9. `IDashboardService`
*   **Responsibilities:** Renders dashboards.
*   **Methods:**
    *   `render_ui() -> Void`
    *   `update_plots(metrics: TimeSeriesData) -> Void`
*   **Inputs:**
    *   `metrics`: Ingested metrics parameters database.
*   **Outputs:** None.
*   **Exceptions:**
    *   `DatabaseQueryError`: Thrown if metrics fetching fails.

### 10. `IConfigurationLoader`
*   **Responsibilities:** Parses JSON setups.
*   **Methods:**
    *   `load_config(path: FilePath) -> SystemConfig`
*   **Inputs:**
    *   `path`: Target filepath on disk.
*   **Outputs:**
    *   `SystemConfig`: Loaded system configurations object.
*   **Exceptions:**
    *   `InvalidConfigurationFormat`: Thrown if file structure parsing fails.

### 11. `ILogger`
*   **Responsibilities:** Writes diagnostic logs.
*   **Methods:**
    *   `log_info(msg: String) -> Void`
    *   `log_error(err: Exception) -> Void`
*   **Inputs:**
    *   `msg`: Text information.
    *   `err`: Raised exception classes.
*   **Outputs:** None.
*   **Exceptions:** None.
