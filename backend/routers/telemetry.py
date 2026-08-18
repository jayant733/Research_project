from fastapi import APIRouter
from backend.models.schemas import TelemetryPush
from backend.services.state import state

router = APIRouter(prefix="/api/v1/telemetry")

@router.post("/push")
def push_telemetry(data: TelemetryPush):
    if data.client_id in state.clients:
        state.clients[data.client_id]["telemetry"] = data.model_dump()
    return {"status": "received"}
