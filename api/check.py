import json
import math
from http.server import BaseHTTPRequestHandler

MAX_BODY = 8192

def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

def score_signals(signals):
    """Return an advisory risk score; client telemetry is untrusted."""
    score = 0.0
    moves = signals.get("pointer_moves", 0)
    scrolls = signals.get("scroll_events", 0)
    touches = signals.get("touch_events", 0)
    samples = signals.get("interval_samples", 0)
    variance = signals.get("interval_variance", 0)
    elapsed = signals.get("elapsed_ms", 0)

    if not all(is_number(v) for v in (moves, scrolls, touches, samples, variance, elapsed)):
        raise ValueError("Signal fields must be finite numbers.")
    if any(v < 0 for v in (moves, scrolls, touches, samples, variance, elapsed)):
        raise ValueError("Signal fields cannot be negative.")
    if moves > 100000 or scrolls > 10000 or touches > 10000 or samples > 10000 or elapsed > 86400000:
        raise ValueError("Signal values exceed allowed bounds.")

    # Only weak indicators. Never classify or block based on one signal.
    if elapsed >= 1500 and moves == 0 and scrolls == 0 and touches == 0:
        score += 0.35
    if samples >= 8 and variance < 1:
        score += 0.35
    if moves > 5000 and elapsed < 5000:
        score += 0.25
    return min(score, 1.0)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._send(200, {
            "service": "Bertie Bots",
            "mode": "prototype",
            "message": "Passive assessment endpoint is running."
        })

    def do_POST(self):
        try:
            if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
                return self._send(415, {"ok": False, "message": "Send application/json."})
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                return self._send(413, {"ok": False, "message": "Request body missing or too large."})
            body = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(body, dict):
                return self._send(400, {"ok": False, "message": "Expected a JSON object."})
            phase = body.get("phase")
            signals = body.get("signals")
            if phase not in ("passive", "challenge") or not isinstance(signals, dict):
                return self._send(400, {"ok": False, "message": "Invalid assessment request."})

            if phase == "passive":
                score = score_signals(signals)
                # Presence check is not authentication. Never claim WebAuthn proves humanity.
                auth_available = False
                return self._send(200, {
                    "ok": True,
                    "risk_score": round(score, 2),
                    "challenge_required": score >= 0.8,
                    "authenticator_available": auth_available,
                    "classification": "needs_review" if score >= 0.65 else "no_challenge",
                    "message": "An extra interaction check is suggested by the demo heuristic." if score >= 0.65 else "No extra challenge suggested by the demo heuristic."
                })

            completed = signals.get("challenge_completed") is True
            points = signals.get("path_points", 0)
            duration = signals.get("challenge_duration_ms", 0)
            path_length = signals.get("path_length", 0)
            if not all(is_number(v) for v in (points, duration, path_length)):
                return self._send(400, {"ok": False, "message": "Invalid challenge signal format."})
            if any(v < 0 or v > 1000000 for v in (points, duration, path_length)):
                return self._send(400, {"ok": False, "message": "Challenge values outside allowed bounds."})
            return self._send(200, {
                "ok": True,
                "classification": "interaction_completed" if completed else "needs_review",
                "challenge_completed": completed,
                "message": "Challenge interaction completed. This does not prove the visitor is human, and no block was applied." if completed else "Challenge not completed. No block was applied."
            })
        except (ValueError, TypeError, json.JSONDecodeError):
            return self._send(400, {"ok": False, "message": "Invalid JSON request."})

    def _send(self, status, payload):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
