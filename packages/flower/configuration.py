# packages/flower/configuration.py
# Technical Explanation: Encapsulates specific Flower-related configuration parameters.

from dataclasses import dataclass


@dataclass
class FlowerConfiguration:
    """Contains Flower-specific configuration parameters."""

    server_address: str
    num_rounds: int
    min_fit_clients: int
    min_available_clients: int
