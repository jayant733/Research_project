# apps/scheduler/main.py
# Technical Explanation: Scheduler microservice.
# Accepts POST requests with telemetry/constraints and returns tier assignments.

import http.server
import json
import os
import socketserver
import sys

from packages.scheduler.scheduler import ResourceAwareScheduler
from packages.scheduler.types import ConstraintVector
from packages.telemetry.vectors import TelemetryVector

PORT = int(os.environ.get("SCHEDULER_PORT", "8003"))
scheduler = ResourceAwareScheduler()


class SchedulerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in ("/health", "/ready", "/live"):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "UP"}')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        if self.path == "/evaluate":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data)
                # Expected body: telemetry and constraints keyed by client id.
                telemetry = {
                    cid: TelemetryVector(**v)
                    for cid, v in data.get("telemetry", {}).items()
                }
                constraints = {
                    cid: ConstraintVector(**v)
                    for cid, v in data.get("constraints", {}).items()
                }

                # Evaluate
                assignments = scheduler.evaluate(telemetry, constraints)

                # Format output
                out = {cid: tier.value for cid, tier in assignments.items()}

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(out).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def main() -> None:
    print(f"Starting Scheduler service on port {PORT}...", flush=True)
    handler = SchedulerHandler
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("Scheduler active.", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down...", flush=True)
            sys.exit(0)


if __name__ == "__main__":
    main()
