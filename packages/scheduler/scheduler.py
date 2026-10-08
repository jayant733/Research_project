from typing import Dict

from packages.common.config_loader import config_loader
from packages.scheduler.interfaces import IScheduler
from packages.scheduler.topsis import TOPSISEngine
from packages.scheduler.types import ConstraintVector, PrivacyTier
from packages.telemetry.vectors import TelemetryVector


class ResourceAwareScheduler(IScheduler):
    """Assigns clients to privacy tiers based on telemetry and TOPSIS scores."""

    def __init__(self):
        # Load configuration
        config = config_loader.load_all_configs()
        sched_config = config.get("scheduler", {})

        self.policy_type = sched_config.get("policy_type", "topsis")

        weights = sched_config.get(
            "topsis",
            {
                "w_cpu": 0.2,
                "w_memory": 0.2,
                "w_bandwidth": 0.2,
                "w_battery": 0.2,
                "w_sensitivity": 0.2,
            },
        )
        self.topsis_engine = TOPSISEngine(weights)

        thresholds = sched_config.get(
            "thresholds", {"tier_1_min_score": 0.7, "tier_2_min_score": 0.4}
        )
        self.t1_threshold = float(thresholds["tier_1_min_score"])
        self.t2_threshold = float(thresholds["tier_2_min_score"])

    def evaluate(
        self,
        telemetry: Dict[str, TelemetryVector],
        constraints: Dict[str, ConstraintVector],
    ) -> Dict[str, PrivacyTier]:
        """
        Evaluates active clients and assigns them to a privacy tier.

        Tier 1 (FHE): Needs high compute & memory, handles high sensitivity.
        Tier 2 (SecAgg): Needs moderate compute, handles medium sensitivity.
        Tier 3 (DP): Low compute footprint for lower sensitivity.
        """
        return {
            client_id: PrivacyTier(details["tier"])
            for client_id, details in self.explain(telemetry, constraints).items()
        }

    def explain(
        self,
        telemetry: Dict[str, TelemetryVector],
        constraints: Dict[str, ConstraintVector],
    ) -> Dict[str, Dict[str, float | str | bool]]:
        """Return the tier, TOPSIS score, and whether a hard override applied."""
        assignments: Dict[str, Dict[str, float | str | bool]] = {}
        topsis_input = {}
        for client_id, telemetry_vector in telemetry.items():
            constraint = constraints.get(
                client_id, ConstraintVector(data_sensitivity_score=0.5)
            )
            if constraint.requires_fhe:
                assignments[client_id] = {
                    "tier": PrivacyTier.TIER_1_FHE.value,
                    "score": 1.0,
                    "override": True,
                }
                continue
            topsis_input[client_id] = (
                telemetry_vector,
                constraint.data_sensitivity_score,
            )

        if not topsis_input:
            return assignments

        scores = self.topsis_engine.compute_scores(topsis_input)
        for client_id, score in scores.items():
            assignments[client_id] = {
                "tier": self._tier_for_score(score).value,
                "score": float(score),
                "override": False,
            }
        return assignments

    def _tier_for_score(self, score: float) -> PrivacyTier:
        if score >= self.t1_threshold:
            return PrivacyTier.TIER_1_FHE
        if score >= self.t2_threshold:
            return PrivacyTier.TIER_2_SECAGG
        return PrivacyTier.TIER_3_DP_PLAIN
