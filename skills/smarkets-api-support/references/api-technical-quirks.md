# Smarkets API — Technical Quirks (Verified July 2026)

Session-verified API details discovered while building trading tools and rate limit testing scripts. These are facts that support agents and developers need when debugging or building against the Smarkets HTTP Trading API.

## Authentication

### Login endpoint: `POST /v3/sessions/`
- **Returns 201 (Created) on success**, NOT 200. Code checking for `status_code == 200` will fail.
- Response body: `{"token": "...", "refresh_token": "...", "factor": "complete", "stop": "...", "verify": false, "created_social_member": false}`
- **Token field is `token`**, NOT `session_token`. This was a bug in our rate limit script.
- Token is also set as cookie `User-Session-Token`.
- Login JSON body uses `{"username": "<email>", "password": "***"}` — the field is `username`, not `email`, even though the value is an email address.
- Auth methods that all work: `Authorization: Session-Token <token>`, `Authorization: Bearer <token>`, cookie `User-Session-Token`.

### Token TTL — 30 minutes with sliding renewal (NOT 24 hours)

- Session tokens are valid for **30 minutes**, not 24 hours.
- Each authenticated request **renews** the token for another 30 minutes.
- As long as the customer makes an authenticated request at least every 30 minutes, the token stays alive indefinitely.
- If 30 minutes pass without an authenticated request, the token expires and the customer must log in again via `POST /v3/sessions/`.

**Correction (verified live 2026-10-01):** the sliding renewal description does not hold for header-only clients. Session tokens rotate on a ~20 minute cycle and renewal runs through the session and refresh tokens, as cookies. A client that sends only `Authorization: Session-Token` is rejected with `401 AUTH_REQUIRED` at the first rotation (observed at 20.0 to 20.2 minutes in every run, before the 30 minute `stop` value), however often it polls. Fix: send `Cookie: User-Session-Token=<token>; Refresh-Token=<refresh_token>` with every request and adopt each renewed `User-Session-Token`. Full case: `references/session-token-rotation-cookie-refresh.md`.
- The login response includes a `stop` field with the expiry timestamp (e.g., `"stop": "2026-07-16T14:40:02.708970"`).

**Common customer misconception (July 2026):** Customers may claim a "24-hour TTL" for their session token. This is wrong. The actual TTL is 30 minutes with sliding renewal. If a customer says their token was valid because "it had only been active for ~2.5 hours against a 24-hour TTL," correct them: tokens are valid for 30 minutes and renew on each authenticated request. The token's age since login is irrelevant — what matters is whether they've made an authenticated request within the last 30 minutes.

**Sources:** `training/pattern_matching_guide.md` line 70, `training/customer_faq.md` line 94, `training/confluence_draft_v2.md`.

### Session rate limit
- `POST /v3/sessions/` has a **5 requests per 300 seconds** rate limit.
- This is VERY easy to burn through during debugging. Each test login + each script run = 1 request.
- If you hit it, you get 429 with `{"data": {"count": N, "expiry": "RFC_2822_TIMESTAMP", "limit": 5}}`.
- The `expiry` field is in **RFC 2822 format** (`Thu, 16 Jul 2026 11:21:18 GMT`), NOT ISO 8601. Use `email.utils.parsedate_to_datetime()` to parse it.
- Wait time is typically ~4-5 minutes for the window to reset.

## OpenAPI Spec

- **Live spec URL:** `https://api.smarkets.com/v0/control/openapi/` — note this is **v0**, not v3.
- The spec contains all trading API endpoints, request/response schemas, and rate limit documentation.
- Can be fetched with a simple `curl -sL` or `requests.get()`.

## Finding Horse Racing Events

- `GET /v3/events/` with `type=horse_racing` returns **400** (invalid type value).
- `GET /v3/events/` with `type_domain=horse-racing` returns **empty results**.
- `GET /v3/events/` with `state=upcoming` returns **empty results**.
- **Working approach:** Use `GET /v3/search/horse/` to get event IDs, then fetch details with `GET /v3/events/{ids}/`.
- The event `type` field for horse races is `horse_racing_race`.
- Filter for upcoming races by comparing `start_datetime` to current UTC time.
- Events return `start_datetime` in ISO format with Z suffix (e.g., `2026-07-16T14:25:00Z`).

## Quotes Structure

- `GET /v3/markets/{market_id}/quotes/` requires authentication.
- **maxItems: 200** — the endpoint accepts up to 200 market IDs per request (live OpenAPI spec, verified July 2026). Customers batching fewer IDs per request can increase batch size to reduce request count. The rate limit is 50 requests per 60 seconds, so larger batches = fewer requests against the limit.
- Response format: `{"<contract_id>": {"bids": [...], "offers": [...]}}`
- **bids** = back orders resting in the book (sorted descending by price)
- **offers** = lay orders resting in the book (sorted ascending by price)
- To BACK a horse: match the lowest offer (offers[0])
- To LAY a horse: match the highest bid (bids[0])
- Each bid/offer has `{"price": <int>, "quantity": <int>}`
- The favourite = contract with the **highest best-offer price** (lowest decimal odds)

### Quotes Endpoint Documented Error Responses (live spec, July 2026)

The live OpenAPI spec documents these response codes for `GET /v3/markets/{market_ids}/quotes/`:

| Status | error_type | Notes |
|--------|-----------|-------|
| 200 | — | Success: order book with bids/offers arrays |
| 400 | BAD_REQUEST, REQUEST_VALIDATION_ERROR | Invalid market IDs or parameters |
| 401 | AUTH_REQUIRED | Authentication not accepted |
| 403 | FORBIDDEN | Account-level access issue |
| 429 | RATE_LIMIT_EXCEEDED | Inline schema WITHOUT count/limit/expiry (see rate-limits.md) |
| 500 | INTERNAL_ERROR | Server error (uses components/schemas/InternalServerError) |
| 503 | MDS_SERVICE_UNAVAILABLE, SBK_PRICER_UNAVAILABLE, CHARTS_INTERNAL_ERROR, CHARTS_UNAVAILABLE | Internal service dependencies |

The 503 error types reveal internal service names (MDS = Market Data Service, SBK Pricer, Charts). These suggest the quotes endpoint depends on downstream services that can be temporarily unavailable. A mass 401 event affecting all quotes requests while other endpoints return 200 is consistent with a transient issue in the auth validation layer for this endpoint specifically.

## Order Placement

- `POST /v3/orders/` with JSON body.
- **Price:** basis points. 5000 = 50% = 2.0 decimal odds. Formula: `10000 / price = decimal_odds`.
- **Quantity:** 1/10000 of currency unit. Back stake = `quantity * price / 100000000`.
  - Example: for €0.05 back at price 4237 (2.36 odds): quantity = `0.05 * 100000000 / 4237 = 1180`.
- **Side:** `buy` = back, `sell` = lay.
- **Type:** `immediate_or_cancel` (fill or kill), `good_til_cancelled`, `good_til_halted`, `keep_in_play`.
- **Minimum stake:** £0.05 or currency equivalent.
- Response includes `order_id`, `executed_avg_price`, `total_executed_quantity`, `available_balance`, `exposure`.
- Rate limit: 10 requests per second on this endpoint.

## Rate Limit Headers

- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
- Only returned on endpoints that have per-endpoint limits (sessions, orders, quotes, etc.).
- Public endpoints (events, currencies, contracts) do NOT return rate limit headers.
- 429 response includes `expiry` in RFC 2822 format — use `email.utils.parsedate_to_datetime()`.

## Market Structure

- Horse racing events have 3 markets: "To win", "To place (top 2)", "To place (top 3)".
- `GET /v3/events/{event_id}/markets/` returns all markets for an event.
- `GET /v3/markets/{market_id}/contracts/` returns all contracts (horses) for a market.
- Contract fields: `id`, `name` (or `runner_name`).

## Global Rate Limit

- 1200 RPM across all endpoints, per account.
- Per-endpoint caps (e.g., 10/sec for orders, 50/min for quotes, 5/300s for sessions) are maximums, NOT additive.
- The sum of documented per-endpoint limits (1282 RPM) exceeds the global pool (1200 RPM).
- Unauthenticated traffic does NOT count toward the 1200 RPM cap — public endpoints can be hammered freely.
