# Smarkets API Rate Limits — Authoritative Documentation

## Source

All rate limit documentation below is from the **live OpenAPI spec** at:
`https://api.smarkets.com/v0/control/openapi/?tags=trading_api`

This URL was discovered by reading the Swagger UI HTML source at `docs.smarkets.com`, which loads the spec from that endpoint.

**Update (2026-09-23):** the local snapshot `~/smarkets-api-support/openapi/smarkets_openapi.json` (md5 `afec019e8b174fe3e8cb3c9e7bb3d99b`, mtime 2026-08-18) DOES now contain the rate-limit descriptions — the old "local copy is stripped" note no longer applies. It is still **stale in one place**: it lacks the live `GET /v3/events/` block `Maximum 600 requests per 60 seconds`. Live spec fetched 2026-09-23 has **7** endpoints with per-endpoint caps (was 6). Always diff live vs local descriptions before quoting counts.

## Global Rate Limit

**1200 requests per 60 seconds** across ALL endpoints, applied per account.

> "All API users are subject to a default rate limit of 1200 requests per 60 seconds across all endpoints, applied per account. Individual endpoints may have additional stricter limits as documented on each route below."

## Rate Limit Response Headers

All API responses (including errors) may include:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests allowed in the current window |
| `X-RateLimit-Remaining` | Requests remaining in the current window |
| `X-RateLimit-Reset` | Seconds until the rate limit window resets. Can occasionally return negative values or be missing — always clamp calculated wait times to a minimum of 5 seconds. |

## 429 Rate Limit Exceeded Response

### General Schema (most endpoints)

```json
{
  "error_type": "RATE_LIMIT_EXCEEDED",
  "data": {
    "count": 42,
    "limit": 1200,
    "expiry": "Thu, 16 Jul 2026 11:21:18 GMT"
  }
}
```

- `count`: how many requests you've made in the current window
- `limit`: the maximum allowed (1200 for global, lower for per-endpoint)
- `expiry`: **RFC 2822** timestamp when the window resets (NOT ISO 8601). Parse with `email.utils.parsedate_to_datetime()`, not `datetime.fromisoformat()` — the latter crashes with `ValueError: Invalid isoformat string`. This was confirmed during a multi-pass audit of the rate limit discovery script in July 2026.

### Quotes Endpoint Exception (CRITICAL)

The quotes endpoint (`GET /v3/markets/{ids}/quotes/`) uses an **inline 429 schema** that does NOT include `count`, `limit`, or `expiry` fields. Verified from the live OpenAPI spec (July 2026):

```json
{
  "error_type": "RATE_LIMIT_EXCEEDED",
  "data": "string or object"
}
```

The `data` field is typed as `["string", "object"]` — it may contain a simple error message string, not the structured rate limit data. This means:

- Customers hitting the quotes rate limit will NOT see `count`/`limit`/`expiry` in the response body
- They cannot determine when the window resets from the response alone
- The `X-RateLimit-*` response headers may still be present (if the endpoint returns them)
- Do NOT tell customers to "check the expiry field" for quotes endpoint 429s — tell them to wait a short period before retrying

This exception is also noted in `training/customer_faq.md` line 325. The general RateLimitError schema in `components/schemas` (with count/limit/expiry) applies to most GET endpoints but NOT to quotes.

Other endpoints that use the simpler inline 429 schema (without count/limit/expiry): order placement (`POST /v3/orders/`), order cancellation (`DELETE /v3/orders/` and `DELETE /v3/orders/{id}/`), session management (`POST /v3/sessions/`, `DELETE /v3/sessions/`).

## Per-Endpoint Documented Limits (7 of 21 endpoints — live spec 2026-09-23)

| Endpoint | Method | Limit | Window | RPM Equivalent |
|----------|--------|-------|--------|----------------|
| `/v3/events/` | GET | 600 | 60s | 600 rpm |
| `/v3/sessions/` | POST | 5 | 300s | 1 rpm |
| `/v3/sessions/` | DELETE | 30 | 60s | 30 rpm |
| `/v3/markets/{ids}/quotes/` | GET | 50 | 60s | 50 rpm |
| `/v3/orders/` | POST | 10 | 1s | 600 rpm |
| `/v3/orders/` | DELETE | 1 | 60s | 1 rpm |
| `/v3/orders/{order_id}/` | DELETE | 10 | 1s | 600 rpm |

**Quotes has TWO tiers (verified live Aug/Sep 2026):** the quotes endpoint description explicitly says "The rate limits below are applicable to API users. The rate limits for non-API users are lower." 50/60s is the **API-user** limit. Non-API (or not-yet-approved) accounts get a lower cap — observed in the field as `X-RateLimit-Limit: 20` on a 60s window, matching the "lower for non-API users" wording. The global description confirms: "In order to place bets and get the latest prices without restrictions using this API, you need to be a Smarkets API user."

**Diagnosing a reported-header-vs-documented mismatch:** When a customer reports an `X-RateLimit-Limit` header that differs from a documented figure (e.g. 20 vs 50 on quotes), the header is ground truth for that account's *effective* tier — do NOT argue the customer is wrong. The single decision-driving question is whether the account is flagged as an approved API user:
- Not approved → the lower header (20) is correct for its tier; 50 applies once API approval/registration completes. No server-side change; explain the tier to the customer.
- Approved → the header is a genuine server-side mismatch. Escalate internally for correction of the account's effective cap (or to confirm a lower per-account cap set on the approval profile). Do not write "align to 50 / force 20→50" as if it's an agent-side override.

**Sum of per-endpoint limits: 1882 rpm** (1282 + 600 for `GET /v3/events/`) — this EXCEEDS the 1200 global pool.

This means per-endpoint limits are concurrent caps that fire BEFORE the global limit is reached. They are NOT additive allocations of the 1200 pool. The 1200 global limit is the true ceiling; per-endpoint limits are additional restrictions.

## Check Batch Size BEFORE Declining a Throughput Increase

When a customer asks for a higher request rate, first check the endpoint's batch-size parameter — a larger batch often satisfies the throughput need without any cap change, which is a better answer than a decline.

Quotes takes `market_ids` with **`maxItems: 200`** (live spec, re-verified 2026-09-30). The cap is 50 requests per 60s, so throughput is bounded by requests-per-minute × IDs-per-request:

| IDs per call | Calls to cover 2,000 markets | Calls to cover 5,000 markets |
|---|---|---|
| 50 | 40 | 100 (over cap) |
| 100 | 20 | 50 (at cap, zero margin) |
| 200 | 10 | 25 (half the cap) |

A customer batching 100 and asking for "120 to 150 quotes per minute" is usually conflating requests with markets. Doubling the batch to 200 halves their request count and may make the increase unnecessary. Say this before declining, not after. Same check applies to other `maxItems` array params.

Frame the advice as headroom, never as a load-maximisation recipe. Do not present refreshes that consume the full quotes allowance or pin a cadence like "a refresh every ten seconds" even when the arithmetic is right (owner feedback 2026-10-12: reads as irresponsible guidance to load the endpoint). Give the per-call coverage and the request count, then stop. The aggregate ceiling (200 ids x 50 calls = 10k ids/min) is inherent to the published endpoint and stays in internal reasoning only, never in customer text.

### Batch-size hard boundary — over-cap batches return a 404, not a 400 (verified live 2026-10-01)

Exceeding a batch route's `maxItems` returns the **route-miss style 404** — `{"data":{"description":"Nothing matches the given URI"},"error_type":"NOT_FOUND"}` — NOT a 400 REQUEST_VALIDATION_ERROR. Verified with paired live controls on public routes: quotes `n=200` → 200 OK, `n=201` → 404; volumes `n=300` → 200 OK (URL 3,044 chars), `n=301` → 404. Each route flips exactly at its documented cap, so URL length is not the constraint. Support reading: when a customer's batch call 404s with "Nothing matches the given URI", check the ID count against the cap before chasing a phantom dead route.

| Route | maxItems |
|---|---|
| `GET /v3/markets/{ids}/quotes/` | 200 |
| `GET /v3/markets/{ids}/volumes/` | 300 |
| `GET /v3/events/{ids}/states/` | 300 |
| `GET /v3/events/{ids}/competitors/` | 300 |
| `GET /v3/markets/{ids}/contracts/` | 100 |
| `GET /v3/markets/{ids}/last_executed_prices/` | 100 |
| `GET /v3/events/{ids}/markets/` | 50 |
| `GET /v3/events/{ids}/markets_count/` | 50 |

Throughput ceilings for scale planning: quotes 200 ids/call × 50 calls/60s = up to 10,000 market ids/min for an approved API user; volumes 300 ids/call shares the 1200 RPM global pool. Raw captures: `~/smarkets-api-support/responses/2026-10-01-batch-boundary/`.

Cancelling in batches has the opposite trap: cancel-one is 10/s but cancel-all is 1 per 60s. A customer spacing single cancellations at 1.5s is nowhere near their real constraint and will not be warned by the placement limit.

## Endpoints WITHOUT Per-Endpoint Limits (14 endpoints)

These endpoints share the 1200 RPM global pool with no individual cap:

1. `POST /v3/sessions/verify/` (MFA verification)
2. `GET /v3/events/{ids}/states/` (event states)
3. `GET /v3/events/{ids}/competitors/` (competitors)
4. `GET /v3/events/{ids}/markets/` (markets for events)
5. `GET /v3/events/{ids}/markets_count/` (market counts)
6. `GET /v3/markets/{ids}/contracts/` (contracts)
7. `GET /v3/markets/{ids}/last_executed_prices/` (last trade prices)
8. `GET /v3/markets/{ids}/volumes/` (traded volumes)
9. `GET /v3/orders/` (open + settled orders)
10. `GET /v3/orders/fullcover/` (fullcover orders)
11. `GET /v3/accounts/` (balance, exposure)
12. `GET /v3/accounts/activity/` (account statement)
13. `GET /v3/account_activity_csv/{start}/{end}/` (CSV export)
14. `GET /v3/currencies/{code}/` (FX rates)

## Discrepancy: POST /v3/orders/ Limit

**Local file `responses/api-scope-confirmation.txt` says:** "Order placement (POST /v3/orders/): throttled on a per-account basis, no specific published number"

**Live OpenAPI spec says:** "Maximum 10 requests per second"

The live spec is authoritative. If a customer asks about order placement rate limits, cite 10 requests per second, not "no specific published number."

## Live Test Observations (July 2026)

### Phase 1 — Smoke Test (single request per endpoint)

Tested via `scripts/rate_limit_discovery.py` Phase 1 smoke test:

- **POST /v3/sessions/** (invalid credentials, 400 response): Rate limit headers returned — `limit=5 remaining=4 reset=299s`. Confirms the 5/300s documented limit. This endpoint has its own rate limiter that fires regardless of auth status (brute-force protection on login).
- **Public GET endpoints** (events, currencies, contracts, markets): All returned 200 but did NOT include X-RateLimit-* headers. Confirmed explanation (see Phase 2 below): rate limits are per-account, and without a session token there is no account to rate-limit against.

### Phase 2 — No-Auth Rate Limit Hammer Test (CRITICAL FINDING)

Hammered `GET /v3/events/` with 20 concurrent threads, NO authentication:

- **18,141 requests in 90 seconds** (12,086 RPM)
- **Zero 429s. Every single request returned 200.**
- **No X-RateLimit-* headers** on any response
- Cloudflare sits in front (`CF-RAY` headers present) but does not apply API rate limits to unauthenticated traffic

**Conclusion: The 1200 RPM limit is per-account (session token), NOT per-IP.** Without a session token, public endpoints are effectively unlimited. This means:

1. The 1200 RPM global limit only applies to authenticated API users
2. Public endpoints (events, markets, contracts, currencies) can be polled without rate limits if no session token is sent
3. Authenticated endpoints (quotes, orders, accounts) require a session token, so the 1200 RPM limit always applies to them
4. `POST /v3/sessions/` is the exception — it has its own rate limiter (5/300s) that fires even without valid credentials

**Support implication:** If a customer asks about rate limits for public data access (events, markets, contracts), the answer is: no rate limit applies to unauthenticated requests. The 1200 RPM limit is tied to the account, not the IP. However, customers should still use a session token for real-time (non-delayed) quotes data.

### Authentication: Login Response, Token Field, and Auth Methods

**Login request:** `POST /v3/sessions/` with `{"username": "user@example.com", "password": "..."}`

The API requires `username` as the JSON key, with the email address as the value. The OpenAPI spec confirms: `"username": {"format": "email", "example": "john.doe@company.com"}`. Using `email` as the key returns `REQUEST_VALIDATION_ERROR: data must contain ['password', 'username'] properties`.

**Login response status: 201, NOT 200.** Successful session creation returns HTTP 201 (Created), not 200 OK. Scripts that check `if r.status_code == 200` will fail to parse the token. Always check `if r.status_code in (200, 201)`.

**Token field: `token`, NOT `session_token`.** The 201 response body contains:

```json
{"token": "BQQBAAAA...", "refresh_token": "BgIBAA...", "factor": "complete", "stop": "2026-07-16T14:40:02.708970", "verify": false}
```

Extract with `data.get("token")`, not `data.get("session_token")`.

**Three auth methods all work** for authenticated endpoints (confirmed July 2026):

| Method | Header/Cookie | Example |
|--------|---------------|---------|
| Authorization header (Session-Token) | `Authorization: Session-Token {token}` | Primary method used by discovery script |
| Cookie | `Cookie: User-Session-Token={token}` | Also set automatically by login response |
| Authorization header (Bearer) | `Authorization: Bearer {token}` | Also works |

All three return 200 on `GET /v3/accounts/`. The `Session-Token` header is the documented method; `Bearer` also works but is not officially documented.

**Pitfall: Login rate limit burns fast during debugging.** The 5/300s limit on `POST /v3/sessions/` is per-account and fires even on failed attempts. A few test logins during development will trigger 429. When this happens, the 429 response includes the standard rate limit data with RFC 2822 expiry. Wait for the window to reset (typically 4-5 minutes) before retrying.

## Discovery Methodology

The full rate limit discovery script lives at `~/smarkets-api-support/scripts/rate_limit_discovery.py` (also published at https://github.com/smiley1910/smarkets-rate-limit-discovery). The skill's `scripts/rate_limit_quick_check.py` is a lightweight version that hits each endpoint once. The full script implements a 4-phase approach:

1. **Phase 1 — Smoke test:** One request per endpoint, capture status + rate limit headers
2. **Phase 2 — Per-endpoint probe:** Hammer each safe endpoint until 429, then wait for reset
3. **Phase 3 — Shared pool test:** Fire all endpoints concurrently to test if 1200 is truly shared
4. **Phase 4 — Aggregate analysis:** Compare documented vs discovered limits, calculate 1200 breakdown

The script is safe to run: does NOT place orders, does NOT cancel real orders (uses fake UUID), does NOT logout until the end.

For audit patterns, thread safety rules, and security hardening when building or reviewing rate limit discovery scripts, see `references/rate-limit-script-audit.md`.

## How to Fetch the Live OpenAPI Spec

```bash
# Get the full live spec (JSON)
curl -sL "https://api.smarkets.com/v0/control/openapi/?tags=trading_api" | python3 -m json.tool

# Extract just the rate limit info from descriptions
curl -sL "https://api.smarkets.com/v0/control/openapi/?tags=trading_api" | python3 -c "
import json, sys
spec = json.load(sys.stdin)
print(spec.get('info', {}).get('description', 'N/A'))
for path, methods in spec.get('paths', {}).items():
    for method, details in methods.items():
        desc = details.get('description', '')
        if 'rate' in desc.lower() or 'limit' in desc.lower():
            print(f'\n{method.upper()} {path}:')
            print(desc[:500])
"
```

The Swagger UI at `docs.smarkets.com` loads this spec in the browser. The spec URL is embedded in the page's JavaScript: `url: "https://api.smarkets.com/v0/control/openapi/?tags=trading_api"`.
