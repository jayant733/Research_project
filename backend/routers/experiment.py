"""Experiment start and measured-result export."""

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from backend.services.live import start_live_run
from backend.services.state import state

router = APIRouter(prefix="/api/v1")
_MODES = {"ratc", "plain", "random", "static", "reactive", "predictive", "bandit"}
_OBJECTIVES = {"topsis", "privacy", "latency", "upload"}
_SCENARIOS = {"none", "poison", "freerider", "telemetry", "dropout"}


class RunRequest(BaseModel):
    rounds: int = Field(default=4, ge=1, le=20)
    seed: int = Field(default=7, ge=0, le=10_000)
    mode: str = "ratc"
    objective: str = "topsis"
    scenario: str = "none"
    budget_epsilon: Optional[float] = Field(default=None, ge=0, le=100)
    latency_cap: Optional[float] = Field(default=None, ge=0, le=60)
    forbid_iot_fhe: bool = False
    secagg_recovery: bool = False


@router.post("/experiment/start")
def start_experiment(request: RunRequest) -> Dict[str, Any]:
    _check(request.mode, _MODES, "Mode")
    _check(request.objective, _OBJECTIVES, "Objective")
    _check(request.scenario, _SCENARIOS, "Scenario")
    try:
        snapshot = start_live_run(
            request.rounds,
            request.seed,
            request.mode,
            request.objective,
            request.scenario,
            request.budget_epsilon,
            request.latency_cap,
            request.forbid_iot_fhe,
            request.secagg_recovery or request.scenario == "dropout",
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return snapshot


@router.get("/comparison")
def comparison() -> Dict[str, Any]:
    path = Path("experiments/logs/summary.json")
    if not path.exists():
        return {"available": False, "summary": {}}
    return {"available": True, "summary": json.loads(path.read_text(encoding="utf-8"))}


def _check(value: str, allowed: set[str], label: str) -> None:
    if value not in allowed:
        raise HTTPException(
            status_code=400, detail=f"{label} must be one of {sorted(allowed)}."
        )


@router.get("/export/json")
def export_json() -> Response:
    body = json.dumps(state.view(), indent=2)
    return Response(
        content=body,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=ratc-history.json"},
    )


@router.get("/export/csv")
def export_csv() -> Response:
    return Response(
        content=_history_csv(state.view()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ratc-history.csv"},
    )


def _history_csv(snapshot: Dict[str, Any]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "round",
            "mode",
            "seed",
            "accuracy",
            "loss",
            "latency_seconds",
            "payload_bytes",
            "epsilon",
            "client_id",
            "profile",
            "tier",
            "score",
            "fit_seconds",
            "client_bytes",
            "objective",
            "scenario",
            "trust",
            "epsilon_spent",
            "epsilon_remaining",
            "attack",
            "dropout",
            "reason",
        ]
    )
    for metrics in snapshot["history"]:
        clients = metrics.get("clients", {})
        if not clients:
            writer.writerow(
                [
                    metrics.get("round"),
                    metrics.get("mode"),
                    metrics.get("seed"),
                    metrics.get("accuracy"),
                    metrics.get("loss"),
                    metrics.get("latency"),
                    metrics.get("payload_bytes"),
                    metrics.get("privacy_budget"),
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    metrics.get("objective"),
                    metrics.get("scenario"),
                    "",
                    "",
                    "",
                    "",
                    metrics.get("dropout"),
                    "",
                ]
            )
            continue
        for client_id, client in clients.items():
            writer.writerow(
                [
                    metrics.get("round"),
                    metrics.get("mode"),
                    metrics.get("seed"),
                    metrics.get("accuracy"),
                    metrics.get("loss"),
                    metrics.get("latency"),
                    metrics.get("payload_bytes"),
                    metrics.get("privacy_budget"),
                    client_id,
                    client.get("profile"),
                    client.get("tier"),
                    client.get("score"),
                    client.get("fit_seconds"),
                    client.get("payload_bytes"),
                    metrics.get("objective"),
                    metrics.get("scenario"),
                    client.get("trust"),
                    client.get("epsilon"),
                    client.get("epsilon_remaining"),
                    client.get("attack"),
                    metrics.get("dropout"),
                    client.get("reason"),
                ]
            )
    return buffer.getvalue()
