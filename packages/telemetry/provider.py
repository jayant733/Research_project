import psutil

from packages.telemetry.interfaces import ITelemetryProvider
from packages.telemetry.vectors import TelemetryVector


class SystemTelemetryProvider(ITelemetryProvider):
    """Concrete provider using psutil to harvest cross-platform hardware metrics."""

    def __init__(self, network_interface_speed_mbps: float = 1000.0):
        self.network_interface_speed_mbps = network_interface_speed_mbps
        
        # Initialize CPU timing
        psutil.cpu_percent(interval=None)
        
        # Initialize Network IO
        self.last_net_io = psutil.net_io_counters()
        import time
        self.last_net_time = time.time()

    def get_battery_status(self) -> float:
        if not hasattr(psutil, "sensors_battery"):
            return 1.0 # Assume plugged in if no sensor
            
        battery = psutil.sensors_battery()
        if battery is None:
            return 1.0 # Assume plugged in desktop/server
            
        return battery.percent / 100.0

    def harvest_metrics(self) -> TelemetryVector:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_usage = cpu_percent / 100.0
        
        # Memory
        mem = psutil.virtual_memory()
        memory_usage = mem.percent / 100.0
        
        # Network (bytes per second)
        current_net_io = psutil.net_io_counters()
        import time
        current_time = time.time()
        
        time_delta = current_time - self.last_net_time
        if time_delta > 0:
            bytes_sent = current_net_io.bytes_sent - self.last_net_io.bytes_sent
            bytes_recv = current_net_io.bytes_recv - self.last_net_io.bytes_recv
            
            # bits per second
            bps = (bytes_sent + bytes_recv) * 8 / time_delta
            # convert to mbps
            mbps = bps / (1024 * 1024)
            
            # Normalize against theoretical max
            network_bandwidth = min(1.0, mbps / self.network_interface_speed_mbps)
        else:
            network_bandwidth = 0.0
            
        self.last_net_io = current_net_io
        self.last_net_time = current_time
        
        # Battery
        battery_level = self.get_battery_status()
        
        # Disk IO (simplified, assuming mostly SSD/fast I/O for ML, mock at 0.1 for baseline)
        disk_io = 0.1
        
        return TelemetryVector(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            network_bandwidth=network_bandwidth,
            battery_level=battery_level,
            disk_io=disk_io
        )

TelemetryProvider = SystemTelemetryProvider
