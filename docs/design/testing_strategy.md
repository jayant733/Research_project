# Testing Strategy

This document establishes the testing strategy, test classifications, coverage targets, and validation workflows for the RATC project.

---

## 1. Test Classifications

### Unit Tests
*   **Target:** Isolated components without external dependencies (mocked interfaces).
*   **Focus Areas:**
    *   `IPrivacyEngine`: Ensure correct mathematical properties of noise additions (LDP verification) and key generation parameters.
    *   `IScheduler`: Verify the TOPSIS scoring logic mathematically by passing fixed telemetry profiles.
    *   `IConfigurationLoader`: Validate JSON/YAML parsing errors and fallback values.

### Integration Tests
*   **Target:** Interactions between multiple internal modules.
*   **Focus Areas:**
    *   Verify the flow between the Flower client wrappers, local model training loops, and the privacy engine (FHE encryption and weight transfers).
    *   Verify the flow from telemetry polling to scheduler ingestion, followed by tier routing.

### Simulation Tests
*   **Target:** Automated execution of multi-client federated training rounds within Docker networks.
*   **Focus Areas:**
    *   Verify model convergence on non-IID partitioned datasets under dynamic scheduler updates.

### Stress & Performance Tests
*   **Target:** Scalability and stability limits of the system.
*   **Focus Areas:**
    *   **Client Scale:** Scale client containers (e.g., from 10 to 100) to find communication bottle-necks on gRPC channels.
    *   **Memory Profiling:** Monitor RAM/VRAM usage during FHE operations to prevent Out-of-Memory (OOM) failures.

### Fault Injection
*   **Target:** Resilience against runtime errors.
*   **Focus Areas:**
    *   Inject artificial network dropouts (using traffic control containers) to verify that Flower strategy retry limits work correctly.
    *   Pass corrupt/empty telemetry vectors to verify that the Scheduler falls back to the rule-based heuristic policy.

### Security Tests
*   **Target:** Data privacy and network security checks.
*   **Focus Areas:**
    *   Verify that plain model weights are never transmitted over network sockets (all communications must be encrypted with FHE/SecAgg, or protected with DP noise).
    *   Verify SSL/TLS authentication and certificate validation on all client-server connections.

### Acceptance Tests (DoD Verification)
*   **Target:** Ensuring system behavior matches all expectations before release.
*   **Focus Areas:**
    *   Verify that resource-aware tiered clustering delivers higher training accuracy compared to plain FHE FL, while consuming less overall energy and bandwidth.

---

## 2. Coverage Goals & Automation

*   **Code Coverage Target:**
    *   Minimum **80%** line coverage across the core Python codebase (`src/`).
    *   Minimum **90%** coverage for critical packages (`src/crypto/` and `src/server/scheduler/`).
*   **CI/CD Pipeline Integration:**
    *   Unit and integration tests run automatically on every Pull Request.
    *   Code coverage metrics are computed using `pytest-cov` and posted to the PR checklist.
    *   Stress and performance tests are executed on release branch merges.
