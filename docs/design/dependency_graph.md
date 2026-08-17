# System Dependency Graphs & Sequences

This document maps out package, module, import, and runtime dependencies, along with system lifecycles and communication paths for the Resource-Aware Tiered Clustering (RATC) project. It establishes structural isolation to ensure there are **no cyclic dependencies**.

---

## 1. Package Dependency Graph
The high-level coupling between directory modules. System dependency is unidirectional, flowing down to core utilities (`monitoring`, `config`, `datasets`).

```mermaid
graph TD
    %% Nodes
    runner["experiments (IExperimentRunner)"]
    backend["backend (IDashboardService)"]
    flower["flower (IFlowerClient, IFlowerServer, IAggregator)"]
    sched["scheduler (IScheduler)"]
    crypto["crypto (IPrivacyEngine)"]
    train["training (ITrainingEngine)"]
    datasets["datasets"]
    monitor["monitoring (ILogger, ITelemetryProvider)"]
    cfg["config (IConfigurationLoader)"]

    %% Dependencies
    runner --> flower
    runner --> backend
    runner --> cfg
    
    backend --> monitor
    backend --> cfg

    flower --> crypto
    flower --> train
    flower --> sched
    flower --> monitor

    sched --> monitor
    sched --> cfg

    crypto --> monitor
    
    train --> datasets
    train --> monitor

    monitor --> cfg
```

---

## 2. Module Dependency Graph
The relationship within modules showing how concrete implementations depend exclusively on interfaces.

```mermaid
graph LR
    subgraph Scheduler Module
        ISched["IScheduler (Interface)"]
        TopsisSched["TopsisScheduler (Concrete)"]
        RlSched["RlScheduler (Concrete)"]
        TopsisSched --> ISched
        RlSched --> ISched
    end

    subgraph Cryptography Module
        IPriv["IPrivacyEngine (Interface)"]
        CkkPriv["CkkPrivacyEngine (Concrete)"]
        CkkPriv --> IPriv
    end

    subgraph Client Engine Module
        ITrain["ITrainingEngine (Interface)"]
        PyTorchTrain["PyTorchTrainingEngine (Concrete)"]
        PyTorchTrain --> ITrain
    end
```

---

## 3. Import Dependency Graph
Guidelines for Python file imports to prevent circular importing.

```
[Concrete Client Code]
     │
     ▼ (imports)
[Module Interfaces]
     │
     ▼ (imports)
[Data Containers / Dataclasses] (e.g. TelemetryVector, ModelUpdate)
     │
     ▼ (imports)
[Standard Types / typing]
```
*Rule:* Modules never import concrete classes from other modules directly. They only import interfaces or data model definitions (e.g., `TelemetryVector`).

---

## 4. Runtime Dependency Graph
Defines data flows and interactions between running instances.

```mermaid
graph LR
    Server["Flower Server"]
    Client["Flower Client"]
    Sched["Scheduler"]
    Telemetry["Telemetry Provider"]
    Privacy["Privacy Engine"]
    Training["Training Engine"]

    Server -- 1. Requests Telemetry --> Client
    Client -- 2. Harvests Metrics --> Telemetry
    Client -- 3. Sends Telemetry --> Server
    Server -- 4. Evaluates Assignments --> Sched
    Server -- 5. Broadcasts Tier Weights --> Client
    Client -- 6. Obtains Privacy Bounds --> Privacy
    Client -- 7. Trains Model --> Training
    Client -- 8. Applies Noise/FHE --> Privacy
    Client -- 9. Returns Updates --> Server
```

---

## 5. System Initialization Order
The sequence of object instantiations when booting a node.

```mermaid
stateDiagram-v2
    [*] --> 1_LoadConfiguration: Load config files via IConfigurationLoader
    1_LoadConfiguration --> 2_InitializeLogger: Instantiate ILogger using logging configurations
    2_InitializeLogger --> 3_PrepareDataLoaders: Mount datasets & data loaders
    3_PrepareDataLoaders --> 4_SetupPrivacyEngine: Initialize IPrivacyEngine keys
    4_SetupPrivacyEngine --> 5_StartTelemetryProvider: Spawn ITelemetryProvider metrics loop
    5_StartTelemetryProvider --> 6_InstantiateClientServer: Load Client / Server execution layers
    6_InstantiateClientServer --> [*]
```

---

## 6. Service Startup Order
The sequence in which independent Docker containers and backend processes are spun up.

```mermaid
sequenceDiagram
    autonumber
    participant DB as Metrics Database
    participant Prom as Prometheus
    participant Srv as Flower Server Orchestrator
    participant Dash as Dashboard Service
    participant Cli as Flower Clients

    Note over DB,Cli: Docker Compose Up Command
    DB->>DB: Start database daemon, mount volumes, open ports
    Prom->>DB: Boot, verify connection database, start telemetry scraper
    Srv->>Prom: Boot, verify network interfaces, open socket ports
    Dash->>Prom: Boot dashboard server, verify Prometheus datasource
    Cli->>Srv: Connect socket channels, request registration
```

---

## 7. Shutdown Order
The sequence for executing clean teardowns of running processes to avoid data corruption or resource locks.

```mermaid
sequenceDiagram
    autonumber
    participant Cli as Flower Clients
    participant Srv as Flower Server Orchestrator
    participant Dash as Dashboard Service
    participant Prom as Prometheus
    participant DB as Metrics Database

    Note over Cli,DB: SIGINT / SIGTERM Received
    Cli->>Cli: Complete/Interrupt epoch, release GPU memory, close connections
    Cli->>Srv: Deregister and exit process
    Srv->>Srv: Close socket servers, save final weights
    Dash->>Dash: Close HTTP listener
    Prom->>Prom: Persist scrapers buffer to DB
    DB->>DB: Sync write buffers to disk, close db connection sockets
```

---

## 8. Communication Graph
The channels and protocols through which components share data.

```mermaid
graph TD
    Client["Flower Client Node"]
    Server["Flower Server Node"]
    DB["Metrics Database"]
    Prom["Prometheus Collector"]
    Grafana["Grafana Dashboards"]

    Client <-->|gRPC / Flower Protocol| Server
    Client -.->|HTTP GET metrics endpoint| Prom
    Server -.->|HTTP GET metrics endpoint| Prom
    Prom --->|SQL Ingestion| DB
    Grafana ===>|Query HTTP API| Prom
```
*Note:* Dashed lines represent scrape queries, solid lines indicate data transport, and triple lines represent client-facing queries.
