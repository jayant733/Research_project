from fastapi import APIRouter, BackgroundTasks

from backend.services.simulation import simulate_round
from backend.services.state import state

router = APIRouter(prefix="/api/v1/round")


@router.post("/start")
async def start_round(background_tasks: BackgroundTasks):
    background_tasks.add_task(simulate_round)
    return {"message": "Round started"}


@router.get("/status")
def round_status():
    return {"current_round": state.current_round, "total_rounds": state.total_rounds}


@router.get("/history")
def round_history():
    return state.view()["history"]
