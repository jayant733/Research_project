# Configuration Design Specifications

This document defines the schema design, field constraints, default values, validations, dependencies, and extension points for all configuration layers of the Resource-Aware Tiered Clustering (RATC) project. 

---

## 1. `config.yaml`
*   **Purpose:** Global system coordinator configuration specifying current operational mode, profile bindings, network endpoints, and data directories.
*   **Fields:**
    *   `active_profile` (string): Name of the profile config to load.
    *   `system_mode` (string): Active execution mode (`simulation`, `real_time`, `hybrid`).
    *   `data_root` (string): Root directory for local dataset caching and storage.
    *   `ssl` (object): TLS setup.
        *   `enabled` (boolean): Toggle TLS.
        *   `cert_path` (string): Path to SSL certificate.
        *   `key_path` (string): Path to SSL private key.
*   **Default values:**
    *   `active_profile`: `"development"`
    *   `system_mode`: `"simulation"`
    *   `data_root`: `"data/"`
    *   `ssl.enabled`: `false`
*   **Validation rules:**
    *   `active_profile` must match one of the defined profile files.
    *   `system_mode` must be one of: `simulation`, `real_time`, `hybrid`.
    *   `ssl.cert_path` and `ssl.key_path` must be valid paths if `ssl.enabled` is `true`.
*   **Dependencies:** Loaded first by `IConfigurationLoader`. Overridden by profiles.
*   **Future extensions:** Integration with secret managers (e.g., Vault) to retrieve certificates dynamically.

---

## 2. `scheduler.yaml`
*   **Purpose:** Configures scheduling parameters, RL model details, TOPSIS decision weights, and client tier routing thresholds.
*   **Fields:**
    *   `policy_type` (string): Policy to run (`topsis`, `rl`, `heuristic`).
    *   `topsis` (object): Weights for TOPSIS scoring (floats):
        *   `w_cpu`, `w_memory`, `w_bandwidth`, `w_battery`, `w_sensitivity`.
    *   `rl_agent` (object):
        *   `gamma` (float): Discount factor.
        *   `learning_rate` (float): Update step size.
        *   `hidden_layers` (list of integers): Layer sizes.
    *   `thresholds` (object):
        *   `tier_1_min_score` (float): Score threshold for Tier 1.
        *   `tier_2_min_score` (float): Score threshold for Tier 2.
*   **Default values:**
    *   `policy_type`: `"topsis"`
    *   `topsis.w_cpu`: `0.2`, `topsis.w_memory`: `0.2`, `topsis.w_bandwidth`: `0.2`, `topsis.w_battery`: `0.2`, `topsis.w_sensitivity`: `0.2`
    *   `rl_agent.gamma`: `0.99`, `rl_agent.learning_rate`: `0.001`
    *   `thresholds.tier_1_min_score`: `0.7`, `thresholds.tier_2_min_score`: `0.4`
*   **Validation rules:**
    *   `topsis` weights must sum exactly to `1.0`.
    *   `thresholds` must satisfy: `0.0 <= tier_2_min_score < tier_1_min_score <= 1.0`.
*   **Dependencies:** Fed into `IScheduler` to determine client placement.
*   **Future extensions:** Dynamic weight adjustment based on runtime scheduling feedback loops.

---

## 3. `telemetry.yaml`
*   **Purpose:** Configures client-side system telemetry harvesting rates and OS sensor locations.
*   **Fields:**
    *   `polling_interval_ms` (integer): Time between hardware metrics samples.
    *   `cgroup_paths` (object): Linux cgroup paths.
        *   `cpu_shares` (string)
        *   `memory_limit` (string)
    *   `interfaces` (list of strings): Network interface names.
    *   `battery_node` (string): Sysfs battery capacity node path.
*   **Default values:**
    *   `polling_interval_ms`: `1000`
    *   `cgroup_paths.cpu_shares`: `"/sys/fs/cgroup/cpu/cpu.shares"`
    *   `battery_node`: `"/sys/class/power_supply/BAT0/capacity"`
*   **Validation rules:**
    *   `polling_interval_ms` must be positive and >= `100`.
*   **Dependencies:** Used by `ITelemetryProvider` during telemetry harvesting loop.
*   **Future extensions:** Windows/macOS hardware query bindings (WMI / sysctl).

---

## 4. `monitoring.yaml`
*   **Purpose:** Controls Prometheus endpoint settings, scrape intervals, alert limits, and notification destinations.
*   **Fields:**
    *   `prometheus_enabled` (boolean): Enable Prometheus metrics.
    *   `alerting` (object):
        *   `cpu_threshold` (float): Alarm trigger CPU load percentage.
        *   `memory_threshold` (float): Alarm trigger RAM percentage.
        *   `webhook_url` (string): Alert webhook endpoint.
*   **Default values:**
    *   `prometheus_enabled`: `true`
    *   `alerting.cpu_threshold`: `90.0`
    *   `alerting.memory_threshold`: `85.0`
*   **Validation rules:**
    *   Thresholds must be floats between `0.0` and `100.0`.
    *   `webhook_url` must be a valid URL if alerting is enabled.
*   **Dependencies:** Ingested by `IDashboardService` and the alerting engine.
*   **Future extensions:** Integration with PagerDuty or Opsgenie.

---

## 5. `experiment.yaml`
*   **Purpose:** Controls simulation variables, dataset specifications, local hyper-parameters, and privacy bounds for benchmarking.
*   **Fields:**
    *   `dataset` (string): Dataset name.
    *   `rounds` (integer): Training cycles.
    *   `optimizer` (object):
        *   `name` (string): e.g. `sgd`, `adam`, `fedprox`.
        *   `lr` (float): Learning rate.
    *   `differential_privacy` (object):
        *   `epsilon` (float): Privacy loss parameter.
        *   `delta` (float): Failure probability.
*   **Default values:**
    *   `rounds`: `50`
    *   `optimizer.name`: `"sgd"`
    *   `optimizer.lr`: `0.01`
    *   `differential_privacy.epsilon`: `1.0`
*   **Validation rules:**
    *   `rounds` must be >= `1`.
    *   `differential_privacy.epsilon` must be positive.
*   **Dependencies:** Ingested by `IExperimentRunner`.
*   **Future extensions:** Support for automated hyperparameter tuning (Grid/Bayesian search).

---

## 6. `logging.yaml`
*   **Purpose:** Structures console/file handlers, log rotation policies, formatting strings, and verbosity thresholds.
*   **Fields:**
    *   `handlers` (object): Console and file configurations.
    *   `rotation` (object):
        *   `max_bytes` (integer): Max log file size.
        *   `backup_count` (integer): Retained logs.
    *   `formatters` (object): Pattern templates.
*   **Default values:**
    *   `rotation.max_bytes`: `10485760` (10MB)
    *   `rotation.backup_count`: `5`
*   **Validation rules:**
    *   `max_bytes` must be positive.
*   **Dependencies:** Parsed during system boot to initialize `ILogger`.
*   **Future extensions:** Structured JSON log outputs for Splunk/ELK stack compatibility.

---

## 7. `docker-compose.yml`
*   **Purpose:** Orchestrates multi-container execution for the server, clients, database, and monitoring components.
*   **Fields:**
    *   `version` (string): Docker Compose spec version.
    *   `services` (object): Multi-container services mapping (images, ports, env, volumes).
    *   `networks` (object): Bridge network setup.
*   **Default values:** Standard compose specifications.
*   **Validation rules:** Standard docker-compose syntax.
*   **Dependencies:** Docker engine runtime.
*   **Future extensions:** Kubernetes manifest generation.

---

## 8. `.env.example`
*   **Purpose:** Serves as a local environment template for development and deployments.
*   **Fields:** Credentials and environment settings (e.g. `DB_PASSWORD`, `SECRET_KEY`).
*   **Default values:** Dummy/placeholder structures only.
*   **Validation rules:** Standard shell format.
*   **Dependencies:** Shell runtime and `config.yaml` setup.
*   **Future extensions:** Automated `.env` validation scripts.

---

## 9. `client_profiles.json`
*   **Purpose:** Contains profile definitions mapping specific hardware performance limitations and connection speeds (e.g., IoT node vs. Desktop workstation).
*   **Fields:**
    *   `profiles` (list of objects):
        *   `profile_name` (string): Profile name.
        *   `cpu_capacity` (float): Relative CPU speed.
        *   `memory_capacity_mb` (integer): Memory limit.
        *   `network_speed_kbps` (float): Bandwidth limit.
*   **Default values:** Evaluated dynamically.
*   **Validation rules:**
    *   All capacity values must be positive.
*   **Dependencies:** Used by telemetry simulation profiles in `IExperimentRunner`.
*   **Future extensions:** Integration with actual cgroup settings for local node emulation.

---

## 10. `privacy_profiles.json`
*   **Purpose:** Defines differential privacy parameters, encryption parameters, and security requirements matching legal or user constraints.
*   **Fields:**
    *   `profiles` (list of objects):
        *   `tier_name` (string): Tier name.
        *   `security_level` (string): Encryption type (`fhe`, `sec_agg`, `plain`).
        *   `noise_multiplier` (float): DP scale factor.
        *   `fhe_poly_modulus_degree` (integer): FHE scale.
*   **Default values:** Checked against baseline models.
*   **Validation rules:**
    *   `fhe_poly_modulus_degree` must be a power of `2`.
*   **Dependencies:** Input to `IPrivacyEngine` for parameter configurations.
*   **Future extensions:** Dynamic scaling of privacy profiles based on threat level feeds.

---

## 11. `prometheus.yml`
*   **Purpose:** Controls Prometheus scraping jobs, endpoints, paths, intervals, and authentication rules.
*   **Fields:**
    *   `global` (object): Ingestion rates.
    *   `scrape_configs` (list of objects): Target scrapers.
*   **Default values:** Default Prometheus schema.
*   **Validation rules:** Valid Prometheus YAML layout.
*   **Dependencies:** Prometheus container/daemon instance.
*   **Future extensions:** Service-discovery integrations.

---

## 12. Grafana Provisioning
*   **Purpose:** Automates dashboard layout files configuration and data source setups for Grafana.
*   **Fields:**
    *   `datasources` (object): Setup mapping pointing Grafana to Prometheus databases.
    *   `dashboards` (object): Provider configurations pointing to static JSON layouts.
*   **Default values:** Standard provisioning templates.
*   **Validation rules:** Valid Grafana YAML structure.
*   **Dependencies:** Grafana container runtime.
*   **Future extensions:** Automated dashboard updates via Grafana API.
