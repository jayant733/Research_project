from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import health, federation, clients, metrics, telemetry
from backend.websocket.manager import ws_router

app = FastAPI(title="RATC Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(federation.router)
app.include_router(clients.router)
app.include_router(metrics.router)
app.include_router(telemetry.router)
app.include_router(ws_router)
