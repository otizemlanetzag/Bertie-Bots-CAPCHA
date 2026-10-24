# Bertie Bots CAPTCHA

Vercel-ready prototype of a more open approach to bot protection.

## Deploy
Import this repository into Vercel, keep the root directory at the repository root, and deploy. No database or environment variables are required.

## Included
- Passive browser-side event counters for pointer movement, scrolling and touch activity.
- Only aggregate counts/timing statistics are sent to `POST /api/check`; raw pointer coordinates are used locally for the drag challenge and are not sent as telemetry.
- An advisory serverless risk score can suggest a challenge; the drag interaction is shown only when the demo score reaches its threshold.
- Server-side input validation, bounded request size, JSON responses and no-store headers.
- The API never blocks a visitor or marks an IP as malicious.

## Limits / production work still required
This is a prototype, not production CAPTCHA or DDoS protection. Browser signals are client-controlled and can be forged; the risk score is a demonstrative heuristic, not a trained classifier. A completed drag does not prove humanity. WebAuthn/passkeys authenticate a relying-party credential and are not proof that a visitor is human; this demo does not perform WebAuthn authentication. A real deployment needs relying-party registration/authentication flows, server-side authorization around protected actions, carefully designed rate limiting, and privacy/retention review.

The design intentionally does not implement partner sharing or a persistent threat database yet. Vercel serverless memory is not suitable as a shared global blocklist. The CAPTCHA should be integrated into a site that uses the API's decision server-side; a standalone page cannot protect unrelated routes or applications.
