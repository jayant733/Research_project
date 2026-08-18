from fastapi import APIRouter
from backend.services.state import state
from backend.models.schemas import ClientRegistration

router = APIRouter(prefix="/api/v1/clients")

@router.get("")
def get_clients():
    return state.clients

@router.post("/register")
def register_client(client: ClientRegistration):
    state.clients[client.client_id] = {
        "profile": client.profile,
        "tier": None,
        "telemetry": None
    }
    return {"message": "Registered", "client": state.clients[client.client_id]}
