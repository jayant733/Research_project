# packages/flower/federation.py
# Technical Explanation: Concretizes IFederation for the Flower framework.
# Translates abstract strategy/client instances to Flower-compatible adapters.

import flwr as fl

from packages.common.client_interface import IGenericClient
from packages.common.events import events
from packages.common.federation_interface import IFederation
from packages.common.strategy_interface import IFederationStrategy
from packages.flower.client_adapter import FlowerClientAdapter
from packages.flower.strategy_adapter import FlowerStrategyAdapter


class FlowerFederation(IFederation):
    """Flower platform orchestrator adapting standard structures dynamically."""

    def start_server(
        self, server_address: str, num_rounds: int, strategy: IFederationStrategy
    ) -> None:
        """Adapts the generic strategy and starts the Flower server."""
        events.on_server_start.fire(server_address=server_address)

        # Instantiate adapter strategy, defaulting minimum available clients to 1
        # In real runs, these bounds are controlled by the configuration loaders.
        flower_strategy = FlowerStrategyAdapter(
            generic_strategy=strategy,
            fraction_fit=1.0,
            fraction_evaluate=1.0,
            min_fit_clients=1,
            min_evaluate_clients=1,
            min_available_clients=1,
        )

        server_config = fl.server.ServerConfig(num_rounds=num_rounds)
        fl.server.start_server(
            server_address=server_address,
            config=server_config,
            strategy=flower_strategy,
        )

        events.on_server_stop.fire()

    def start_client(self, server_address: str, client: IGenericClient) -> None:
        """Adapts the generic client and connects to the Flower gRPC listener."""
        flower_client = FlowerClientAdapter(generic_client=client)
        fl.client.start_numpy_client(
            server_address=server_address, client=flower_client
        )

FederatedOrchestrator = FlowerFederation
