# packages/flower/server_interface.py
# Technical Explanation: Declares standard interfaces for the Flower Server wrapper.

from abc import ABC, abstractmethod
from typing import Any


class IFlowerServer(ABC):
    """Abstract interface defining the execution loop for the federated server."""

    @abstractmethod
    def start_listeners(
        self, server_address: str, num_rounds: int, strategy: Any
    ) -> None:
        """
        Starts the Flower gRPC listener socket and orchestrates training rounds.

        Inputs:
            server_address: IP:port string where the server will bind.
            num_rounds: Total rounds of federated training to run.
            strategy: Flower strategy class (e.g. FedAvg).
        Outputs:
            None.
        Exceptions:
            SocketBindingError: Raised if the target ports are in use.
        """
        pass
