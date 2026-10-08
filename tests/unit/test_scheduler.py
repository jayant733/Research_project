"""Scheduler tier tests for the demonstration fleet."""

from packages.ratc.fleet import default_fleet, telemetry_for
from packages.scheduler.scheduler import ResourceAwareScheduler
from packages.scheduler.types import ConstraintVector


def test_default_fleet_uses_all_three_tiers() -> None:
    fleet = default_fleet()
    telemetry = {client.client_id: telemetry_for(client, 1, seed=7) for client in fleet}
    constraints = {
        client.client_id: ConstraintVector(data_sensitivity_score=client.sensitivity)
        for client in fleet
    }
    explained = ResourceAwareScheduler().explain(telemetry, constraints)
    tiers = {details["tier"] for details in explained.values()}
    assert tiers == {"TIER_1_FHE", "TIER_2_SECAGG", "TIER_3_DP_PLAIN"}
    assert explained["ws-1"]["score"] > explained["iot-2"]["score"]
