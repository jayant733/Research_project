"""Small linear contextual bandit over the three privacy tiers."""

from typing import Dict, Sequence

import numpy as np

from packages.telemetry.vectors import TelemetryVector

ARMS = ("TIER_1_FHE", "TIER_2_SECAGG", "TIER_3_DP_PLAIN")


class ContextualBandit:
    """LinUCB with one linear model per tier."""

    def __init__(self, alpha: float = 0.35, dimensions: int = 7) -> None:
        self.alpha = float(alpha)
        self.dimensions = dimensions
        self.gram: Dict[str, np.ndarray] = {
            arm: np.eye(dimensions) for arm in ARMS
        }
        self.response: Dict[str, np.ndarray] = {
            arm: np.zeros(dimensions) for arm in ARMS
        }

    def choose(self, context: np.ndarray, legal: Sequence[str]) -> str:
        vector = np.asarray(context, dtype=np.float64)
        best_arm = legal[0]
        best_score = -1e18
        for arm in legal:
            if arm not in self.gram:
                continue
            inverse = np.linalg.inv(self.gram[arm])
            estimate = float(vector @ inverse @ self.response[arm])
            bonus = self.alpha * float(np.sqrt(max(0.0, vector @ inverse @ vector)))
            score = estimate + bonus
            if score > best_score:
                best_score = score
                best_arm = arm
        return best_arm

    def update(self, arm: str, context: np.ndarray, reward: float) -> None:
        vector = np.asarray(context, dtype=np.float64)
        self.gram[arm] = self.gram[arm] + np.outer(vector, vector)
        self.response[arm] = self.response[arm] + (float(reward) * vector)


def context_vector(
    telemetry: TelemetryVector,
    sensitivity: float,
    trust: float,
    budget_fraction: float,
) -> np.ndarray:
    return np.array(
        [
            1.0 - telemetry.cpu_usage,
            1.0 - telemetry.memory_usage,
            telemetry.network_bandwidth,
            telemetry.battery_level,
            float(sensitivity),
            float(trust),
            float(budget_fraction),
        ],
        dtype=np.float64,
    )


def round_reward(
    accuracy: float,
    previous_accuracy: float | None,
    latency: float,
    payload_bytes: float,
    epsilon: float,
) -> float:
    """Reward accuracy change and charge measured latency, upload, and privacy spend."""
    gain = accuracy if previous_accuracy is None else accuracy - previous_accuracy
    upload_cost = payload_bytes / 1_000_000
    return float(gain - (0.02 * latency) - upload_cost - (0.01 * epsilon))
