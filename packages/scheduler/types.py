from dataclasses import dataclass
from enum import Enum


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
