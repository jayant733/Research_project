"""Flower client that trains locally and applies the assigned privacy tier."""

import json
from typing import Any, Dict, List, Tuple

import psutil

from packages.common.client import GenericClient
from packages.common.context import RoundContext
from packages.common.model_interface import IModel
from packages.privacy.dp_engine import DPEngine
from packages.privacy.fhe_engine import PublicFHEClient
from packages.ratc.attacks import apply_weight_attack
from packages.ratc.fleet import ClientSpec, telemetry_for
from packages.ratc.protect import protect_update


class RATCClient(GenericClient):
    """Participant that reports telemetry and returns a tier-specific update."""

    def __init__(
        self,
        model: IModel,
        spec: ClientSpec,
        train_data: Any,
        test_data: Any,
        seed: int,
        secagg_secret: str,
        public_fhe: bytes | None,
    ) -> None:
        super().__init__(model=model, data=train_data, test_data=test_data)
        self.spec = spec.canonical()
        self.seed = seed
        self.secagg_secret = secagg_secret
        self.fhe_client = (
            PublicFHEClient(public_fhe) if public_fhe is not None else None
        )
        self.dp_engine = DPEngine()
        self.last_fit_seconds: float | None = None

    def fit(
        self, parameters: List[Any], context: RoundContext
    ) -> Tuple[List[Any], int, Dict[str, Any]]:
        started = psutil.Process().cpu_times()
        updated, sample_count, train_metrics = super().fit(parameters, context)
        elapsed = _cpu_seconds(started)
        self.last_fit_seconds = elapsed
        tier, peers = _assignment(context.config, self.spec.client_id)
        attack = _attack(context.config, self.spec.client_id)
        if attack == "dropout":
            tier = "DROPPED"
        elif attack in {"poison", "freerider"}:
            updated = apply_weight_attack(parameters, updated, attack)
        payload, privacy_metrics = protect_update(
            global_weights=parameters,
            local_weights=updated,
            tier=tier,
            client_id=self.spec.client_id,
            round_index=context.current_round,
            sample_count=sample_count,
            secagg_peers=peers,
            secagg_secret=self.secagg_secret,
            fhe_client=self.fhe_client,
            dp_engine=self.dp_engine,
            noise_multiplier=_noise(context.config, self.spec.client_id),
            recovery=_recovery_enabled(context.config, tier),
        )
        reported = self.spec
        if attack == "telemetry":
            reported = ClientSpec(
                self.spec.client_id, "workstation", self.spec.sensitivity
            )
        telemetry = telemetry_for(
            reported, context.current_round, self.seed, measured_fit_seconds=elapsed
        )
        metrics = {
            **train_metrics,
            **privacy_metrics,
            **_telemetry_metrics(telemetry),
            "fit_seconds": float(elapsed),
            "profile": self.spec.profile,
            "sensitivity": float(self.spec.sensitivity),
        }
        return payload, sample_count, metrics

    def evaluate(
        self, parameters: List[Any], context: RoundContext
    ) -> Tuple[float, int, Dict[str, Any]]:
        loss, sample_count, metrics = super().evaluate(parameters, context)
        metrics["client_id"] = self.spec.client_id
        metrics["accuracy"] = float(metrics.get("accuracy", 0.0))
        return float(loss), sample_count, metrics


def _recovery_enabled(config: Dict[str, Any], tier: str) -> bool:
    enabled = int(float(config.get("secagg_recovery", 0))) == 1
    return enabled and tier == "TIER_2_SECAGG"


def _attack(config: Dict[str, Any], client_id: str) -> str:
    raw = config.get("attack_json", "{}")
    attacks = json.loads(str(raw))
    return str(attacks.get(client_id, ""))


def _noise(config: Dict[str, Any], client_id: str) -> float | None:
    raw = config.get("noise_json", "{}")
    values = json.loads(str(raw))
    if client_id not in values:
        return None
    return float(values[client_id])


def _assignment(config: Dict[str, Any], client_id: str) -> Tuple[str, List[str]]:
    raw = config.get("assignments_json", "{}")
    assignments = json.loads(str(raw))
    tier = str(assignments.get(client_id, "PLAIN"))
    peers = [peer for peer in str(config.get("secagg_peers", "")).split(",") if peer]
    return tier, peers


def _telemetry_metrics(telemetry: Any) -> Dict[str, float]:
    payload = telemetry.to_dict()
    return {key: float(value) for key, value in payload.items()}


def _cpu_seconds(started: Any) -> float:
    ended = psutil.Process().cpu_times()
    return float((ended.user + ended.system) - (started.user + started.system))
