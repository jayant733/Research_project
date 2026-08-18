import random
from typing import Dict

from packages.telemetry.interfaces import ITelemetryProvider
from packages.telemetry.vectors import TelemetryVector


class SimulatedTelemetryProvider(ITelemetryProvider):
    """Simulator provider that generates telemetry based on a profile."""

    def __init__(self, profile_name: str, profiles_config: list):
        self.profile = next((p for p in profiles_config if p["profile_name"] == profile_name), None)
        if not self.profile:
            # Fallback default profile if not found
            self.profile = {
                "profile_name": "default",
                "cpu_capacity": 0.5,
                "memory_capacity_mb": 4096,
                "network_speed_kbps": 10240
            }

    def get_battery_status(self) -> float:
        # Simulate battery drain if it's a mobile/IoT device, otherwise plugged in
        if "workstation" in self.profile["profile_name"] or "server" in self.profile["profile_name"]:
            return 1.0
        return random.uniform(0.1, 1.0)

    def harvest_metrics(self) -> TelemetryVector:
        # Generate metrics around a mean defined by the profile
        
        # A weaker CPU will appear to have higher usage for the same task
        cpu_usage_base = max(0.1, 1.0 - self.profile["cpu_capacity"])
        cpu_usage = min(1.0, max(0.0, random.gauss(cpu_usage_base, 0.1)))
        
        # Memory usage normalized
        mem_base = min(0.9, 1024 / float(self.profile["memory_capacity_mb"]))
        mem_usage = min(1.0, max(0.0, random.gauss(mem_base, 0.05)))
        
        # Network bandwidth usage
        net_speed_kbps = self.profile["network_speed_kbps"]
        # Fast networks show low utilization percentage
        net_base = min(1.0, 1000 / float(net_speed_kbps))
        net_usage = min(1.0, max(0.0, random.gauss(net_base, 0.2)))
        
        battery = self.get_battery_status()
        
        return TelemetryVector(
            cpu_usage=cpu_usage,
            memory_usage=mem_usage,
            network_bandwidth=net_usage,
            battery_level=battery,
            disk_io=random.uniform(0.1, 0.5)
        )
