"""Per-client local differential-privacy spend."""

from typing import Dict, Iterable, Optional


class BudgetLedger:
    """Tracks cumulative epsilon reported by each client."""

    def __init__(self, client_ids: Iterable[str], cap: Optional[float]) -> None:
        self.cap = None if cap is None else float(cap)
        self.spent: Dict[str, float] = {client_id: 0.0 for client_id in client_ids}

    def remaining(self, client_id: str) -> Optional[float]:
        """Return unused epsilon, or None when the run has no cap."""
        if self.cap is None:
            return None
        return max(0.0, self.cap - self.spent.get(client_id, 0.0))

    def blocks_dp(self, client_id: str, floor: float = 0.75) -> bool:
        remaining = self.remaining(client_id)
        return remaining is not None and remaining < floor

    def noise_multiplier(self, client_id: str, sensitivity: float) -> float:
        """Keep the demonstration multiplier until a cap makes the budget bind."""
        if self.cap is None:
            return 0.5
        remaining = self.remaining(client_id) or 0.0
        used = 0.0 if self.cap <= 0 else (self.cap - remaining) / self.cap
        return float(0.5 * (1.0 + float(sensitivity)) * (1.0 + used))

    def note_cumulative(self, client_id: str, epsilon: float) -> None:
        self.spent[client_id] = max(self.spent.get(client_id, 0.0), float(epsilon))
