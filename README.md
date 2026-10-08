# Adaptive Privacy Orchestrator

RATC is a local, reproducible Flower system that assigns each client a privacy mechanism from its resource profile and measured fit time:

- High-capacity clients use CKKS fully homomorphic encryption (TenSEAL). The server adds ciphertexts and decrypts only the aggregate.
- Medium clients use demonstrator pairwise secure aggregation. Masks cancel when every assigned client reports. There is no dropout recovery.
- Constrained clients add calibrated Gaussian noise to the model update. Opacus accounts for the spent epsilon.

The same run is visible in the control center: tiers, migrations, accuracy, loss, fit time, upload size, and epsilon come from the live Flower session.

This is not a claim to be the first resource-aware or tiered federated-learning system. Fed-RAC, TV-FedAvg, HERL, OFL, M2FDP, and FedPHE already cover parts of that space. The working contribution here is the open orchestration loop that routes one model across those three mechanisms and records the tradeoff.

## Run the control center

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
python -m backend.demo
```

Open http://localhost:8080. Choose a seed and round count, then start a live run. The default fleet is two workstations, two mobiles, and two IoT profiles. Export JSON or CSV after the run.

`make demo` starts the same server. `make docker-dev-up` builds the single demo container and serves the same UI on port 8080.

## Reproduce a comparison

```bash
python scripts/run_experiment.py
```

This writes `experiments/logs/comparison.csv`, `summary.json`, and `comparison.svg` for plain FedAvg, random tiers, static tiers, and RATC. Numbers in that folder are produced by the run; they are not stored as paper results.

## Tests

```bash
pytest tests/unit tests/integration
```

## Limits

Read [docs/design/threat_model.md](docs/design/threat_model.md) before describing the privacy guarantees. Secure aggregation is explicitly demonstrator-grade. The dashboard and the training clients share one machine, so device class is a seeded profile; fit time is measured.
