"""Thread-safe dashboard state for live federated runs."""

import threading
from copy import deepcopy
from typing import Any, Dict, List


class AppState:
    """Stores the latest run, round history, and connected client snapshots."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.clients: Dict[str, Dict[str, Any]] = {}
        self.current_round = 0
        self.total_rounds = 4
        self.metrics_history: List[Dict[str, Any]] = []
        self.running = False
        self.mode = "ratc"
        self.objective = "topsis"
        self.scenario = "none"
        self.seed = 7
        self.source = "live"
        self.message = "Idle. Start a live Flower run to assign privacy tiers."
        self.loop: Any = None

    def reset_run(
        self,
        rounds: int,
        seed: int,
        mode: str,
        objective: str = "topsis",
        scenario: str = "none",
    ) -> None:
        with self._lock:
            self.clients = {}
            self.current_round = 0
            self.total_rounds = rounds
            self.metrics_history = []
            self.running = True
            self.mode = mode
            self.objective = objective
            self.scenario = scenario
            self.seed = seed
            self.source = "live"
            self.message = (
                f"Starting {mode} run with seed {seed}, "
                f"objective {objective}, scenario {scenario}."
            )

    def mark_finished(self, message: str, running: bool = False) -> None:
        with self._lock:
            self.running = running
            self.message = message

    def apply_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Update state from an orchestrator event and return a broadcast payload."""
        payload = deepcopy(event)
        with self._lock:
            kind = str(payload.get("type", ""))
            if kind == "RUN_STARTED":
                self.running = True
                self.message = (
                    "Flower server is connected. Waiting for the first round."
                )
            elif kind == "ROUND_COMPLETED":
                metrics = payload.get("metrics", {})
                self.current_round = int(metrics.get("round", self.current_round))
                self.clients = deepcopy(payload.get("clients", {}))
                self.metrics_history.append(deepcopy(metrics))
                self.message = (
                    f"Round {self.current_round} aggregated "
                    f"{len(self.clients)} live client updates."
                )
            elif kind == "RUN_FINISHED":
                self.running = False
                self.message = "Live run finished. Export the measured round history."
            elif kind == "RUN_FAILED":
                self.running = False
                self.message = str(payload.get("error", "The live run failed."))
            payload["state"] = self._view_unlocked()
        return payload

    def view(self) -> Dict[str, Any]:
        with self._lock:
            return self._view_unlocked()

    def _view_unlocked(self) -> Dict[str, Any]:
        return {
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "active_clients": len(self.clients),
            "clients_per_tier": _tier_counts(self.clients),
            "running": self.running,
            "mode": self.mode,
            "objective": self.objective,
            "scenario": self.scenario,
            "seed": self.seed,
            "source": self.source,
            "message": self.message,
            "clients": deepcopy(self.clients),
            "history": deepcopy(self.metrics_history),
        }


def _tier_counts(clients: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for client in clients.values():
        tier = str(client.get("tier") or "UNASSIGNED")
        counts[tier] = counts.get(tier, 0) + 1
    return counts


state = AppState()
