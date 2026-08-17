# API Contracts

This document defines the structural interfaces and payloads for all REST, gRPC, and internal system communication APIs within the RATC project.

---

## 1. REST APIs (Dashboard Services)

### Endpoint: `GET /api/v1/metrics/summary`
*   **Purpose:** Fetches the aggregated performance summary of the current federated learning round (loss, accuracy, round speed, and active client count).
*   **Authentication:** Bearer JWT Token required in Header.
*   **Request Parameters:**
    *   `round_id` (integer, optional): Target round index.
*   **Response (200 OK):**
    ```json
    {
      "round_id": 12,
      "global_loss": 0.345,
      "global_accuracy": 0.892,
      "elapsed_seconds": 45.2,
      "active_clients": 15
    }
    ```
*   **Validation:** `round_id` must be positive.
*   **Error Codes:**
    *   `401 Unauthorized`: Token missing/expired.
    *   `404 Not Found`: Target round data not yet generated.

### Endpoint: `POST /api/v1/experiment/start`
*   **Purpose:** Triggers a new automated benchmark simulation.
*   **Authentication:** Admin Api-Key in Header.
*   **Request Payload:**
    ```json
    {
      "config_file": "config/experiment_config.json",
      "override_rounds": 100
    }
    ```
*   **Response (202 Accepted):**
    ```json
    {
      "experiment_id": "exp-9902-ff2",
      "status": "queued"
    }
    ```
*   **Validation:** `config_file` must represent a valid path; `override_rounds` must be in range `[1, 1000]`.
*   **Error Codes:**
    *   `400 Bad Request`: Invalid configuration paths.
    *   `403 Forbidden`: Insufficient user permissions.

---

## 2. gRPC APIs (Flower Integration & Telemetry)

### Service: `TelemetryCollector`
*   **gRPC Method:** `SendTelemetry`
*   **Purpose:** Clients stream their harvested cgroup telemetry to the Server at the start of a round.
*   **Authentication:** Client TLS Certificate validation.
*   **Request Message:**
    ```protobuf
    message TelemetryRequest {
      string client_id = 1;
      float cpu_usage = 2;
      float memory_used_mb = 3;
      float network_bandwidth_kbps = 4;
      float battery_percentage = 5;
    }
    ```
*   **Response Message:**
    ```protobuf
    message TelemetryResponse {
      string client_id = 1;
      bool accepted = 2;
    }
    ```
*   **Validation:** All capacity values must be >= 0.0. `battery_percentage` must be in range `[0.0, 100.0]`.
*   **Error Status Codes:**
    *   `INVALID_ARGUMENT`: Missing client ID or out-of-bounds metrics values.
    *   `UNAUTHENTICATED`: TLS verification failed.

---

## 3. Internal APIs (Scheduler, Telemetry, and Cryptography)

### Interface: `IScheduler`
*   **Method:** `evaluate`
*   **Purpose:** Invoked internally on the server to assign clients to privacy pools.
*   **Signature:**
    ```python
    def evaluate(
        telemetry: Dict[str, TelemetryVector], 
        constraints: Dict[str, ConstraintVector]
    ) -> Dict[str, PrivacyTier]:
        pass
    ```
*   **Validation:**
    *   Both inputs must be non-empty.
    *   `TelemetryVector` fields must not contain NaN values.
*   **Exceptions:**
    *   `InvalidTelemetryError`: Thrown if a client's telemetry does not contain necessary metrics keys.
    *   `NoActiveClientsError`: Thrown if the active client mapping is empty.

### Interface: `IPrivacyEngine`
*   **Method:** `encrypt_weights`
*   **Purpose:** Encrypts local weights using homomorphic encryption parameters.
*   **Signature:**
    ```python
    def encrypt_weights(weights: List[float]) -> Ciphertext:
        pass
    ```
*   **Validation:** `weights` must match the pre-configured model layer sizing constraints.
*   **Exceptions:**
    *   `ScaleOutOfRangeError`: Thrown if FHE parameters scale outside valid bounds.
