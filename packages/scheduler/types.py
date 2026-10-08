from dataclasses import dataclass
from enum import Enum
from typing import Optional, Set


class PrivacyTier(Enum):
    """Enumeration of available privacy execution tiers."""
    TIER_1_FHE = "TIER_1_FHE"
    TIER_2_SECAGG = "TIER_2_SECAGG"
    TIER_3_DP_PLAIN = "TIER_3_DP_PLAIN"


@dataclass
class ConstraintVector:
    """Client-specific privacy requirements and data sensitivity levels."""
    data_sensitivity_score: float  # [0.0, 1.0] where 1.0 is highly sensitive
    requires_fhe: bool = False
    min_dp_epsilon: float = 1.0
    allowed_tiers: Optional[Set[str]] = None
    epsilon_cap: Optional[float] = None
    latency_cap: Optional[float] = None
    forbid_fhe: bool = False
