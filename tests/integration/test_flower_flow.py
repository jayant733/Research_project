# tests/integration/test_flower_flow.py
# Technical Explanation: Verifies decoupled distributed orchestration
# runs successfully over localhost threads using FlowerFederation adapters.

import threading
import time

import numpy as np

from packages.common.client import GenericClient
from packages.common.fedavg_aggregator import FedAvgAggregator
from packages.common.generic_strategy import GenericStrategy
from packages.common.mock_model import MockModel
from packages.flower.federation import FlowerFederation


def test_flower_federated_flow() -> None:
    """Runs a single round of federated training using decoupled interfaces."""
    port = 8088
    server_address = f"127.0.0.1:{port}"

    # 1. Instantiate Server dependencies
    initial_weights = [np.array([1.0, 2.0, 3.0], dtype=np.float32)]
    aggregator = FedAvgAggregator()
    strategy = GenericStrategy(
        initial_parameters=initial_weights, aggregator=aggregator
    )

    federation = FlowerFederation()

    # Start the Server thread
    server_thread = threading.Thread(
        target=federation.start_server, args=(server_address, 1, strategy), daemon=True
    )
    server_thread.start()
    time.sleep(2.0)

    # 2. Instantiate Client dependencies
    model = MockModel()
    client = GenericClient(model=model)

    # Run the client loop (blocking)
    federation.start_client(server_address=server_address, client=client)

    # 3. Assert client weights are successfully updated to [2.0, 3.0, 4.0]
    np.testing.assert_array_almost_equal(
        model.get_weights()[0], np.array([2.0, 3.0, 4.0], dtype=np.float32)
    )
