# Database Design

This document details the relational schemas, timeseries tables, relationships, indexes, constraints, and data retention rules for the databases in the RATC project.

---

## 1. Relational Database Schema (PostgreSQL)
Used for managing configuration parameters, experiment profiles, and global model training results.

### Table: `experiments`
*   **Purpose:** Tracks metadata for benchmarking simulation runs.
*   **Columns:**
    *   `id` (UUID, Primary Key): Unique experiment identifier.
    *   `name` (VARCHAR(128), NOT NULL): Human-readable name.
    *   `started_at` (TIMESTAMP, DEFAULT NOW()): Initialization timestamp.
    *   `completed_at` (TIMESTAMP, NULL): Completion timestamp.
    *   `config_snapshot` (JSONB, NOT NULL): Copy of the loaded `experiment_config.json` at run start.

### Table: `rounds`
*   **Purpose:** Logs outcomes of each training round.
*   **Columns:**
    *   `id` (BIGSERIAL, Primary Key): Unique round record index.
    *   `experiment_id` (UUID, Foreign Key -> `experiments.id` ON DELETE CASCADE): Link to parent experiment.
    *   `round_number` (INTEGER, NOT NULL): The sequence index of the round.
    *   `global_loss` (DOUBLE PRECISION, NOT NULL): Combined global training loss.
    *   `global_accuracy` (DOUBLE PRECISION, NOT NULL): Global classification accuracy.
    *   `duration_seconds` (DOUBLE PRECISION, NOT NULL): Total time elapsed during the round.
*   **Constraints:**
    *   `unique_experiment_round`: Unique constraint on `(experiment_id, round_number)`.
    *   `accuracy_range`: Check constraint `global_accuracy BETWEEN 0.0 AND 1.0`.

---

## 2. Timeseries Database Schema (TimescaleDB / Prometheus)
Used for high-frequency telemetry metrics and client-side profiling.

### Hypertable: `client_telemetry`
*   **Purpose:** Ingests resource metrics from active client nodes.
*   **Columns:**
    *   `timestamp` (TIMESTAMPTZ, NOT NULL): Ingestion time (partition key).
    *   `client_id` (VARCHAR(64), NOT NULL): Client node identifier.
    *   `round_number` (INTEGER, NOT NULL): Current round index.
    *   `cpu_utilization` (REAL, NOT NULL): CPU usage percentage.
    *   `memory_used_mb` (REAL, NOT NULL): Memory usage in MB.
    *   `network_bandwidth_kbps` (REAL, NOT NULL): Current network transmission rate.
    *   `battery_percentage` (REAL, NOT NULL): Battery level.
    *   `assigned_tier` (VARCHAR(32), NOT NULL): Scheduling assignment (e.g. `fhe`, `sec_agg`, `plain`).
*   **Constraints:**
    *   `cpu_range`: Check `cpu_utilization >= 0.0`.
    *   `battery_range`: Check `battery_percentage BETWEEN 0.0 AND 100.0`.

---

## 3. Indexes & Performance Optimization

*   **`idx_rounds_experiment`:** Index on `rounds (experiment_id, round_number)`. Speeds up retrieval of round-by-round charts.
*   **`idx_telemetry_client_time`:** Composite index on timeseries table `client_telemetry (client_id, timestamp DESC)`. Speeds up retrieval of a client's historical telemetry charts.
*   **`idx_telemetry_timestamp`:** Partitioning index on `client_telemetry (timestamp DESC)`. Speeds up real-time analytics dashboards.

---

## 4. Retention Policy

*   **Configurations and Experiment Results (`experiments`, `rounds`):**
    *   *Retention:* Permanent. These records are lightweight and essential for paper plots, statistics, and historical analysis.
*   **High-Frequency Telemetry (`client_telemetry`):**
    *   *Retention:* **30 Days**.
    *   *Mechanism:* TimescaleDB data retention policies drop old partition chunks automatically after 30 days to free up system disk space.
    *   *Downsampling:* Telemetry metrics older than 30 days are aggregated into daily averages (minimum, maximum, average CPU/memory usage per client) and stored in a compressed `client_telemetry_daily_summary` table.
