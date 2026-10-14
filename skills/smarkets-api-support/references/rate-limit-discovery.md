# Smarkets API Rate Limit Discovery — Findings

## Architecture

- **Global cap:** 1200 RPM per account (documented, confirmed by testing)
- **Per-endpoint caps:** 6 endpoints have their own documented limits
- **Per-endpoint caps are MAXIMUMS, not additive allocations** — the global cap takes precedence
- **Sum of documented per-endpoint limits = 1282 RPM** — exceeds the 1200 global pool, confirming they are concurrent caps
- **15 endpoints have NO per-endpoint limit** and share the 1200 RPM global pool
- **Rate limits are strictly account/session-bound** — unauthenticated traffic bypasses the 1200 RPM ceiling entirely (tested: 18,141 requests in 90 seconds = 12,086 RPM with zero 429s and no X-RateLimit headers)

## Documented Per-Endpoint Limits

| Endpoint | Limit | RPM Equivalent |
|----------|-------|----------------|
| `POST /v3/sessions/` | 5 per 300s | 1 |
| `DELETE /v3/sessions/` | 30 per 60s | 30 |
| `GET /v3/markets/{ids}/quotes/` | 50 per 60s | 50 |
| `POST /v3/orders/` | 10 per 1s | 600 |
| `DELETE /v3/orders/` | 1 per 60s | 1 |
| `DELETE /v3/orders/{id}/` | 10 per 1s | 600 |
| **Total documented** | | **1282** |

## API Quirks (Critical for Testing)

### Auth
- Login endpoint: `POST /v3/sessions/`
- JSON body: `{"username": "<email>", "password": "***"}`
- **The field is `username`, NOT `email`** — even though the value is an email address
- Session token returned in `Set-Cookie` header

### Rate Limit Headers (on 200 responses)
- `X-RateLimit-Limit` — max requests in current window
- `X-RateLimit-Remaining` — remaining requests in current window
- `X-RateLimit-Reset` — seconds until window resets

### 429 Response Format
```json
{
  "error_type": "RATE_LIMIT_EXCEEDED",
  "data": {
    "count": N,
    "limit": N,
    "expiry": "Thu, 16 Jul 2026 11:21:18 GMT"
  }
}
```

**CRITICAL:** The `expiry` field is in **RFC 2822 format** (`Thu, 16 Jul 2026 11:21:18 GMT`), NOT ISO 8601. Use `email.utils.parsedate_to_datetime()` to parse it, not `datetime.fromisoformat()`.

### OpenAPI Spec
- Live spec: `https://api.smarkets.com/v3/control/openapi/?tags=trading_api`
- 21 endpoints total across the trading API

## Discovery Methodology

1. **Phase 1 — Smoke Test:** One request per endpoint, capture status + rate limit headers
2. **Phase 2 — Per-Endpoint Probe:** Hammer each safe endpoint until 429, discover actual per-endpoint limit
3. **Phase 3 — Shared Pool Test:** Fire all endpoints concurrently to test if 1200 RPM is truly shared
4. **Phase 4 — Aggregate Analysis:** Compare documented vs discovered limits, show how 1200 RPM breaks down

## Safety Constraints for Testing

- Do NOT place orders (`POST /v3/orders/`) — read-only probing only
- Do NOT cancel real orders — use fake UUID for `DELETE /v3/orders/{id}/`
- Do NOT logout until the very end (session token needed for all phases)
- Wait for rate limit window reset between endpoint probes
- Public endpoints (events, currencies, contracts) work without credentials

## Discrepancy Note

`api-scope-confirmation.txt` says `POST /v3/orders/` has no limit — the live OpenAPI spec says 10/sec. The live spec is authoritative.

## Repository

- GitHub: `smiley1910/smarkets-rate-limit-discovery`
- Script: `rate_limit_discovery.py` (1168 lines, 15 issues audited and fixed across 6 passes)
- Includes: `AGENTS.md` (persistent OpenCode rules), `PROMPTING_GUIDE.md` (prompt engineering guide)
