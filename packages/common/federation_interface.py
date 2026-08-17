# packages/common/federation_interface.py
# Technical Explanation: Declares generic distributed orchestration platforms.

from abc import ABC, abstractmethod

from packages.common.client_interface import IGenericClient
from packages.common.strategy_interface import IFederationStrategy


class IFederation(ABC):
    """Abstract interface exposing server-client start hooks.

    Decoupled from libraries.
    """

    @abstractmethod
    def start_server(
        self, server_address: str, num_rounds: int, strategy: IFederationStrategy
    ) -> None:
        """
        Starts the federated orchestration server.

        Inputs:
            server_address: IP/port string to listen on.
            num_rounds: Number of rounds to run.
            strategy: Custom aggregation strategy.
        """
        pass

    @abstractmethod
    def start_client(self, server_address: str, client: IGenericClient) -> None:
        """
        Starts and connects a federated client node.

        Inputs:
            server_address: Destination server socket IP/port.
            client: Standardized generic client logic wrapper.
        """
        pass
