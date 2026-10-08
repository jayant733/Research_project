"""Policy, budget, trust, prediction, bandit, and dropout-recovery tests."""

import numpy as np
import pytest

from packages.privacy.secagg_engine import SecAggEngine, build_recovery_shares
from packages.privacy.shamir import reconstruct_secret, share_secret
from packages.ratc.bandit import ContextualBandit, round_reward
from packages.ratc.budget import BudgetLedger
from packages.ratc.merge import aggregate_pools
from packages.ratc.predict import predict_telemetry
from packages.ratc.trust import next_trust, trust_weight
from packages.scheduler.policy import decide
from packages.scheduler.types import ConstraintVector
from packages.telemetry.vectors import TelemetryVector


def test_privacy_objective_obeys_an_iot_ckks_ban() -> None:
    decision = decide(
        "privacy",
        score=0.95,
        constraint=ConstraintVector(data_sensitivity_score=0.2, forbid_fhe=True),
    )
    assert decision["tier"] == "TIER_2_SECAGG"
    assert decision["feasible"] is True
    assert any("forbidden" in item for item in decision["rejected"])


def test_impossible_latency_cap_excludes_the_client() -> None:
    decision = decide(
        "latency",
        score=0.2,
        constraint=ConstraintVector(data_sensitivity_score=0.2, latency_cap=0.01),
        fit_seconds=0.2,
    )
    assert decision["tier"] == "EXCLUDED"
    assert decision["feasible"] is False
    assert "No tier satisfies" in str(decision["reason"])


def test_exhausted_budget_blocks_local_dp_and_scales_noise() -> None:
    ledger = BudgetLedger(["iot-1"], cap=1.0)
    assert ledger.noise_multiplier("iot-1", 0.2) > 0.5
    ledger.note_cumulative("iot-1", 0.9)
    assert ledger.blocks_dp("iot-1")
    decision = decide(
        "upload",
        score=0.1,
        constraint=ConstraintVector(data_sensitivity_score=0.2),
        remaining_epsilon=ledger.remaining("iot-1"),
    )
    assert decision["tier"] != "TIER_3_DP_PLAIN"


def test_poison_norm_lowers_trust_and_aggregation_weight() -> None:
    updated, label = next_trust(1.0, update_norm=20.0, median_norm=1.0)
    assert label == "poison"
    assert updated < 0.45
    assert trust_weight(updated) == 0.15


def test_prediction_extends_the_last_step() -> None:
    history = [
        TelemetryVector(0.2, 0.2, 0.4, 0.8, 0.1),
        TelemetryVector(0.3, 0.2, 0.5, 0.7, 0.1),
    ]
    predicted = predict_telemetry(history)
    assert predicted.cpu_usage == pytest.approx(0.4)
    assert predicted.battery_level == pytest.approx(0.6)


def test_bandit_update_changes_the_linear_score() -> None:
    bandit = ContextualBandit(alpha=0.0)
    context = np.ones(7)
    before = bandit.choose(context, ["TIER_3_DP_PLAIN", "TIER_2_SECAGG"])
    bandit.update("TIER_2_SECAGG", context, reward=2.0)
    after = bandit.choose(context, ["TIER_3_DP_PLAIN", "TIER_2_SECAGG"])
    assert before == "TIER_3_DP_PLAIN"
    assert after == "TIER_2_SECAGG"
    assert round_reward(0.9, 0.8, 1.0, 1000, 1.0) < 0.1


def test_shamir_round_trip() -> None:
    shares = share_secret(123456, 2, [1, 2, 3], [99])
    assert reconstruct_secret(shares[:2]) == 123456


def test_one_secagg_dropout_reconstructs_the_survivor_average() -> None:
    engine = SecAggEngine("test-secret")
    peers = ["a", "b", "c"]
    weights = {
        "a": [np.array([1.0, 1.0], dtype=np.float32)],
        "b": [np.array([3.0, 3.0], dtype=np.float32)],
        "c": [np.array([7.0, 7.0], dtype=np.float32)],
    }
    updates = []
    for client_id in ("a", "b"):
        masked = engine.mask_weights(weights[client_id], client_id, peers, 3, 2)
        shares = build_recovery_shares(engine, client_id, peers, 3)
        updates.append(
            (
                [*masked, shares],
                2,
                {
                    "client_id": client_id,
                    "tier": "TIER_2_SECAGG",
                    "has_recovery": 1,
                },
            )
        )
    notes: dict = {}
    averaged, counts = aggregate_pools(updates, peers, None, None, notes=notes)
    np.testing.assert_allclose(averaged[0], [2.0, 2.0], atol=1e-4)
    assert counts["TIER_2_SECAGG"] == 2
    assert notes["dropout"] == "recovered"
    assert notes["dropped_clients"] == ["c"]
