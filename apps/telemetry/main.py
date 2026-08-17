# apps/telemetry/main.py
# Technical Explanation: Telemetry service entrypoint mock.
# Implements standardized /health, /ready, and /live check paths on port 8002.

import http.server
import socketserver
import sys

PORT = 8002


class TelemetryHealthHandler(http.server.BaseHTTPRequestHandler):
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


def main() -> None:
    print(f"Starting Telemetry service on port {PORT}...", flush=True)
    handler = TelemetryHealthHandler
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("Telemetry service is active. Ready for health checks.", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down Telemetry service.", flush=True)
            sys.exit(0)


if __name__ == "__main__":
    main()
