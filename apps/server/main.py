# apps/server/main.py
import sys
from typing import Dict

import flwr as fl

from packages.common.generic_strategy import GenericStrategy
from packages.common.real_model import RealModel
from packages.flower.strategy_adapter import FlowerStrategyAdapter
from packages.training.providers.pytorch.healthcare_model import HealthcareMLP


def main() -> None:
    print("Starting Flower Server Node...", flush=True)

    # 1. Initialize global model for initial parameters
    torch_model = HealthcareMLP(input_dim=15)
    global_model = RealModel(torch_model, device="cpu")
    initial_weights = global_model.get_weights()

    # 2. Initialize framework-agnostic strategy
    from packages.common.fedavg_aggregator import FedAvgAggregator
    aggregator = FedAvgAggregator()
    generic_strategy = GenericStrategy(initial_parameters=initial_weights, aggregator=aggregator)

    # 3. Adapt to Flower framework
    flower_strategy = FlowerStrategyAdapter(generic_strategy)

    # 4. Start Server
    print("Binding Flower Server to 0.0.0.0:8081...", flush=True)
    try:
        fl.server.start_server(
            server_address="0.0.0.0:8081",
            config=fl.server.ServerConfig(num_rounds=3),
            strategy=flower_strategy,
        )
    except Exception as e:
        print(f"Server execution failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
