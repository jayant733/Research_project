# Experiment Design

This document designs the experimental protocols, variables, metrics, graphs, statistical tests, and validation methodologies for evaluating the Resource-Aware Tiered Clustering (RATC) framework. The designs are formulated to match IEEE publication standards.

---

## 1. Experimental Sub-Protocols

### Baseline Experiments
*   **Goal:** Establish standard execution parameters without resource constraints or scheduler tiering.
*   **Protocols:**
    *   **Baseline A (Plain FL):** Flower training using vanilla FedAvg with no privacy mechanics or telemetry monitoring.
    *   **Baseline B (Homogeneous FHE FL):** Flower training forcing FHE (CKKS) across all nodes, regardless of hardware resource capabilities.

### Differential Privacy (DP) Experiments
*   **Goal:** Quantify the trade-off between model accuracy and privacy budgets.
*   **Protocols:**
    *   Measure global model convergence accuracy across varying values of the privacy parameter $\epsilon$ (ranging from $0.1$ to $10.0$) and delta $\delta = 10^{-5}$.
    *   Vary the gradient clipping thresholds to optimize utility.

### Secure Aggregation (SecAgg) Experiments
*   **Goal:** Analyze computation overhead and mask generation latencies.
*   **Protocols:**
    *   Measure execution times for key exchange and secret sharing steps under varying client pool sizes.

### Scheduler Experiments
*   **Goal:** Evaluate scheduling policy effectiveness.
*   **Protocols:**
    *   Compare the TOPSIS scoring assignment policy against:
        1.  *Random Assignment:* Grouping clients to tiers randomly.
        2.  *Static Partitioning:* Assigning clients based on fixed initial configurations.
        3.  *Reinforcement Learning (RL) Policy:* Training scheduler decisions via RL feedback.

### Telemetry Experiments
*   **Goal:** Verify accuracy of telemetry metrics harvesting and simulated resource limits.
*   **Protocols:**
    *   Artificially restrict Docker containers (e.g. throttling CPU execution to 10% or limiting memory to 256MB).
    *   Verify if `ITelemetryProvider` catches resource limits and translates them into appropriate routing decisions.

---

## 2. Metrics & Graph Layouts

### Primary Performance Indicators (KPIs)
*   **Model Performance:** Accuracy, F1-score, and convergence rate (rounds to target accuracy).
*   **Resource Footprint:** Memory consumption (MB), network data transferred (MB), and CPU utilization.
*   **Energy Overhead:** Battery depletion rate per training epoch.

### Projected IEEE Graph Layouts
*   **Figure 1: Accuracy vs. Communication Rounds:** x-axis = Communication Rounds [0-100]; y-axis = Accuracy [0.0-1.0]. Plots lines for Plain FL, Homogeneous FHE, and RATC.
*   **Figure 2: Energy Consumption vs. Time:** x-axis = Cumulative Time (seconds); y-axis = Total Joules/Battery depleted. Compares Homogeneous FHE vs. RATC.
*   **Figure 3: Scheduler Stability Matrix:** Heatmap showing client resource changes on the y-axis and tier transitions on the x-axis.

---

## 3. Statistical Validation Tests

*   **T-Tests & ANOVA:**
    *   Apply two-sample t-tests to compare convergence speed differences between homogeneous systems and RATC.
    *   Apply ANOVA tests to determine if scheduler policy variations (TOPSIS, RL, Heuristic) yield statistically significant performance differences.
*   **Wilcoxon Signed-Rank Test:**
    *   Used as a non-parametric test to compare paired accuracy differences across heterogeneous execution runs.

---

## 4. Threats to Validity & Mitigation

*   **Internal Validity:** Client dropouts or networking fluctuations skewing metrics.
    *   *Mitigation:* Run each simulation 10 times with different random seeds and report confidence intervals (95% CI).
*   **External Validity:** Synthetic simulation environments may not match actual hardware behaviors.
    *   *Mitigation:* Validate the telemetry extraction on physical resource-constrained nodes (e.g. Raspberry Pi) to verify container-limit readings.
*   **Construct Validity:** Choosing inappropriate TOPSIS weights can distort routing performance.
    *   *Mitigation:* Run sensitivity analyses across varying weight weights to identify optimal assignments.

---

## 5. Expected Outcomes

*   **Convergence Trade-offs:** RATC is expected to converge up to **40% faster** than homogeneous FHE FL, while maintaining model accuracy within 1.5% of plain FL.
*   **Resource Utilization:** Bandwidth and energy consumption on resource-constrained nodes are expected to drop by **50% or more** by routing them to DP or SecAgg pools instead of FHE pipelines.
