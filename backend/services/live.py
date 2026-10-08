"""Start the real Flower session and stream its events to the dashboard."""

import asyncio
import threading
from typing import Any, Dict

from backend.services.state import state
from backend.websocket.manager import manager
from packages.ratc.orchestrator import RunConfig, run_session


def start_live_run(
    rounds: int,
    seed: int,
    mode: str,
    objective: str = "topsis",
    scenario: str = "none",
    budget_epsilon: float | None = None,
    latency_cap: float | None = None,
    forbid_iot_fhe: bool = False,
    secagg_recovery: bool = False,
) -> Dict[str, Any]:
    """Launch one live run. A second request is rejected while it is active."""
    with state._lock:
        if state.running:
            raise RuntimeError("A live run is already in progress.")
    bounded_rounds = max(1, min(int(rounds), 20))
    state.reset_run(bounded_rounds, int(seed), mode, objective, scenario)
    thread = threading.Thread(
        target=_run,
        args=(
            bounded_rounds,
            int(seed),
            mode,
            objective,
            scenario,
            budget_epsilon,
            latency_cap,
            forbid_iot_fhe,
            secagg_recovery,
        ),
        daemon=True,
        name="ratc-live-run",
    )
    thread.start()
    return state.view()


def _run(
    rounds: int,
    seed: int,
    mode: str,
    objective: str,
    scenario: str,
    budget_epsilon: float | None,
    latency_cap: float | None,
    forbid_iot_fhe: bool,
    secagg_recovery: bool,
) -> None:
    try:
        run_session(
            RunConfig(
                mode=mode,
                seed=seed,
                num_rounds=rounds,
                epochs=2,
                objective=objective,
                scenario=scenario,
                budget_epsilon=budget_epsilon,
                latency_cap=latency_cap,
                forbid_iot_fhe=forbid_iot_fhe,
                secagg_recovery=secagg_recovery,
            ),
            on_event=_publish,
        )
    except Exception as exc:
        _publish({"type": "RUN_FAILED", "error": str(exc), "source": "live"})
        state.mark_finished(str(exc))


def _publish(event: Dict[str, Any]) -> None:
    payload = state.apply_event(event)
    loop = state.loop
    if loop is None or not loop.is_running():
        return
    asyncio.run_coroutine_threadsafe(manager.broadcast(payload), loop)
