from dataclasses import dataclass


@dataclass
class TelemetryVector:
    """Normalized hardware metrics representation for the scheduler.
    All values are normalized to a [0.0, 1.0] scale.
    """
    cpu_usage: float
    memory_usage: float
    network_bandwidth: float
    battery_level: float
    disk_io: float

    def to_dict(self) -> dict:
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "network_bandwidth": self.network_bandwidth,
            "battery_level": self.battery_level,
            "disk_io": self.disk_io
        }
