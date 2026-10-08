"""Server policy that assigns tiers and merges their model updates."""

import json
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from packages.common.fedavg_aggregator import FedAvgAggregator
from packages.common.generic_strategy import GenericStrategy
from packages.privacy.fhe_engine import FHESession
from packages.ratc.attacks import scenario_targets
from packages.ratc.bandit import ContextualBandit, context_vector, round_reward
from packages.ratc.budget import BudgetLedger
from packages.ratc.fleet import ClientSpec, fleet_by_id, telemetry_for
from packages.ratc.merge import aggregate_pools
from packages.ratc.predict import predict_telemetry
from packages.ratc.trust import initial_trust, median, next_trust, telemetry_gap
from packages.scheduler.policy import EXCLUDED, decide
from packages.scheduler.scheduler import ResourceAwareScheduler
from packages.scheduler.types import ConstraintVector
from packages.telemetry.vectors import TelemetryVector

EventCallback = Callable[[Dict[str, Any]], None]
SOLVER_OBJECTIVES = {"privacy", "latency", "upload"}


class RATCStrategy(GenericStrategy):
    """Telemetry-driven tier assignment with pool-level aggregation."""

    def __init__(
        self,
        initial_parameters: List[Any],
        clients: Sequence[ClientSpec],
        mode: str,
        seed: int,
        epochs: int = 2,
        learning_rate: float = 0.15,
        fhe_session: Optional[FHESession] = None,
        on_event: Optional[EventCallback] = None,
        objective: str = "topsis",
        scenario: str = "none",
        budget_epsilon: Optional[float] = None,
        latency_cap: Optional[float] = None,
        forbid_iot_fhe: bool = False,
        secagg_recovery: bool = False,
    ) -> None:
        super().__init__(initial_parameters, FedAvgAggregator())
        self.clients = fleet_by_id(list(clients))
        self.mode = mode
        self.seed = seed
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.fhe_session = fhe_session
        self.on_event = on_event
        self.objective = objective
        self.scenario = scenario
        self.latency_cap = latency_cap
        self.forbid_iot_fhe = forbid_iot_fhe
        self.secagg_recovery = secagg_recovery or scenario == "dropout"
        self.scheduler = ResourceAwareScheduler()
        self.ledger = BudgetLedger(self.clients, budget_epsilon)
        self.trust = initial_trust(list(self.clients))
        self.bandits = {client_id: ContextualBandit() for client_id in self.clients}
        self.bandit_context: Dict[str, Any] = {}
        self.telemetry_history: Dict[str, List[TelemetryVector]] = {}
        self.telemetry: Dict[str, TelemetryVector] = {}
        self.fit_seconds: Dict[str, float] = {}
        self.previous_tiers: Dict[str, str] = {}
        self._fit_metrics: List[Dict[str, Any]] = []
        self._config_round = -1
        self._cached_config: Dict[str, Any] = {}
        self._pending: Dict[str, Any] = {}
        self._reported_round = -1
        self._previous_accuracy: Optional[float] = None
        self.explanations: Dict[str, Dict[str, Any]] = {}
        self._tiers_before_round: Dict[str, str] = {}
        self._attack_labels: Dict[str, str] = {}
        self._notes: Dict[str, Any] = {}

    def config_for_round(self, server_round: int) -> Dict[str, str | int | float]:
        """Build the identical Flower fit config shared with every client."""
        if self._config_round != server_round:
            self._cached_config = self._prepare_round(server_round)
            self._config_round = server_round
        return self._cached_config

    def consume_fit_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        self._fit_metrics = [dict(item) for item in metrics]

    def aggregate_fit(self, results: List[Tuple[List[Any], int]]) -> List[Any]:
        paired = _pair(results, self._fit_metrics)
        self._remember_measurements(paired)
        self._update_trust(paired)
        peers = _peers_from_config(self._cached_config)
        engine = None if self.fhe_session is None else self.fhe_session.server_engine
        authority = None if self.fhe_session is None else self.fhe_session.authority
        self._notes = {}
        aggregated, counts = aggregate_pools(
            paired, peers, engine, authority, trust=self.trust, notes=self._notes
        )
        if not aggregated:
            aggregated = list(self.initial_parameters)
        self._pending = self._round_record(paired, counts)
        return aggregated

    def record_evaluation(
        self, server_round: int, loss: float, accuracy: float
    ) -> None:
        """Attach held-out metrics and publish the completed round once."""
        if self._reported_round == server_round or not self._pending:
            return
        self._pending["round"] = int(server_round)
        self._pending["loss"] = float(loss)
        self._pending["accuracy"] = float(accuracy)
        self._update_bandits(float(accuracy))
        self._previous_accuracy = float(accuracy)
        self._reported_round = server_round
        self._emit(
            {
                "type": "ROUND_COMPLETED",
                "metrics": self._pending,
                "clients": self._pending["clients"],
            }
        )

    def _prepare_round(self, server_round: int) -> Dict[str, str | int | float]:
        self._tiers_before_round = dict(self.previous_tiers)
        explanations = self._assign(server_round)
        self._ensure_dropout_pool(explanations)
        self.explanations = explanations
        assignments = {
            client_id: str(details["tier"])
            for client_id, details in explanations.items()
        }
        peers = sorted(
            client_id
            for client_id, tier in assignments.items()
            if tier == "TIER_2_SECAGG"
        )
        attacks = scenario_targets(list(self.clients.values()), self.scenario)
        if self.scenario == "dropout" and peers:
            attacks[peers[-1]] = "dropout"
        noise = {
            client_id: self.ledger.noise_multiplier(
                client_id, self.clients[client_id].sensitivity
            )
            for client_id, tier in assignments.items()
            if tier == "TIER_3_DP_PLAIN"
        }
        self._emit(
            {
                "type": "ROUND_STARTED",
                "round": server_round,
                "assignments": explanations,
            }
        )
        return {
            "server_round": int(server_round),
            "epochs": int(self.epochs),
            "lr": float(self.learning_rate),
            "assignments_json": json.dumps(assignments),
            "secagg_peers": ",".join(peers),
            "mode": self.mode,
            "objective": self.objective,
            "scenario": self.scenario,
            "attack_json": json.dumps(attacks),
            "noise_json": json.dumps(noise),
            "secagg_recovery": 1 if self.secagg_recovery else 0,
        }

    def _assign(self, server_round: int) -> Dict[str, Dict[str, Any]]:
        if self.mode == "plain":
            return {client_id: _decision("PLAIN", 0.0) for client_id in self.clients}
        if self.mode == "random":
            return self._random_assignments(server_round)
        if self.mode == "static" and self.previous_tiers:
            return {
                client_id: _decision(tier, 0.0)
                for client_id, tier in self.previous_tiers.items()
            }
        telemetry = self._telemetry(server_round)
        if self.mode == "bandit" or self._constraints_active():
            explained = self._solve(telemetry)
        else:
            explained = self.scheduler.explain(telemetry, self._constraint_map())
            explained = {
                client_id: _decision(str(details["tier"]), float(details["score"]))
                for client_id, details in explained.items()
            }
        self.telemetry = telemetry
        for client_id, details in explained.items():
            tier = str(details["tier"])
            if tier != EXCLUDED:
                self.previous_tiers[client_id] = tier
        return explained

    def _ensure_dropout_pool(self, explanations: Dict[str, Dict[str, Any]]) -> None:
        """Keep two masked clients available so one benign dropout can be recovered."""
        if self.scenario != "dropout":
            return
        peers = [
            client_id
            for client_id, details in explanations.items()
            if details["tier"] == "TIER_2_SECAGG"
        ]
        spare = sorted(
            (
                client_id
                for client_id, details in explanations.items()
                if details["tier"] not in {"TIER_2_SECAGG", EXCLUDED}
            ),
            key=lambda client_id: float(explanations[client_id].get("score", 0.0)),
        )
        while len(peers) < 2 and spare:
            client_id = spare.pop(0)
            updated = dict(explanations[client_id])
            updated["tier"] = "TIER_2_SECAGG"
            updated["override"] = True
            updated["reason"] = "Placed in SecAgg so one-dropout recovery can run."
            explanations[client_id] = updated
            peers.append(client_id)

    def _telemetry(self, server_round: int) -> Dict[str, TelemetryVector]:
        observed = {
            client_id: telemetry_for(
                spec,
                server_round,
                self.seed,
                self.fit_seconds.get(client_id),
            )
            for client_id, spec in self.clients.items()
        }
        selected: Dict[str, TelemetryVector] = {}
        for client_id, vector in observed.items():
            history = self.telemetry_history.setdefault(client_id, [])
            if self.mode == "predictive" and history:
                selected[client_id] = predict_telemetry([*history, vector])
            else:
                selected[client_id] = vector
            history.append(vector)
        return selected

    def _solve(
        self, telemetry: Dict[str, TelemetryVector]
    ) -> Dict[str, Dict[str, Any]]:
        scores = self.scheduler.topsis_engine.compute_scores(
            {
                client_id: (vector, self.clients[client_id].sensitivity)
                for client_id, vector in telemetry.items()
            }
        )
        objective = self.objective if self.mode != "bandit" else "topsis"
        assigned: Dict[str, Dict[str, Any]] = {}
        self.bandit_context = {}
        for client_id, vector in telemetry.items():
            constraint = self._constraint_for(client_id)
            remaining = self.ledger.remaining(client_id)
            decision = decide(
                objective,
                float(scores.get(client_id, 0.0)),
                constraint,
                trust=self.trust.get(client_id, 1.0),
                remaining_epsilon=remaining,
                fit_seconds=self.fit_seconds.get(client_id),
                tier_one=self.scheduler.t1_threshold,
                tier_two=self.scheduler.t2_threshold,
            )
            legal = _legal_from_decision(decision)
            if self.mode == "bandit" and legal:
                cap = self.ledger.cap or 1.0
                fraction = 1.0 if remaining is None else remaining / max(cap, 1e-6)
                context = context_vector(
                    vector,
                    self.clients[client_id].sensitivity,
                    self.trust.get(client_id, 1.0),
                    fraction,
                )
                chosen = self.bandits[client_id].choose(context, legal)
                decision = dict(decision)
                decision["tier"] = chosen
                decision["reason"] = f"contextual bandit -> {chosen}"
                self.bandit_context[client_id] = context
            assigned[client_id] = decision
        return assigned

    def _constraints_active(self) -> bool:
        return (
            self.objective in SOLVER_OBJECTIVES
            or self.mode in {"reactive", "predictive", "bandit"}
            or self.forbid_iot_fhe
            or self.ledger.cap is not None
            or self.latency_cap is not None
            or any(value < 0.45 for value in self.trust.values())
        )

    def _constraint_map(self) -> Dict[str, ConstraintVector]:
        return {
            client_id: self._constraint_for(client_id) for client_id in self.clients
        }

    def _constraint_for(self, client_id: str) -> ConstraintVector:
        spec = self.clients[client_id]
        return ConstraintVector(
            data_sensitivity_score=spec.sensitivity,
            forbid_fhe=self.forbid_iot_fhe and spec.profile == "iot_device",
            epsilon_cap=self.ledger.cap,
            latency_cap=self.latency_cap,
        )

    def _random_assignments(self, server_round: int) -> Dict[str, Dict[str, Any]]:
        tiers = ["TIER_1_FHE", "TIER_2_SECAGG", "TIER_3_DP_PLAIN"]
        assigned: Dict[str, Dict[str, Any]] = {}
        for index, client_id in enumerate(sorted(self.clients)):
            choice = tiers[(self.seed + server_round + index) % len(tiers)]
            assigned[client_id] = _decision(choice, 0.0, "random tier")
            self.previous_tiers[client_id] = choice
        return assigned

    def _remember_measurements(
        self, paired: Sequence[Tuple[List[Any], int, Dict[str, Any]]]
    ) -> None:
        for _weights, _count, metrics in paired:
            client_id = str(metrics.get("client_id", ""))
            if "fit_seconds" in metrics:
                self.fit_seconds[client_id] = float(metrics["fit_seconds"])
            self.ledger.note_cumulative(client_id, float(metrics.get("epsilon", 0.0)))

    def _update_trust(
        self, paired: Sequence[Tuple[List[Any], int, Dict[str, Any]]]
    ) -> None:
        norms = [float(metrics.get("update_norm", 0.0)) for _w, _c, metrics in paired]
        midpoint = median(norms)
        labels: Dict[str, str] = {}
        for _weights, _count, metrics in paired:
            client_id = str(metrics.get("client_id", ""))
            expected = self.telemetry.get(client_id)
            gap = 0.0 if expected is None else telemetry_gap(expected, metrics)
            updated, label = next_trust(
                self.trust.get(client_id, 1.0),
                float(metrics.get("update_norm", 0.0)),
                midpoint,
                gap,
            )
            self.trust[client_id] = updated
            if label:
                labels[client_id] = label
        self._attack_labels = labels

    def _update_bandits(self, accuracy: float) -> None:
        if self.mode != "bandit":
            return
        reward = round_reward(
            accuracy,
            self._previous_accuracy,
            float(self._pending.get("latency", 0.0)),
            float(self._pending.get("payload_bytes", 0.0)),
            float(self._pending.get("privacy_budget", 0.0)),
        )
        for client_id, context in self.bandit_context.items():
            tier = str(self.explanations.get(client_id, {}).get("tier", ""))
            if tier in {"TIER_1_FHE", "TIER_2_SECAGG", "TIER_3_DP_PLAIN"}:
                self.bandits[client_id].update(tier, context, reward)

    def _round_record(
        self,
        paired: Sequence[Tuple[List[Any], int, Dict[str, Any]]],
        counts: Dict[str, int],
    ) -> Dict[str, Any]:
        clients: Dict[str, Dict[str, Any]] = {}
        payload_bytes = 0
        latency = 0.0
        epsilon = 0.0
        migrations = 0
        for _weights, sample_count, metrics in paired:
            client_id = str(metrics.get("client_id", "unknown"))
            spec = self.clients.get(client_id)
            tier = str(metrics.get("tier", "PLAIN"))
            previous = self._tiers_before_round.get(client_id, "")
            if previous and previous != tier:
                migrations += 1
            payload_bytes += int(float(metrics.get("payload_bytes", 0)))
            latency = max(latency, float(metrics.get("fit_seconds", 0.0)))
            epsilon = max(epsilon, float(metrics.get("epsilon", 0.0)))
            explanation = self.explanations.get(client_id, {})
            remaining = self.ledger.remaining(client_id)
            clients[client_id] = {
                "profile": spec.profile if spec else str(metrics.get("profile", "")),
                "tier": tier,
                "previous_tier": previous,
                "score": float(explanation.get("score", 0.0)),
                "reason": str(explanation.get("reason", "")),
                "rejected": list(explanation.get("rejected", [])),
                "feasible": bool(explanation.get("feasible", True)),
                "sample_count": int(sample_count),
                "telemetry": _telemetry_dict(metrics),
                "fit_seconds": float(metrics.get("fit_seconds", 0.0)),
                "payload_bytes": int(float(metrics.get("payload_bytes", 0))),
                "epsilon": float(metrics.get("epsilon", 0.0)),
                "epsilon_remaining": remaining,
                "privacy_seconds": float(metrics.get("privacy_seconds", 0.0)),
                "trust": float(self.trust.get(client_id, 1.0)),
                "attack": self._attack_labels.get(client_id, ""),
                "update_norm": float(metrics.get("update_norm", 0.0)),
            }
        return {
            "mode": self.mode,
            "objective": self.objective,
            "scenario": self.scenario,
            "seed": self.seed,
            "accuracy": 0.0,
            "loss": 0.0,
            "latency": latency,
            "payload_bytes": payload_bytes,
            "privacy_budget": epsilon,
            "tier_counts": counts,
            "migrations": migrations,
            "dropout": self._notes.get("dropout", "none"),
            "dropped_clients": list(self._notes.get("dropped_clients", [])),
            "clients": clients,
            "source": "live",
        }

    def _emit(self, event: Dict[str, Any]) -> None:
        if self.on_event is not None:
            self.on_event(event)


def _legal_from_decision(decision: Dict[str, Any]) -> List[str]:
    rejected = [str(item) for item in decision.get("rejected", [])]
    return [
        tier
        for tier in ("TIER_1_FHE", "TIER_2_SECAGG", "TIER_3_DP_PLAIN")
        if not any(item.startswith(f"{tier}:") for item in rejected)
    ]


def _decision(tier: str, score: float, reason: str = "TOPSIS score") -> Dict[str, Any]:
    return {
        "tier": tier,
        "score": score,
        "override": False,
        "feasible": tier != EXCLUDED,
        "reason": reason,
        "rejected": [],
    }


def _pair(
    results: Sequence[Tuple[List[Any], int]], metrics: Sequence[Dict[str, Any]]
) -> List[Tuple[List[Any], int, Dict[str, Any]]]:
    if len(results) != len(metrics):
        raise ValueError("Flower results and metrics have different lengths.")
    return [
        (weights, sample_count, meta)
        for (weights, sample_count), meta in zip(results, metrics)
    ]


def _peers_from_config(config: Dict[str, Any]) -> List[str]:
    return [peer for peer in str(config.get("secagg_peers", "")).split(",") if peer]


def _telemetry_dict(metrics: Dict[str, Any]) -> Dict[str, float]:
    keys = [
        "cpu_usage",
        "memory_usage",
        "network_bandwidth",
        "battery_level",
        "disk_io",
    ]
    return {key: float(metrics.get(key, 0.0)) for key in keys}
