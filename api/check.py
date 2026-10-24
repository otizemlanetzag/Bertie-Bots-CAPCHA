from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > 8192:
                return self._send(413, {"ok": False, "message": "Request too large."})
            body = json.loads(self.rfile.read(length) or b"{}")
            completed = body.get("challenge_completed") is True
            points = body.get("path_points", 0)
            duration = body.get("duration_ms", 0)
            path_length = body.get("path_length", 0)
            if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (points, duration, path_length)):
                return self._send(400, {"ok": False, "message": "Invalid signal format."})
            # Deliberately advisory only: browser-supplied signals are untrusted.
            suspicious = not completed or points > 5000 or duration > 180000
            if suspicious:
                return self._send(200, {
                    "ok": True,
                    "classification": "needs_review",
                    "message": "Extra verification may be appropriate. This demo does not block anyone."
                })
            return self._send(200, {
                "ok": True,
                "classification": "interaction_completed",
                "message": "Interaction completed. No block was applied."
            })
        except (ValueError, TypeError, json.JSONDecodeError):
            return self._send(400, {"ok": False, "message": "Invalid JSON request."})

    def do_GET(self):
        return self._send(200, {
            "service": "Bertie Bots",
            "mode": "prototype",
            "message": "Demo check endpoint is running."
        })

    def _send(self, status, payload):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
