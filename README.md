# Bertie Bots CAPTCHA

A Vercel-ready prototype exploring a more open approach to bot protection.

## Deploy to Vercel

1. Import this repository into Vercel.
2. Keep the project root set to the repository root.
3. Use the default Python runtime detection and deploy.
4. Open the deployed URL. The frontend calls `POST /api/check`.

No database or environment variables are required for this prototype.

## What this prototype does

- Presents a small, accessible drag interaction.
- Sends a limited summary of the interaction to a Python serverless endpoint.
- Returns an advisory result; it does not block users or legitimate crawlers.
- Does not collect biometrics, persist IP addresses, or share threat data.

## Important limitations

This is a demonstration, not production-grade CAPTCHA or DDoS protection. Browser-supplied telemetry can be forged; mouse paths and drag challenges do not reliably distinguish humans from sophisticated automation. WebAuthn is an authentication mechanism and must not be treated as proof that a visitor is human. For production, enforce authorization and rate limits on the server, protect sensitive operations independently, and use a shared persistent store only after designing privacy, retention, access controls, and partner agreements.

Vercel serverless instances are not a shared persistent threat database. Do not use in-memory state here as a global blocklist. The IP-sharing and partner network described in the concept is intentionally not implemented in this starter.
