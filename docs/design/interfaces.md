# Interface Specifications

This document defines the interface designs for all core modules of the Resource-Aware Tiered Clustering (RATC) project. Every interface outline defines:
- **Responsibilities:** Core purpose and domain role.
- **Methods:** API operations.
- **Inputs:** Parameters, types, and descriptions.
- **Outputs:** Return values, types, and descriptions.
- **Exceptions:** Errors raised under specific failure conditions.

No implementations are provided.

---

## 1. `IScheduler`

*   **Responsibilities:**
    *   Evaluates telemetry vectors containing real-time resource indicators from active client nodes.
    *   Assesses data sensitivity and compliance constraints for each client.
    *   Executes resource-aware clustering (e.g., using TOPSIS or RL policies) to group clients into appropriate privacy tiers.
    *   Outputs tier routing assignments for client execution.

*   **Methods:**
    *   `evaluate(telemetry: Map<String, TelemetryVector>, constraints: Map<String, ConstraintVector>) -> Map<String, PrivacyTier>`

*   **Inputs:**
    *   `telemetry`: `Map<String, TelemetryVector>` - A lookup linking active client IDs to their normalized resource vectors (CPU, Memory, Network status, battery levels).
    *   `constraints`: `Map<String, ConstraintVector>` - A lookup linking client IDs to compliance rules, required differential privacy budgets, and sensitivity indicators.

*   **Outputs:**
    *   `Map<String, PrivacyTier>` - A mapping of client IDs to their assigned privacy execution tiers (e.g., `PrivacyTier.TIER_1_FHE`, `PrivacyTier.TIER_2_SEC_AGG`, `PrivacyTier.TIER_3_DP_PLAIN`).

*   **Exceptions:**
    *   `InvalidTelemetryError`: Raised if telemetry values are missing, corrupted, or contain parameters outside logical bounds (e.g., negative CPU usage).
    *   `NoActiveClientsError`: Raised if the telemetry mapping is empty, indicating zero active nodes are online.

---

## 2. `ITelemetryProvider`

*   **Responsibilities:**
    *   Retrieves low-level hardware performance and operating system resource indicators from the client node.
    *   Standardizes metrics such as CPU usage, RAM utilization, network bandwidth, and battery levels into a unified vector format.
    *   Abstracts OS-specific calls (e.g., checking Linux cgroups or sysfs) to support cross-platform telemetry harvesting.

*   **Methods:**
    *   `harvest_metrics() -> TelemetryVector`
    *   `get_battery_status() -> Float`

*   **Inputs:** None.

*   **Outputs:**
    *   `harvest_metrics()` returns a `TelemetryVector` object representing normalized client system performance.
    *   `get_battery_status()` returns a `Float` indicating the remaining battery capacity scaled between `0.0` (fully depleted) and `1.0` (fully charged).

*   **Exceptions:**
    *   `SensorReadError`: Raised if the OS blocks read operations on hardware endpoints (e.g., due to insufficient system privileges or sandboxing).

---

## 3. `IAggregator`

*   **Responsibilities:**
    *   Combines model updates (gradients or weights) received from clients assigned to a specific privacy tier.
    *   Executes homomorphic addition and scalar operations on encrypted updates when processing FHE updates.
    *   Performs secure multi-party consensus aggregations for Secure Aggregation updates.
    *   Generates a final aggregated global model weight set by combining the intermediate aggregates of all tiers.

*   **Methods:**
    *   `aggregate_pool(pool_id: String, updates: List<ModelUpdate>) -> PoolAggregate`
    *   `homomorphic_bridge(aggregates: Map<String, PoolAggregate>) -> EncryptedAggregate`

*   **Inputs:**
    *   `pool_id`: `String` - Unique label of the target privacy cluster/pool.
    *   `updates`: `List<ModelUpdate>` - A collection of parameter updates received from clients within the specified pool.
    *   `aggregates`: `Map<String, PoolAggregate>` - Intermediate combined models from all active pools to be unified.

*   **Outputs:**
    *   `aggregate_pool()` returns a `PoolAggregate` object enclosing the consolidated parameters of the pool.
    *   `homomorphic_bridge()` returns an `EncryptedAggregate` holding the final combined model in an encrypted state.

*   **Exceptions:**
    *   `CryptographicMismatchError`: Raised if parameters/updates use mismatched encryption scales, noise budgets, or key rings.
    *   `PoolAggregationFailure`: Raised if the numerical summation fails, receives NaN values, or encounters missing weights.

---

## 4. `IFlowerClient`

*   **Responsibilities:**
    *   Acts as the local execution agent interfacing with the Flower federated learning coordinator.
    *   Receives updated global model weights from the server.
    *   Coordinates the local data loading, training, and privacy enforcement pipelines.
    *   Returns training and evaluation outcomes back to the server.

*   **Methods:**
    *   `fit(parameters: List<Array>) -> Pair<List<Array>, Integer>`
    *   `evaluate(parameters: List<Array>) -> Pair<Float, Float>`

*   **Inputs:**
    *   `parameters`: `List<Array>` - A list of tensor arrays containing the current global model weights.

*   **Outputs:**
    *   `fit()` returns a tuple containing:
        *   `List<Array>`: The locally adjusted model parameters.
        *   `Integer`: The count of local training samples processed.
    *   `evaluate()` returns a tuple containing:
        *   `Float`: The local evaluation loss.
        *   `Float`: The evaluation accuracy or target performance metric.

*   **Exceptions:**
    *   `ClientConnectionTimeout`: Raised if network sockets fail to establish connection with the server within the designated timeout.
    *   `TrainingInterruptException`: Raised if training is terminated unexpectedly due to hardware errors, user cancellation, or OS preemptions.

---

## 5. `IFlowerServer`

*   **Responsibilities:**
    *   Listens on designated socket ports for client connections.
    *   Manages the global federated training loop rounds.
    *   Orchestrates configuration broadcasts, telemetry collection requests, and model weight distributions.
    *   Fires up the aggregation strategy on round completion.

*   **Methods:**
    *   `start_listeners() -> Void`
    *   `broadcast_round(round_idx: Integer) -> Void`

*   **Inputs:**
    *   `round_idx`: `Integer` - The sequence index of the current global training round.

*   **Outputs:** None.

*   **Exceptions:**
    *   `SocketBindingError`: Raised if target ports are already bound by another process or if network access is restricted.

---

## 6. `IPrivacyEngine`

*   **Responsibilities:**
    *   Enforces privacy transformations on model weights and gradients.
    *   Implements Fully Homomorphic Encryption (FHE) mechanisms (e.g., CKKS parameter setup and encryption).
    *   Implements Local Differential Privacy (LDP) noise injection algorithms (e.g., Gaussian/Laplace mechanisms).
    *   Generates pseudo-random masking weights for secure aggregation protocols.

*   **Methods:**
    *   `encrypt_weights(weights: Vector) -> Ciphertext`
    *   `apply_dp_noise(gradients: Tensor) -> Tensor`
    *   `generate_mask(seed: Integer) -> Vector`

*   **Inputs:**
    *   `weights`: `Vector` - Flat numeric vector of local model parameters.
    *   `gradients`: `Tensor` - PyTorch gradient tensors to be regularized with noise.
    *   `seed`: `Integer` - Pseudo-random number generator seed to generate masks.

*   **Outputs:**
    *   `encrypt_weights()` returns a `Ciphertext` object holding the homomorphically encrypted weights.
    *   `apply_dp_noise()` returns a noise-perturbed `Tensor`.
    *   `generate_mask()` returns a `Vector` mask.

*   **Exceptions:**
    *   `ScaleOutOfRangeError`: Raised if FHE encoding parameters scale outside the noise budget boundaries.
    *   `DecryptionFailure`: Raised if key configurations are invalid or if a decryption step is triggered with corrupted keys.

---

## 7. `ITrainingEngine`

*   **Responsibilities:**
    *   Executes model training epochs locally using client-side PyTorch instances.
    *   Loads local training partitions into memory batches.
    *   Computes loss and backpropagation gradients using custom optimizers (e.g. Adam, SGD, FedProx).
    *   Computes validation metric curves on local testing datasets.

*   **Methods:**
    *   `train_epoch(model: Model, loader: DataLoader) -> Float`
    *   `evaluate_model(model: Model, loader: DataLoader) -> Pair<Float, Float>`

*   **Inputs:**
    *   `model`: `Model` - The PyTorch target model architecture.
    *   `loader`: `DataLoader` - The iterator managing local data samples.

*   **Outputs:**
    *   `train_epoch()` returns the mean training loss (`Float`) across all batches in the epoch.
    *   `evaluate_model()` returns a tuple of `Pair<Float, Float>` containing the mean evaluation loss and classification accuracy.

*   **Exceptions:**
    *   `OutOfMemoryError`: Raised if system RAM/GPU VRAM is exhausted during batch processing.
    *   `DatasetNotLoadedError`: Raised if data streams are uninitialized, files are missing, or format parsing fails.

---

## 8. `IExperimentRunner`

*   **Responsibilities:**
    *   Automates runs of simulations, benchmarks, and training experiments under various configurations.
    *   Sets up training environments, calls client/server scripts, and logs execution runs.
    *   Extracts convergence speed, resource costs, and final model accuracy.
    *   Persists benchmark logs to CSV or JSON formats.

*   **Methods:**
    *   `run_benchmark(config: ExperimentConfig) -> FilePath`

*   **Inputs:**
    *   `config`: `ExperimentConfig` - Configuration specification defining datasets, client sizes, tiers, and hyperparameters.

*   **Outputs:**
    *   `FilePath`: `String` - Absolute file system path pointing to the generated performance evaluation log.

*   **Exceptions:**
    *   `ConfigurationMismatchError`: Raised if experiment parameters conflict or reference invalid configurations (e.g. referencing a non-existent dataset).

---

## 9. `IDashboardService`

*   **Responsibilities:**
    *   Renders real-time dashboards to visualize training rounds, accuracy curves, and telemetry charts.
    *   Acts as the API host querying monitoring backends.
    *   Updates plots dynamically as metrics are received.

*   **Methods:**
    *   `render_ui() -> Void`
    *   `update_plots(metrics: TimeSeriesData) -> Void`

*   **Inputs:**
    *   `metrics`: `TimeSeriesData` - Structured time-series records of telemetry and training metrics.

*   **Outputs:** None.

*   **Exceptions:**
    *   `DatabaseQueryError`: Raised if metrics cannot be retrieved due to connection loss or schema mismatch.

---

## 10. `IConfigurationLoader`

*   **Responsibilities:**
    *   Parses configuration templates (JSON, YAML, ENV) from disk.
    *   Validates format correctness and boundary limits of incoming parameters.
    *   Injects active configuration overrides based on profiles (development, production).
    *   Outputs a unified, typed system configuration runtime object.

*   **Methods:**
    *   `load_config(path: FilePath) -> SystemConfig`

*   **Inputs:**
    *   `path`: `FilePath` - The absolute target location of the configuration file.

*   **Outputs:**
    *   `SystemConfig` - A structured config representation mapping all properties.

*   **Exceptions:**
    *   `InvalidConfigurationFormat`: Raised if syntactic validation fails or if mandatory parameters are missing.

---

## 11. `ILogger`

*   **Responsibilities:**
    *   Writes structured diagnostic messages (INFO, WARN, ERROR) to standard outputs and files.
    *   Formats log statements with timestamp metadata and module namespaces.
    *   Ensures asynchronous execution so logging operations do not block main computational loops.

*   **Methods:**
    *   `log_info(msg: String) -> Void`
    *   `log_error(err: Exception) -> Void`

*   **Inputs:**
    *   `msg`: `String` - Descriptive message text.
    *   `err`: `Exception` - The caught exception.

*   **Outputs:** None.

*   **Exceptions:** None.
