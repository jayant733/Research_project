"""One real Flower round across CKKS, secure aggregation, and local DP."""

from packages.ratc.fleet import ClientSpec
from packages.ratc.orchestrator import RunConfig, run_session


def test_mixed_tier_flower_round() -> None:
    fleet = [
        ClientSpec("ws-1", "workstation", 0.86),
        ClientSpec("mob-1", "mobile", 0.55),
        ClientSpec("iot-1", "iot_device", 0.2),
    ]
    events = run_session(
        RunConfig(mode="ratc", seed=7, num_rounds=1, epochs=1, clients=fleet)
    )
    completed = [event for event in events if event["type"] == "ROUND_COMPLETED"]
    assert len(completed) == 1
    metrics = completed[0]["metrics"]
    assert metrics["tier_counts"]["TIER_1_FHE"] == 1
    assert metrics["tier_counts"]["TIER_2_SECAGG"] == 1
    assert metrics["tier_counts"]["TIER_3_DP_PLAIN"] == 1
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert (
        metrics["clients"]["ws-1"]["payload_bytes"]
        > metrics["clients"]["iot-1"]["payload_bytes"]
    )
    assert metrics["privacy_budget"] > 0
