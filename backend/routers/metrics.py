from fastapi import APIRouter

from backend.services.state import state

router = APIRouter(prefix="/api/v1")


@router.get("/metrics/live")
def get_live_metrics():
    if not state.metrics_history:
        return {}
    return state.metrics_history[-1]


@router.get("/status")
def get_status():
    return state.view()
