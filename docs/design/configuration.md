# Configuration Specifications

This document defines the schema, format, fields, and options for every configuration layer in the Resource-Aware Tiered Clustering (RATC) project. It contains no executable code.

---

## 1. Environment Config (ENV - `.env`)

The `.env` file holds node-specific and secret environment variables injected at runtime.

*   `ENVIRONMENT`: Identifies the execution profile (`development`, `staging`, `production`). Determines system behavior overrides.
*   `SERVER_HOST`: The IP address or domain name where the server socket listens.
*   `SERVER_PORT`: The network port number for the main Flower and orchestrator server.
*   `DATABASE_URL`: Connection string containing username, password, host, port, and database name for metrics storage.
*   `LOG_LEVEL`: Minimum reporting level for logs (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
*   `CRYPTO_KEY_PATH`: Absolute filesystem path to the directory containing key pairs (e.g. CKKS context keys).
*   `FLOWER_BACKEND_URL`: REST API or RPC connection string for Flower framework orchestration.
*   `PROMETHEUS_PORT`: The network port assigned for exposing metrics scraping interfaces.

---

## 2. Container Orchestration (Docker Compose - `docker-compose.yml`)

The Docker Compose configuration structures the local multi-container network configuration, orchestration services, and hardware limits.

*   `version`: Version of the docker-compose schema spec.
*   `services`: Maps the services that constitute the application stack.
    *   `server`:
        *   `image`: Docker repository image to build/pull.
        *   `container_name`: The runtime name of the container instance.
        *   `ports`: Maps container-internal ports to host-machine ports.
        *   `environment`: Links variables from the host OS / `.env` file into the container.
        *   `volumes`: File system binds or named volumes mapping data folders inside the container.
        *   `networks`: Logical network bridges connecting containers.
    *   `client`:
        *   `deploy.resources.limits.cpus`: Limits the number of fractional CPU cores allocated to the container (e.g., `"1.5"`).
        *   `deploy.resources.limits.memory`: Limits the maximum RAM consumption of the client container (e.g., `"2G"`).
    *   `db` / `prometheus` / `grafana`: Monitoring database and visualizer service configurations, including port mappings and data volume binds.

---

## 3. Experiment Config (JSON - `experiment_config.json`)

Controls global parameters for federated learning benchmark iterations and datasets.

*   `experiment_name`: String identifier describing the current benchmark run.
*   `dataset_name`: Name of the partition dataset target (e.g. `"CIFAR-10"`, `"res_xray"`).
*   `num_rounds`: Integer total of federated learning cycles to run.
*   `batch_size`: Integer number of samples processed before updating local weights.
*   `learning_rate`: Floating-point scalar specifying gradient update step sizing.
*   `client_selection_ratio`: Fraction of active clients chosen randomly per round if selection is enabled.
*   `privacy_configuration`:
    *   `fhe_enabled`: Boolean enabling Fully Homomorphic Encryption.
    *   `secagg_enabled`: Boolean enabling Secure Aggregation masking.
    *   `dp_enabled`: Boolean enabling Differential Privacy noise injection.
    *   `dp_epsilon`: DP scale parameter controlling maximum privacy loss budget.
    *   `dp_delta`: DP failure parameter controlling probability of privacy leak.

---

## 4. Scheduler Config (YAML - `scheduler_config.yaml`)

Defines parameters for assigning client nodes to appropriate tier structures.

*   `scheduling_policy`: The active decision-making strategy (`topsis`, `rl`, `heuristic`).
*   `topsis_weights`: Weights representing priorities sum-scaling to 1.0.
    *   `cpu`: Weight assigned to CPU capacity metrics.
    *   `memory`: Weight assigned to RAM metrics.
    *   `network_bandwidth`: Weight assigned to bandwidth metrics.
    *   `battery`: Weight assigned to battery power levels.
    *   `data_sensitivity`: Weight assigned to compliance/privacy sensitivity rules.
*   `rl_policy`: Parameters for the Reinforcement Learning scheduling policies.
    *   `learning_rate`: Step parameter for optimizer updates.
    *   `gamma`: Discount factor for calculating future reward expectations.
    *   `epsilon_start`: Starting value of the exploration parameter.
    *   `epsilon_decay`: Rate at which exploration decays.
    *   `epsilon_min`: The minimum exploratory baseline.
    *   `hidden_dim`: Neurons in neural network hidden layers.
*   `tier_thresholds`: Normalized score thresholds classifying nodes into tiers.
    *   `tier_1_fhe`: Score above which nodes undergo homomorphic encryption pipelines.
    *   `tier_2_sec_agg`: Score above which nodes undergo secure aggregation pipelines.

---

## 5. Telemetry Config (YAML - `telemetry_config.yaml`)

Controls the intervals and target paths for client-side metric harvesting.

*   `harvesting_interval_seconds`: Integer seconds indicating how frequently system sensors are checked.
*   `metric_endpoints`: System target paths for resource scraping.
    *   `cpu_path`: Path for CPU usage (e.g. `/proc/stat` or cgroup path).
    *   `memory_path`: Path for RAM metrics (e.g. `/proc/meminfo` or cgroup path).
    *   `network_device`: System label for the default network adapter interface.
    *   `battery_path`: Target file containing battery status registers.
*   `normalization_factors`: Hardware maximum assumptions for parsing resource metrics.
    *   `max_cpu_mhz`: Maximum processor capacity assumed.
    *   `max_memory_mb`: Maximum system RAM expected.
    *   `max_bandwidth_kbps`: Maximum data transmission rate assumed.

---

## 6. Monitoring Config (YAML - `monitoring_config.yaml`)

Defines configuration targets for metrics ingestion and alert behaviors.

*   `prometheus_scraping`:
    *   `enabled`: Boolean setting to toggle metric storage integrations.
    *   `scrape_interval`: Periodicity of Prometheus server fetch requests.
    *   `targets`: IP endpoints where metrics are scraped.
*   `grafana_dashboards`:
    *   `enabled`: Boolean controlling dashboard UI hosting.
    *   `dashboard_paths`: Folder locations of target JSON templates defining visual layouts.
*   `alerting`:
    *   `enabled`: Boolean enabling notification integrations.
    *   `slack_webhook_url`: Notification delivery URL endpoint.
    *   `thresholds`:
        *   `cpu_threshold_percent`: Limit of CPU load triggering alarms.
        *   `memory_threshold_percent`: RAM consumption limit triggering alarms.
        *   `disconnected_timeout_seconds`: Time before a client node is marked offline.

---

## 7. Logging Config (JSON - `logging_config.json`)

Details formatting and routing targets for system logging.

*   `version`: Version value of Python's logging dictionary config schema.
*   `disable_existing_loggers`: Boolean indicating whether pre-existing logging configs are disabled.
*   `formatters`:
    *   `brief`: Short log template (e.g. level name, message text).
    *   `detailed`: Full log details including timestamp, module path, and thread.
*   `handlers`:
    *   `console`: Writes outputs directly to stderr or stdout.
    *   `file_handler`: Rotates log files to prevent storage overflow. Includes fields for filepath, size limits, and backups.
*   `loggers`: Specifies logging levels and target output paths for root, scheduler, crypto, and flower sub-modules.

---

## 8. Profiles (Development, Production, Staging)

Profiles define variable overrides targeted at specific operational scenarios.

### Development Profile (`development.yaml`)
*   `log_level`: Default set to `DEBUG` for verbose trace output.
*   `fhe_parameters.insecure_fast_mode`: Enforces low cryptographic parameters to accelerate local testing pipelines.
*   `client_nodes.min_count`: Set to low limits (e.g., `2`) to enable debugging on local resources.
*   `network.ssl_required`: Set to `false` to avoid HTTPS certificate management in local setups.

### Production Profile (`production.yaml`)
*   `log_level`: Default set to `WARNING` or `ERROR` to minimize diagnostic write operations.
*   `fhe_parameters.bit_security`: Enforces high cryptographic standards (e.g., 128-bit or 256-bit security parameters).
*   `client_nodes.min_count`: Minimum client count to initiate rounds (e.g., `100`).
*   `network.ssl_required`: Set to `true` to require HTTPS/TLS certificate bindings.
*   `metrics_persistence`: Enables long-term database persistence for run data.
