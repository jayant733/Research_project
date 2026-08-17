# apps/server/main.py
# Technical Explanation: Server application runner.
# Hooks up event handlers, instantiates the generic strategy,
# and starts the server session using the Flower federation platform.

import http.server
import socketserver
import sys
import threading

import numpy as np

from packages.common.events import events
from packages.common.fedavg_aggregator import FedAvgAggregator
from packages.common.generic_strategy import GenericStrategy
from packages.flower.federation import FlowerFederation

HEALTH_PORT = 8000
FLOWER_PORT = 8080


# Event Listeners matching previous log formatting
@events.on_server_start.handle
def on_start(server_address: str) -> None:
    print(
        f"[SERVER_START] Launching Flower Server on {server_address} for 1 round(s)...",
        flush=True,
    )


@events.on_server_stop.handle
def on_stop() -> None:
    print("[SERVER_STOP] Flower Server run completed successfully.", flush=True)


class ServerHealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        """Routes health, readiness, and liveness endpoints."""
        if self.path in ("/health", "/ready", "/live"):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "UP"}')
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')


def run_health_server() -> None:
    """Runs HTTP health check server."""
    handler = ServerHealthHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", HEALTH_PORT), handler) as httpd:
        httpd.serve_forever()


def main() -> None:
    # 1. Start health checks server in background
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # 2. Configure mock baseline global parameters [1.0, 2.0, 3.0]
    initial_weights = [np.array([1.0, 2.0, 3.0], dtype=np.float32)]

    # 3. Instantiate decoupled aggregation strategy
    aggregator = FedAvgAggregator()
    strategy = GenericStrategy(
        initial_parameters=initial_weights, aggregator=aggregator
    )

    # 4. Launch server using the federation platform
    server_address = f"0.0.0.0:{FLOWER_PORT}"
    federation = FlowerFederation()
    try:
        federation.start_server(
            server_address=server_address, num_rounds=1, strategy=strategy
        )
    except Exception as e:
        print(f"[SERVER_ERROR] Server crash: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
