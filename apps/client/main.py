# apps/client/main.py
# Technical Explanation: Client application runner.
# Hooks up event handlers, instantiates the generic client model,
# and starts the client session using the Flower federation platform.

import http.server
import os
import socketserver
import sys
import threading
import time
from typing import Any, List

from packages.common.client import GenericClient
from packages.common.events import events
from packages.common.mock_model import MockModel
from packages.flower.federation import FlowerFederation

HEALTH_PORT = 8001


# Event Listeners matching previous log formatting
@events.on_client_init.handle
def on_init(model: Any) -> None:
    print(
        "[CLIENT_INIT] Created Flower client with local parameters: [1.0, 2.0, 3.0]",
        flush=True,
    )


@events.on_fit_start.handle
def on_fit(parameters: List[Any], context: Any) -> None:
    print(
        f"[CLIENT_COM] fit requested. Received parameters from Server: {parameters}",
        flush=True,
    )


@events.on_fit_end.handle
def on_fit_complete(updated_weights: List[Any], context: Any) -> None:
    print(
        f"[CLIENT_LOCAL] Local update completed. Updated parameters: {updated_weights}",
        flush=True,
    )


@events.on_evaluate_start.handle
def on_eval(parameters: List[Any], context: Any) -> None:
    print(
        f"[CLIENT_COM] evaluate requested. Checking parameters: {parameters}",
        flush=True,
    )


class ClientHealthHandler(http.server.BaseHTTPRequestHandler):
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
    handler = ClientHealthHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", HEALTH_PORT), handler) as httpd:
        httpd.serve_forever()


def main() -> None:
    # 1. Start health checks server in background
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # 2. Configure target address
    server_host = os.environ.get("SERVER_HOST", "localhost")
    server_address = f"{server_host}:8080"

    print(
        f"[CLIENT_START] Connecting to Flower Server at {server_address}...", flush=True
    )
    time.sleep(3.0)

    # 3. Instantiate decoupled client and run federation loop
    model = MockModel()
    client = GenericClient(model=model)

    federation = FlowerFederation()
    try:
        federation.start_client(server_address=server_address, client=client)
    except Exception as e:
        print(f"[CLIENT_ERROR] Failed to run client: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":

    main()
