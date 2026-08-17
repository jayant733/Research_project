# Benchmark Plan

This document establishes the benchmarking plan, measurement methodologies, and performance comparison criteria for evaluating plain federated learning against different privacy and scheduling setups.

---

## 1. Benchmarking Targets

*   **Plain FL (FedAvg):** Standard baseline running without privacy constraints.
*   **Differential Privacy (LDP):** Gradient perturbation baseline running with DP parameters enabled.
*   **Secure Aggregation (SecAgg):** Cryptographic masking baseline using secure multi-party configurations.
*   **Adaptive Scheduler (RATC):** Dynamic tier routing scheduler assigning nodes based on real-time cgroup telemetry profiles.

---

## 2. Target Metrics & Measurement Methods

| Metric | Target | Measurement Method |
| :--- | :--- | :--- |
| **Accuracy** | Model performance comparisons | Percentage of correct classifications evaluated on test datasets. |
| **Latency** | Network delay indicators | Round trip time (RTT) from server packet dispatch to response reception. |
| **Bandwidth** | Sockets transmission loads | Byte count monitoring on server gRPC ports via `iftop` / `tcpdump`. |
| **Training Time** | Local execution overhead | Millisecond timers tracking local `ITrainingEngine.train_epoch` steps. |
| **CPU** | Processor utilization | Thread profiling reading cgroup CPU quota files inside the containers. |
| **Memory** | RAM/VRAM utilization | Peak usage tracking reading `memory.max_usage_in_bytes` / CUDA metrics. |
| **Communication Cost**| Network payload volume | Total bytes transmitted during weights synchronization per round. |
| **Energy** | Battery consumption profile | Simulated discharge curves linked to CPU/GPU time metrics. |
| **Privacy** | Privacy budget leakage | Quantitative tracking of cumulative privacy loss ($\epsilon, \delta$) over rounds. |

---

## 3. Benchmarking Methodology

### Environment Setup
*   **Containers:** Spin up 1 server container and a fleet of 20 client containers using Docker Compose.
*   **Heterogeneous Emulation:** Map client profiles (`client_profiles.json`) onto container resource limits:
    *   *High-tier clients (Desktop):* Unlimited CPU/RAM.
    *   *Mid-tier clients (Mobile):* 1 CPU core, 1GB RAM limit.
    *   *Low-tier clients (IoT):* 0.25 CPU core, 256MB RAM limit.

### Benchmark Phases
1.  **Warm-up:** Run 2 initialization rounds to cache datasets and establish connection sockets.
2.  **Execution Run:** Execute 50 federated rounds under each benchmarking target.
3.  **Measurement Harvesting:** During runs, the telemetry harvester writes data to the TimescaleDB database.
4.  **Export:** Metrics database tables are exported to CSV logs in the `experiments/logs/` folder.

---

## 4. Evaluation Criteria & Comparison Matrix

*   **Trade-off Index:** A composite efficiency score calculated as:
    $$\text{Efficiency} = \frac{\text{Accuracy}}{\text{Communication Cost} \times \text{Average Latency}}$$
*   **Resilience Evaluation:** Compute model convergence rates under simulated client connection failures (e.g. terminating 20% of client containers during active training rounds).
