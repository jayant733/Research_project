from typing import Dict

from pydantic import BaseModel


class ClientRegistration(BaseModel):
    client_id: str
    profile: str


class TelemetryPush(BaseModel):
    client_id: str
    cpu_usage: float
    memory_usage: float
    network_bandwidth: float
    battery_level: float
    disk_io: float


class SystemStatus(BaseModel):
    current_round: int
    total_rounds: int
    active_clients: int
    clients_per_tier: Dict[str, int]
    running: bool = False
    mode: str = "ratc"
    seed: int = 7
    source: str = "live"
    message: str = ""
