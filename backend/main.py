"""Adaptive Privacy Orchestrator control plane."""

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.routers import clients, experiment, federation, health, metrics, telemetry
from backend.services.state import state
from backend.websocket.manager import ws_router

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    state.loop = asyncio.get_running_loop()
    yield


app = FastAPI(title="RATC Control Center", version="1.0.0", lifespan=lifespan)

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
app.include_router(experiment.router)
app.include_router(ws_router)


@app.get("/")
def dashboard() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")


app.mount("/css", StaticFiles(directory=FRONTEND / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND / "js"), name="js")
