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
        
        weights = sched_config.get("topsis", {
            "w_cpu": 0.2, "w_memory": 0.2, "w_bandwidth": 0.2, 
            "w_battery": 0.2, "w_sensitivity": 0.2
        })
        self.topsis_engine = TOPSISEngine(weights)
        
        thresholds = sched_config.get("thresholds", {
            "tier_1_min_score": 0.7,
            "tier_2_min_score": 0.4
        })
        self.t1_threshold = float(thresholds["tier_1_min_score"])
        self.t2_threshold = float(thresholds["tier_2_min_score"])

    def evaluate(
        self,
        telemetry: Dict[str, TelemetryVector],
        constraints: Dict[str, ConstraintVector]
    ) -> Dict[str, PrivacyTier]:
        """
        Evaluates active clients and assigns them to a privacy tier.
        
        Tier 1 (FHE): Needs high compute & memory, handles high sensitivity.
        Tier 2 (SecAgg): Needs moderate compute, handles medium sensitivity.
        Tier 3 (DP): Low compute footprint, handles lower sensitivity or adds high noise.
        """
        assignments = {}
        
        # Prepare data for TOPSIS
        topsis_input = {}
        for cid, t_vec in telemetry.items():
            # If no constraints provided, assume median sensitivity
            c_vec = constraints.get(cid, ConstraintVector(data_sensitivity_score=0.5))
            
            # Hard constraint override
            if c_vec.requires_fhe:
                assignments[cid] = PrivacyTier.TIER_1_FHE
                continue
                
            topsis_input[cid] = (t_vec, c_vec.data_sensitivity_score)
            
        # Get scores
        if topsis_input:
            scores = self.topsis_engine.compute_scores(topsis_input)
            
            # Map scores to tiers based on thresholds
            for cid, score in scores.items():
                if score >= self.t1_threshold:
                    assignments[cid] = PrivacyTier.TIER_1_FHE
                elif score >= self.t2_threshold:
                    assignments[cid] = PrivacyTier.TIER_2_SECAGG
                else:
                    assignments[cid] = PrivacyTier.TIER_3_DP_PLAIN
                    
        return assignments
