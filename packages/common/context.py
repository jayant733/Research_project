# packages/common/context.py
# Technical Explanation: Encapsulates runtime context parameters during
# federated rounds.

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RoundContext:
    """Contains metadata and options passed between server and clients during rounds."""

    current_round: int
    config: Dict[str, Any]
