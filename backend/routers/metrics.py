from fastapi import APIRouter
from backend.services.state import state
from backend.models.schemas import SystemStatus
from collections import Counter

router = APIRouter(prefix="/api/v1")

@router.get("/metrics/live")
def get_live_metrics():
    if not state.metrics_history:
        return {}
    return state.metrics_history[-1]

@router.get("/status", response_model=SystemStatus)
def get_status():
    tier_counts = Counter(c.get("tier") for c in state.clients.values() if c.get("tier"))
    return SystemStatus(
        current_round=state.current_round,
        total_rounds=state.total_rounds,
        active_clients=len(state.clients),
        clients_per_tier=dict(tier_counts)
    )
