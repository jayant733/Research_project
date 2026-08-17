# Adaptive Privacy Orchestrator

This repository implements the **Resource-Aware Tiered Clustering (RATC)** framework for heterogeneous privacy-preserving federated learning.

## Repository Layout
* `apps/`: Executable binaries and runtime entries (Client, Server, Dashboard).
* `packages/`: Modular logic cores (Telemetry Provider, Scheduler, Cryptography, Common).
* `configs/`: YAML, JSON, and profile configuration templates.
* `docker/`: Dockerfiles and orchestration configuration.
* `docs/`: System design, sprint planning, and API specifications.
* `tests/`: Automated unit, integration, and performance benchmarks.

## Prerequisites
* Python 3.10+
* Virtual Environment (recommended)

## Quickstart Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
2. Install development dependencies:
   ```bash
   pip install -e .[dev]
   ```
3. Run code check tools:
   ```bash
   black --check .
   ruff check .
   mypy .
   ```
