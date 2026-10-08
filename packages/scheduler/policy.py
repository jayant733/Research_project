"""Choose a legal privacy tier from an objective and hard constraints."""

from typing import Dict, List, Sequence, Tuple

from packages.scheduler.types import ConstraintVector

TIERS: Tuple[str, ...] = ("TIER_1_FHE", "TIER_2_SECAGG", "TIER_3_DP_PLAIN")
PRIVACY_RANK = {"TIER_1_FHE": 3, "TIER_2_SECAGG": 2, "TIER_3_DP_PLAIN": 1}
LATENCY_PENALTY = {"TIER_1_FHE": 0.45, "TIER_2_SECAGG": 0.12, "TIER_3_DP_PLAIN": 0.04}
UPLOAD_BYTES = {"TIER_1_FHE": 230_000, "TIER_2_SECAGG": 712, "TIER_3_DP_PLAIN": 712}
EXCLUDED = "EXCLUDED"
DP_BUDGET_FLOOR = 0.75
LOW_TRUST = 0.45


def estimate_latency(tier: str, fit_seconds: float | None) -> float:
    """Estimate tier latency from the last measured fit, plus a fixed privacy cost."""
    base = 0.3 if fit_seconds is None else max(0.0, float(fit_seconds))
    return base + LATENCY_PENALTY[tier]


def legal_tiers(
    constraint: ConstraintVector,
    trust: float,
    remaining_epsilon: float | None,
    fit_seconds: float | None,
) -> Tuple[List[str], List[str]]:
    """Return legal tiers and the reasons the others were rejected."""
    if constraint.allowed_tiers is None:
        allowed = set(TIERS)
    else:
        allowed = set(constraint.allowed_tiers)
    legal: List[str] = []
    rejected: List[str] = []
    for tier in TIERS:
        reason = _rejection(
            tier, allowed, constraint, trust, remaining_epsilon, fit_seconds
        )
        if reason is None:
            legal.append(tier)
        else:
            rejected.append(f"{tier}: {reason}")
    if constraint.requires_fhe:
        if "TIER_1_FHE" in legal:
            bumped = [tier for tier in legal if tier != "TIER_1_FHE"]
            legal = ["TIER_1_FHE"]
            rejected.extend(f"{tier}: CKKS is required" for tier in bumped)
        else:
            legal = []
            rejected.append("TIER_1_FHE: CKKS is required but not legal")
    return legal, rejected


def choose_tier(
    objective: str,
    score: float,
    legal: Sequence[str],
    fit_seconds: float | None,
    tier_one: float = 0.7,
    tier_two: float = 0.4,
) -> str:
    """Pick one legal tier for the selected objective."""
    if not legal:
        return EXCLUDED
    if objective == "privacy":
        return max(legal, key=lambda tier: PRIVACY_RANK[tier])
    if objective == "latency":
        return min(legal, key=lambda tier: estimate_latency(tier, fit_seconds))
    if objective == "upload":
        return min(legal, key=lambda tier: UPLOAD_BYTES[tier])
    preferred = _tier_for_score(score, tier_one, tier_two)
    if preferred in legal:
        return preferred
    return _nearest(preferred, legal)


def decide(
    objective: str,
    score: float,
    constraint: ConstraintVector,
    trust: float = 1.0,
    remaining_epsilon: float | None = None,
    fit_seconds: float | None = None,
    tier_one: float = 0.7,
    tier_two: float = 0.4,
) -> Dict[str, object]:
    """Return the chosen tier, rejected alternatives, and a short reason."""
    legal, rejected = legal_tiers(constraint, trust, remaining_epsilon, fit_seconds)
    tier = choose_tier(objective, score, legal, fit_seconds, tier_one, tier_two)
    feasible = tier != EXCLUDED
    if feasible:
        reason = _choice_reason(objective, tier)
    else:
        reason = "No tier satisfies the constraints."
    return {
        "tier": tier,
        "score": float(score),
        "override": bool(rejected),
        "feasible": feasible,
        "reason": reason,
        "rejected": rejected,
    }


def _rejection(
    tier: str,
    allowed: set,
    constraint: ConstraintVector,
    trust: float,
    remaining_epsilon: float | None,
    fit_seconds: float | None,
) -> str | None:
    if tier not in allowed:
        return "tier is not allowed"
    if tier == "TIER_1_FHE" and constraint.forbid_fhe:
        return "CKKS is forbidden for this profile"
    if tier == "TIER_3_DP_PLAIN" and trust < LOW_TRUST:
        return "low trust blocks a weaker privacy tier"
    if tier == "TIER_3_DP_PLAIN" and remaining_epsilon is not None:
        if remaining_epsilon < DP_BUDGET_FLOOR:
            return "local DP budget is exhausted"
    if constraint.latency_cap is not None:
        if estimate_latency(tier, fit_seconds) > float(constraint.latency_cap):
            return "latency estimate exceeds the cap"
    return None


def _tier_for_score(score: float, tier_one: float, tier_two: float) -> str:
    if score >= tier_one:
        return "TIER_1_FHE"
    if score >= tier_two:
        return "TIER_2_SECAGG"
    return "TIER_3_DP_PLAIN"


def _nearest(preferred: str, legal: Sequence[str]) -> str:
    order = list(TIERS)
    start = order.index(preferred)
    for distance in range(1, len(order)):
        for index in (start - distance, start + distance):
            if 0 <= index < len(order) and order[index] in legal:
                return order[index]
    return legal[0]


def _choice_reason(objective: str, tier: str) -> str:
    labels = {
        "privacy": "strongest legal privacy tier",
        "latency": "lowest estimated latency",
        "upload": "smallest estimated upload",
        "topsis": "TOPSIS score inside the legal set",
    }
    return f"{labels.get(objective, objective)} -> {tier}"
