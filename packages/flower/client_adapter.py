# packages/flower/client_adapter.py
# Technical Explanation: Implements Adapter Pattern mapping flwr.client.NumPyClient
# to IGenericClient.
# Converts raw configurations to RoundContext and parameters to standard list types.

from typing import Any, Dict, List, Tuple

import flwr as fl
import numpy as np

from packages.common.client_interface import IGenericClient
from packages.common.context import RoundContext


class FlowerClientAdapter(fl.client.NumPyClient):
    """Adapts a generic business client instance to Flower's requirements."""

    def __init__(self, generic_client: IGenericClient) -> None:
        self.generic_client = generic_client

    def get_parameters(self, config: Dict[str, Any]) -> List[np.ndarray[Any, Any]]:
        """Delegates parameters retrieval to the generic client."""
        context = RoundContext(current_round=0, config=config)
        return self.generic_client.get_parameters(context)

    def fit(
        self, parameters: List[np.ndarray[Any, Any]], config: Dict[str, Any]
    ) -> Tuple[List[np.ndarray[Any, Any]], int, Dict[str, Any]]:
        """Maps client fit calls to the generic client using RoundContext."""
        current_round = int(config.get("server_round", 0))
        context = RoundContext(current_round=current_round, config=config)
        return self.generic_client.fit(parameters, context)

    def evaluate(
        self, parameters: List[np.ndarray[Any, Any]], config: Dict[str, Any]
    ) -> Tuple[float, int, Dict[str, Any]]:
        """Maps client evaluate calls to the generic client."""
        current_round = int(config.get("server_round", 0))
        context = RoundContext(current_round=current_round, config=config)
        return self.generic_client.evaluate(parameters, context)
