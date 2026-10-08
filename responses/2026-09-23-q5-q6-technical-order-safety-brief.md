# Q5 (technical) + Q6 (order safety / settlement) — evidence brief

Internal research artifact. Not customer-facing prose. Every claim carries a source tag.

## Source key

| Tag | Source | Identity |
|---|---|---|
| SPEC-LIVE | `https://api.smarkets.com/v0/control/openapi/?tags=trading_api` | fetched 2026-09-23T09:34Z, HTTP 200, 195,215 bytes, md5 `b5ce731b0cce3465687c9b949b908a9a` |
| SPEC-LOCAL | `~/smarkets-api-support/openapi/smarkets_openapi.json` | 192,568 bytes, md5 `afec019e8b174fe3e8cb3c9e7bb3d99b`, mtime 2026-08-18; **byte-identical** to `~/smarkets-api-support/smarkets_openapi.json` and `~/smarkets-api-support/scrape-aug18/live_trading.json` |
| DOCS-ENDPOINTS | `~/smarkets-api-support/docs/api_endpoints_reference.md` | local derivative of SPEC-LOCAL |
| DOCS-SCHEMAS | `~/smarkets-api-support/docs/request_response_schemas.md` | local derivative of SPEC-LOCAL |
| API-TCS | `~/smarkets-api-support/scrape-aug18/help/api-tcs.md` | help-centre "Smarkets API: Access, Integration & T&Cs" scrape, 2026-08-18 |
| TICK-HELP | `~/smarkets-api-support/help-pages/smarkets/en-gb/115003210649_Why_can_t_I_bet_at_specific_odds.md` | help-centre article, scraped 2026-06-29 |
| MIN-HELP | `~/smarkets-api-support/help-pages/smarkets/en-gb/212727285_Minimum_and_maximum_stakes.md` | help-centre article |
| FAQ-LOCAL | `~/smarkets-api-support/training/customer_faq.md` | internal training FAQ |
| HERMES-REF | `~/smarkets-api-support/HERMES_REFERENCE.md` | internal ops note |
| PRECEDENT-SCOPE | `~/smarkets-api-support/responses/api-scope-confirmation.txt` | prior internal reply precedent |
| PRECEDENT-WS | `~/smarkets-api-support/responses/2026-09-16-websocket-and-ratelimits-v4-FINAL.txt` | prior internal reply precedent |
| LIVE-TEST | direct unauthenticated `curl` run 2026-09-23T09:34Z (read-only GETs, no orders) | evidence in §Q5.5 |

Spec citation format below is `SPEC.path`: e.g. `SPEC-LIVE .paths["/v3/sessions/"].post.description`.

---

## Q5 — technical requirements

### Q5.1 `api_base`
- `https://api.smarkets.com` — SPEC-LIVE `servers: [{"description":"Production","url":"https://api.smarkets.com"}]` (identical in SPEC-LOCAL). Single server object; **no** alternate/sandbox/test host in the spec. All 21 paths are under `/v3/`.
- Path set is identical between SPEC-LIVE and SPEC-LOCAL (21 paths; no additions/removals; no `security` diffs).

### Q5.2 `auth_method` + header format
- Scheme: SPEC-LIVE `.components.securitySchemes.api_key` = `{type: apiKey, in: header, name: Authorization}`. No OAuth, no API-key-per-app, no HMAC.
- Header value format, verbatim: *"This will return a token that can be used in the Authentication header in the form "Session-Token <your_token>" on authenticated requests."* — SPEC-LIVE `.paths["/v3/sessions/"].post.description`.
- Login: `POST /v3/sessions/`, body requires `password` + `username` (schema `username` has `format: email`), HTTP **201** on success. Token field in 201 body is `token` (required alongside `stop`). — SPEC-LIVE `.paths["/v3/sessions/"].post.requestBody`, `.responses["201"]`.
- MFA path: `POST /v3/sessions/verify/` — token + TOTP code; `factor` enum `complete|totp|nemid`; 403 codes include `LOGIN_VERIFICATION_REQUIRED`, `IP_NOT_TRUSTED`, `DEVICE_NOT_TRUSTED`, `SESSION_LIMIT_REACHED`. — SPEC-LIVE `.paths["/v3/sessions/verify/"].post.description`, `.paths["/v3/sessions/"].post.responses["403"]`.
- Auth-v2 variant: `use_auth_v2: true` in the login body → *"should expect refresh_token and access_token in the cookies and response"*; `remember: true` = *"allow this device to renew the token even after its expiration"*. 201 body is a `oneOf` of the legacy token response and the auth-v2 response (which adds `refresh_token`). — SPEC-LIVE `.paths["/v3/sessions/"].post.requestBody`, `.responses["201"].content["application/json"].schema.oneOf[1]`.
- Logout: `DELETE /v3/sessions/` (`security: null` in spec; token carried by the session). — SPEC-LIVE `.paths["/v3/sessions/"].delete`.
- No customer-facing key provisioning is described in the auth scheme; only the session token. (API-TCS mentions a £150 activation fee — that is fees scope, excluded here, cited only as context.)

### Q5.3 `token_TTL`
- **30 minutes, sliding.** Verbatim: *"The token is valid for 30min, but if you make an authenticated request with it, it will be renewed for the next 30min."* — SPEC-LIVE `.paths["/v3/sessions/"].post.description` (same text in SPEC-LOCAL; also mirrored in DOCS-SCHEMAS lines 104-107).
- Response field `stop`: *"This datetime specifies when the token will expire if not renewed. Any authenticated API call will automatically renew the token for another 30min"* — SPEC-LIVE `.responses["201"]...properties.stop`.
- 401 `AUTH_REQUIRED` on authenticated endpoints when the token is absent/expired: SPEC-LIVE `.paths["/v3/orders/"].post.responses["401"]`, `.paths["/v3/accounts/"].get.responses["401"]`; confirmed live unauthenticated (LIVE-TEST: `{"data":null,"error_type":"AUTH_REQUIRED"}` HTTP 401 on `GET /v3/accounts/` and `GET /v3/orders/`).
- Practical consequence for a long-running personal client: an authenticated request at least every 30 min keeps the token alive; `use_auth_v2` + `refresh_token`, or `remember: true`, are the documented renewal paths after expiry. (Mechanism per SPEC-LIVE fields above; no further TTL documentation exists.)

### Q5.4 `rate_limits`

**global** — *"All API users are subject to a default rate limit of 1200 requests per 60 seconds across all endpoints, applied per account. Individual endpoints may have additional stricter limits as documented on each route below."* — SPEC-LIVE `info.description`. Enforcement metadata: 429 with `error_type: RATE_LIMIT_EXCEEDED`; response headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` — SPEC-LIVE `info.description`. Most GET endpoints' 429 body is the `RateLimitError` component = `{data:{count,limit,expiry}, error_type}` (all three required) — SPEC-LIVE `.components.schemas.RateLimitError`.

**Per-endpoint "Maximum" lines — SPEC-LIVE (authoritative, fetched today):**

| Endpoint | Cap | Source |
|---|---|---|
| Any | 1200 req / 60 s per account | `info.description` |
| `GET /v3/events/` | **600 req / 60 s** | `.paths["/v3/events/"].get.description` |
| `GET /v3/markets/{market_ids}/quotes/` | 50 req / 60 s — plus *"The rate limits below are applicable to API users. The rate limits for non-API users are lower."* | `.paths[...quotes...].get.description` |
| `POST /v3/orders/` | 10 req / s | `.paths["/v3/orders/"].post.description` |
| `DELETE /v3/orders/{order_id}/` | 10 req / s | `.paths["/v3/orders/{order_id}/"].delete.description` |
| `DELETE /v3/orders/` (cancel all) | 1 req / 60 s | `.paths["/v3/orders/"].delete.description` |
| `POST /v3/sessions/` (login) | 5 req / 300 s | `.paths["/v3/sessions/"].post.description` |
| `DELETE /v3/sessions/` (logout) | 30 req / 60 s | `.paths["/v3/sessions/"].delete.description` |

- **SPEC-LOCAL is stale on exactly one of these:** it lacks the `GET /v3/events/` `Maximum 600 requests per 60 seconds` block. A full description diff between SPEC-LIVE and SPEC-LOCAL returns `GET /v3/events/` as the only difference across all 21 paths. Any brief that lists "6 endpoints with caps" is now wrong: SPEC-LIVE has **7**.
- **quotes** — no cap for `volumes`-class traffic; quotes-specific 429 is **inline** (`{data: string|object, error_type}`), i.e. it does **not** carry `count`/`limit`/`expiry` — SPEC-LIVE `.paths[...quotes...].get.responses["429"]`. Do not tell a client to read `expiry` from a quotes 429.
- **volumes** — `GET /v3/markets/{market_ids}/volumes/` has **no per-endpoint Maximum line** in either spec; it shares the 1200/60s global pool. Its 429 *does* use the structured `RateLimitError` (count/limit/expiry) — SPEC-LIVE `.paths[...volumes...].get.responses["429"]`.
- **orders** — three caps (10/s place, 10/s cancel-one, 1/60s cancel-all), all with **inline** 429 schemas (no count/limit/expiry) — SPEC-LIVE `.paths["/v3/orders/"].post.responses["429"]`, `.delete.responses["429"]`, `.paths["/v3/orders/{order_id}/"].delete.responses["429"]`. `GET /v3/orders/` has no per-endpoint cap and does use `RateLimitError`.
- Pre-approval framing: *"Smarkets will preapprove call limits per period. Exceeding them may lead to temporary suspension; and repeated violations could result in API or account access being permanently revoked."* — API-TCS §5. Also API-TCS §6.1: *"By connecting, you agree to adhere to the access, call, and usage limits as notified."*
- **Internal discrepancy flagged (do not use the stale line):** `~/smarkets-api-support/responses/api-scope-confirmation.txt` states order placement has "no specific published number"; SPEC-LIVE documents 10/s. (Same discrepancy already logged in the skill's `references/rate-limits.md`.)

### Q5.5 quotes/volumes security (spec position vs observed behaviour)
- Spec position: `security: [{"api_key": []}]` on **both** `quotes` and `volumes` — SPEC-LIVE `.paths[...quotes...].get.security`, `.paths[...volumes...].get.security`. The only public (`security: null`) endpoints are: `GET /v3/events/`, `/events/{ids}/competitors/`, `/events/{ids}/markets/`, `/events/{ids}/markets_count/`, `/events/{ids}/states/`, `/markets/{ids}/contracts/`, `/currencies/{code}/`, `POST|DELETE /v3/sessions/`, `POST /v3/sessions/verify/`.
- Quotes description explicitly contemplates unauthenticated callers: *"If session token is not sent, these prices will be delayed."* — SPEC-LIVE `.paths[...quotes...].get.description`.
- LIVE-TEST (unauthenticated, 2026-09-23T09:34Z, market 153894927):
  - `GET /v3/markets/153894927/quotes/` → HTTP 200, full bids/offers ladder returned; response headers `x-ratelimit-limit: 20`, `x-ratelimit-remaining: 19`, `x-ratelimit-reset: 59`. This is the "lower for non-API users" tier actually firing at **20/60s**.
  - `GET /v3/markets/153894927/volumes/` → HTTP 200 with data (`{"volumes":[{"double_stake_volume":5648,"market_id":"153894927","volume":9016}]}`); no `x-ratelimit-*` headers returned.
  - `GET /v3/accounts/` and `GET /v3/orders/` → HTTP 401 `AUTH_REQUIRED`.
- Net: quotes and volumes are **readable unauthenticated but at a degraded tier** (delayed prices + lower cap); authenticated requests are required for account/order state and for unrestricted (non-delayed) prices — SPEC-LIVE `info.description` (*"In order to place bets and get the latest prices without restrictions using this API, you need to be a Smarkets API user."*).

### Q5.6 `streaming_position`
- **REST only.** SPEC-LIVE contains zero occurrences of `stream`, `websocket`, `ws://`, or `socket` anywhere in the document (verified by full-text scan of the JSON). Market data is obtained by polling `quotes`, `last_executed_prices`, `volumes`, `events/{ids}/states`.
- Prior internal precedent (approved wording): *"The API doesn't offer websockets or a streaming feed: it is REST only, so there is no websocket interface to connect to, and price updates come from polling the documented endpoints."* — PRECEDENT-WS line 3.
- Legacy artefact, do not offer: `stream.smarkets.com:3801` (protobuf-over-TCP) belonged to the archived `smk_python_sdk`; `sio-live.smarkets.com` is the website frontend channel, not a documented API surface. — skill `references/streaming-infrastructure-and-cftc-product.md`, `references/deprecated-streaming-api-and-sio-live.md`; summarised in HERMES-REF lines 27-29.
- Operational consequence: any client needing sub-second updates must poll within the quotes cap (50/60s for API users, observed 20/60s unauthenticated).

### Q5.7 `min_trading_requirement`
- **NOT_DOCUMENTED as a numeric requirement.** No minimum stake, minimum monthly volume, or minimum activity threshold for API access appears in SPEC-LIVE/SPEC-LOCAL (full-text scan: `minimum` appears only in schema bounds — e.g. `price.minimum: 1`, `quantity.minimum: 0`, `minimum_accepted_quantity.minimum: 0`).
- The only documented constraint in this direction is a fair-usage prohibition, not a threshold: *"Use the API strictly for data extraction purposes without commensurate trading volumes"* is listed under what you agree **not** to do — API-TCS §6.1. No figure is attached to "commensurate".
- Adjacent documented requirement (not a volume minimum): account must be a *"fully registered and verified Smarkets account"* and access is via *"an application process"* — API-TCS §2. Eligibility gating on the trading routes: `POST /v3/orders/` *"only works for Smarkets API users, other users will receive a 403 status code response"* — SPEC-LIVE `.paths["/v3/orders/"].post.description`.

### Q5.8 `ip_restrictions`
- **No IP allowlist/whitelist feature is documented.** SPEC-LIVE/SPEC-LOCAL full-text scan: zero occurrences of `whitelist`, `allowlist`, `ip address`. Internal position: *"IP whitelisting is not a documented feature of the API. Contact support to discuss your specific situation."* — FAQ-LOCAL line 541.
- IP-related *rejection* codes do exist and fire at login: 403 `IP_NOT_TRUSTED`, `SOURCE_BLOCKED`, `CLIENT_JURISDICTION_MISMATCH`, `DEVICE_NOT_TRUSTED` on `POST /v3/sessions/` — SPEC-LIVE `.paths["/v3/sessions/"].post.responses["403"]`. (The same codes appear on `/v3/sessions/verify/`.) So the API can and does refuse a source IP/device/jurisdiction even though there is no customer-configurable allowlist.
- Also documented: `451 COUNTRY_BLOCKED` on login — SPEC-LIVE `.paths["/v3/sessions/"].post.responses["451"]`; `403 FORBIDDEN` (generic) on trading/market-data routes — SPEC-LIVE `.paths["/v3/orders/"].post.responses["403"]`.
- Internal ops note (not public doc): jurisdiction checks plus IP reputation on datacenter IPs; Cloudflare edge blocks can appear as an HTML 403 rather than a JSON API 403; datacenter IPs in supported jurisdictions may require an internal allowlisting request to api@smarkets.com — HERMES-REF lines 22-25. Treat as internal-only until confirmed.

### Q5.9 `testing_sandbox`
- **N.** No sandbox/test environment is documented. SPEC-LIVE has a single `servers` entry (Production) and zero occurrences of `sandbox`. The only `test`-like string in SPEC-LIVE is a third-party KYC redirect example host (`https://test.zignsec.com/...`) in the NemID flow — not an API environment.
- Approved precedent wording: *"The API doesn't have a dedicated test or sandbox environment, so when you're ready to test order placement, you'll be using live funds. For read-only development work, the public endpoints (events, markets, contracts) are available without authentication."* — PRECEDENT-SCOPE line 66.
- **Read-only public endpoints note (spec-verified list, no session token required, `security: null`):** `GET /v3/events/`, `GET /v3/events/{event_ids}/competitors/`, `GET /v3/events/{event_ids}/markets/`, `GET /v3/events/{event_ids}/markets_count/`, `GET /v3/events/{event_ids}/states/`, `GET /v3/markets/{market_ids}/contracts/`, `GET /v3/currencies/{code}/` — SPEC-LIVE per-path `security` blocks. Additionally observed in LIVE-TEST: `quotes` and `volumes` return data unauthenticated (delayed / lower tier) despite declaring `api_key` security.
- Warning: `training/confluence_draft_v2.md` claims a paper-trading environment exists — that contradicts the spec and the red-team audit (skill `references/documentation-redteam-audit-june-2026.md`, row 20). Do not use it.

---

## Q6 — order safety / settlement

### Q6.1 `price_units`
- Integer percentage basis points out of **10,000**. Verbatim: *"This price is in percentage basis points. Example: 5000 = 50%. To convert it to decimal odds, just divide 10000 by it. Example: 10000 / 5000 = 2.0 (decimal odds)."* — SPEC-LIVE `.paths["/v3/orders/"].post.requestBody...properties.price.description` (same text on the `price` field of order responses and of quotes ticks).
- Schema bounds: `type: integer`, `minimum: 1`, `maximum: 9999` — same location.
- Higher-precision variant for reconciliation: `average_price_matched_precise` — *"This price is in percentage basis points with full precision (up to 6 decimal places). Example: 5000 = 50%, 71.234567 = 0.71234567%. Use this field when deriving stake or returns from quantity to avoid rounding error, particularly after reduction factors are applied."* — SPEC-LIVE `.paths["/v3/orders/"].get.responses["200"]...properties.average_price_matched_precise`.
- `average_price_matched` (integer) may differ from the submitted price: *"This price can be different from the order price, as it may have been matched at a better price for the user, according to best price execution rules"* — SPEC-LIVE same response, `...average_price_matched.description`.

### Q6.2 `quantity_stake_liability_units`
- `quantity` = matched pot (back + lay), in **1/10,000 of one unit of the user's currency**. Verbatim (POST request + most response fields): *"Quantity is the sum of the total pot (back+lay) in case the order is matched. The units are 1/10000 * one unit of the user's currency. Example: Quantity 500 = 0.05 GBP. To convert it to back stake, just multiply by the price and divide by 100000000. Example: 100000 (quantity) * 5000 (price) / 100000000 = 5 GBP back stake. The minimum stake is £0.05 or currency equivalent"* — SPEC-LIVE `.paths["/v3/orders/"].post.requestBody...properties.quantity.description`.
- **Spec wording inconsistency (both copies):** the same field on `GET /v3/orders/` and on quotes ticks is described as *"The units are 1/100 of a UK penny"* — numerically identical (1/100 penny = 1/10,000 pound) but differently worded — SPEC-LIVE `.paths["/v3/orders/"].get.responses["200"]...quantity.description`, `.paths[...quotes...].get.responses["200"]...quantity.description`. Quote the 1/10,000 phrasing in any brief.
- Schema bounds: `integer`, `minimum: 0`, `maximum: 4294967295` (uint32) on order paths; quotes tick quantities allow up to `18446744073709551615` (uint64) — SPEC-LIVE respective `quantity` schemas.
- Derived conversions (arithmetic, not verbatim in spec):
  - `back stake (currency units) = quantity × price / 100,000,000`
  - `pot (currency units) = quantity / 10,000`
  - `lay liability (currency units) = quantity × (10,000 − price) / 100,000,000` — **DERIVED**, not stated in the API spec; lay liability is defined in the help centre as `Liability = Backer's stake × (Lay odds − 1)` (`help-pages/.../115003381865_How_to_calculate_the_liability_of_a_lay_bet.md`).
- Exposure/balance semantics: `available_balance` = *"equal to the balance deducted by the exposure"*; `exposure` returned on the order-placement response and on `GET /v3/accounts/` — SPEC-LIVE `.paths["/v3/orders/"].post.responses["200"]...properties.available_balance|exposure.description`, `.paths["/v3/accounts/"].get.responses["200"]...properties.exposure.description`.

### Q6.3 `min_sizes`
- **Minimum stake: £0.05 (or currency equivalent)** — verbatim in the `quantity` description on order and quote schemas (SPEC-LIVE, see Q6.2), and in MIN-HELP: *"The minimum stake is £/€ 0.05 and the maximum stake per bet is £/€ 99,999.99. You can stake larger amounts by placing multiple separate bets."*
- Schema floor for the field itself is `minimum: 0`, so the £0.05 floor is a **business rule**, not a schema bound — SPEC-LIVE `quantity.minimum: 0`.
- Minimum *matched* size on an IOC: `minimum_accepted_quantity` — *"If this minimum accepted quantity is not matched on bet placement time, the order will be cancelled and nothing will be matched. Only applicable to immediate_or_cancel order types."* — SPEC-LIVE `.paths["/v3/orders/"].post.requestBody...properties.minimum_accepted_quantity.description`.
- No documented minimum **order-book** size (i.e. no stated minimum resting quantity beyond the £0.05 stake rule). Internal rag-context asserts a minimum quantity of 500 units (= £0.05 pot); that is an internal interpretation, not spec text — `rag-context/api-support.md`.

### Q6.4 `price_increments`
- **STATE_NOT_DOCUMENTED in the API spec.** SPEC-LIVE/SPEC-LOCAL contain **zero** occurrences of `increment` and no tick-size table. The only API-level statement is a validity condition, not a table: *"This price has to conform to a valid tick on the exchange; an invalid price error will be returned if it does not."* — SPEC-LIVE `.paths["/v3/orders/"].post.requestBody...properties.price.description`. The corresponding rejection code is `ORDER_INVALID_INVALID_PRICE` (400) — SPEC-LIVE `.paths["/v3/orders/"].post.responses["400"]`.
- The increments themselves are published only at website/help-centre level: *"Tick size is the minimum price movement… For instance if you wanted to bet at 6.1 our system would only allow you to bet at 6 or 6.2."* followed by the full tradable price mapping table (decimal odds ↔ %) — TICK-HELP (`help-pages/smarkets/en-gb/115003210649_Why_can_t_I_bet_at_specific_odds.md`). Table includes the top-end rungs `300 0.33% / 500 0.20% / 1000 0.10% / 10000 0.01%`.
- Client-side implication: submit integer basis points that map onto a rung of that table; off-rung integers are rejected (code above), so a mapping/validation table must be maintained client-side. Whether the help-centre table is the authoritative API-side tick set is unconfirmed → GAP.

### Q6.5 `partial_fills`
- Supported and first-class. Order `state` enum: `created` (unmatched) / `partial` (partially matched) / `filled` (fully matched) / `settled` (final) — SPEC-LIVE `.paths["/v3/orders/"].get.responses["200"]...properties.state.description`; also a `state` filter parameter on the same route.
- Fill quantities on `GET /v3/orders/`: `quantity_filled` (*"The quantity in GBP of the order that was matched"*), `quantity_unfilled` (*"…still unmatched"*), plus `_user_currency` variants and `quantity_traded_out_user_currency` — SPEC-LIVE same response.
- On the placement response: `available_quantity` (*"Quantity left to be matched in the order"*), `executed_avg_price`, `orig_price` (*"…can be different from the matched price. This value will be null if there were no executions."*) — SPEC-LIVE `.paths["/v3/orders/"].post.responses["200"]`.
- In-play pending confirmation: `quantity_filled_pending` — *"The quantity in GBP of the order that was matched and pending confirmation. Bets will be subject to an eight second 'Pending' confirmation delay after being matched… If subsequent messages confirm that a material event has occurred, we void those bets matched in the preceding eight seconds. This is to protect users from courtsiding and faster feeds."* — SPEC-LIVE `.paths["/v3/orders/"].get.responses["200"]...quantity_filled_pending.description`. **Any position/P&L calculation that ignores `quantity_filled_pending` will overstate confirmed fills.**
- Matching is not price-guaranteed for resting orders (see Q6.1 `average_price_matched`) and IOC semantics are all-or-minimum: SPEC-LIVE `minimum_accepted_quantity` description.

### Q6.6 `client_reference_idempotency`
- **No client-generated reference field exists on `POST /v3/orders/`.** The complete request schema is: `contract_id` (req), `market_id` (req), `price` (req), `quantity` (req), `side` (req), `label`, `minimum_accepted_quantity`, `type` — SPEC-LIVE `.paths["/v3/orders/"].post.requestBody...schema.properties` / `.required`. The only client-supplied free-text string is `label`: *"Label is a user-defined string that will be stored in the order. It can be used to identify different trading strategies"* — no uniqueness or dedup guarantee stated.
- A retry/idempotency field **does exist elsewhere in the spec**: `reference_id` and `buy_reference_id`, both described *"To handle retries over flaky network. Same value sent twice will result in `DUPLICATE_TRADE` error instead of 2 duplicate bets"* — SPEC-LIVE `.paths["/v3/orders/fullcover/"].get.responses["200"]...properties.orders.items.properties.reference_id` (and `buy_reference_id`). These appear **only** on the fullcover (multiples) response schema, and `DUPLICATE_TRADE` does not appear anywhere in the single-order route's error enums. So the documented retry-safety mechanism is not exposed on the public single-contract order route → GAP.
- Server-side identity: `order_id` (returned on placement), `original_order_id` (present on order reads), and `sequence_number` (*"This refers to the sequence number in the account activity - statement endpoint"*) — SPEC-LIVE order schemas.
- Therefore: **client-side dedupe is mandatory.** The safe pattern is submit → on ambiguity, reconcile via `GET /v3/orders/` (filters: `id`, `market_id`, `contract_id`, `state`, `created_datetime_min/max`, `limit`) and use `label` as your own correlation tag, since it is the only field that survives round-trip.
- Internal contradiction to flag: `troubleshooting/common_api_issues.md` line 162 claims an already-cancelled `DELETE /v3/orders/{order_id}/` *"is idempotent - it succeeds regardless"*, while SPEC-LIVE documents a 404 path on that route (`ORDER_CANCEL_REJECTED_NOT_FOUND`) — do not assert idempotent cancel in a client design without confirming.

### Q6.7 `timeout_recovery`
- **Partially documented; the exact post-timeout procedure for placement is STATE_NOT_DOCUMENTED.** What is documented:
  - Failure codes on `POST /v3/orders/`: 503 `CREATE_ORDER_TIMEOUT`, `ORDER_UNAVAILABLE` (plus `KYC_SERVICE_UNAVAILABLE`, `KYC_SERVICE_INTERNAL_ERROR`, `AUTH_UNAVAILABLE`) — SPEC-LIVE `.paths["/v3/orders/"].post.responses["503"]`; 400 `ORDER_REJECTED_SERVICE_TEMPORARILY_UNAVAILABLE` — `.responses["400"]`.
  - The spec's own stated status-check pattern: *"For all other order types, the route will return when the order is accepted by the exchange. In the latter case, GET v3/orders should be used to check the status of the order, using the order id returned by this response."* — SPEC-LIVE `.paths["/v3/orders/"].post.description` (verbatim; note it says "GET v3/orders", not "/v3/orders/").
  - Read-side timeouts: `GET /v3/orders/` documents `504 ZEUS_TIMEOUT` and `503 ZEUS_UNAVAILABLE, PROMOTION_SERVICE_UNAVAILABLE, ZEUS_CONNECTION_ERROR` — SPEC-LIVE `.paths["/v3/orders/"].get.responses`; `ZEUS_TIMEOUT`/`RECKONATOR_UNAVAILABLE` also appear as the generic GatewayTimeout schema in DOCS-ENDPOINTS lines 325-327.
  - Login timeout: `503 AUTH_UNAVAILABLE, TIMEOUT` — SPEC-LIVE `.paths["/v3/sessions/"].post.responses["503"]`.
- **Not documented:** what to do when the POST times out **before** returning `order_id` (the spec's reconciliation instruction depends on an id that a `CREATE_ORDER_TIMEOUT` response does not contain), and there is no stated idempotency window or safe-retry rule. → GAP. The defensible client pattern (derived, not spec text): on any ambiguous placement outcome, query `GET /v3/orders/?created_datetime_min=…&market_id=…&state=created,partial,filled` and reconcile by `label`/`contract_id`/`quantity` before resubmitting; never blind-retry.

### Q6.8 `void_repricing_commission_settlement_reporting`

**Void / reduction-factor (reprice) reporting in the API:**
- Order-level outcome enum, verbatim: `winner` (*"…the winner or one of the winners of the market"*), `loser`, `deadheat` (*"There was a tie between this contract and another one. This is quite a rare outcome."*), `reduce` (*"This contract was withdrawn from the market and a reduction factor was applied."*), `void` (*"This contract is no longer allowed to be traded on."*) — SPEC-LIVE `.paths["/v3/orders/"].get.responses["200"]...properties.outcome.description`. This is the per-order signal that a reprice/void happened.
- Contract-level equivalents are on `GET /v3/markets/{market_ids}/contracts/`: `state_or_outcome` enum = `new, open, live, halted, winner, loser, deadheat, reduced` (*"withdrawn and a reduction factor was applied"*), `voided` (*"no longer available for betting"*), `unavailable`; `outcome_timestamp` = *"If the contract has settled, this will have the settlement datetime, null otherwise"*; and a `reduction_factor` field (example `"0.45451"`, numeric-string pattern, **no description text in the spec**) — SPEC-LIVE `.paths["/v3/markets/{market_ids}/contracts/"].get.responses["200"]...properties.state_or_outcome|outcome_timestamp|reduction_factor`. `reduction_factor` occurs exactly once in the whole spec and only on this route — it is **not** present on order or activity schemas.
- Account-activity `source` enum carries the settlement/reprice event vocabulary, including: `contract.settle`, `contract.unsettle`, `contract.void`, `contract.unvoid`, `contract.reduce`, `contract.unreduce`, `contract.resettle`, `execution.settle`, `execution.unsettle`, `execution.void`, `execution.unvoid`, `execution.reduce`, `market.settle`, `market.unsettle`, `market.void`, `market.unvoid`, `market.resettle`, `market.partial_unsettle`, `order.settle`, `order.unsettle`, `order.void`, `order.unvoid`, `order.execute.void`, `order.reduce`, `order.book.reduce_qty`, plus `commission.update` and `cash_out.*` — SPEC-LIVE `.paths["/v3/accounts/activity/"].get...parameters[source].schema.items.enum` (same enum in the activity row `source` field). This is the authoritative list for reconciling voids/reprices in code.
- In-play void reporting: `quantity_filled_pending` (8-second pending → void of bets matched in the preceding 8 seconds on a confirmed material event) — SPEC-LIVE `.paths["/v3/orders/"].get.responses["200"]...quantity_filled_pending.description` (full text quoted in Q6.5).
- Reduction-factor arithmetic guidance: use `average_price_matched_precise` *"particularly after reduction factors are applied"* — SPEC-LIVE (Q6.1).

**Commission reporting in the API:**
- Per-transaction: `commission` — *"How much commission was charged"* — SPEC-LIVE `.paths["/v3/accounts/activity/"].get.responses["200"]...items.properties.commission.description`.
- Account-level rate: `commission_type` — *"Commission charged by Smarkets on the account"*, example `"0.02"` — SPEC-LIVE `.paths["/v3/accounts/"].get.responses["200"]...properties.commission_type.description`. (Tier *product rules* are out of scope for this brief; API-TCS §3 states API accounts get standard Customer Commission and are ineligible for affiliate/60-day 0% offers.)
- Commission appears as a distinct activity `source` (`commission.update`), so commission changes are separately reportable — SPEC-LIVE activity `source` enum.

**Settlement reporting surfaces (for a reconciliation job):**
- `GET /v3/accounts/activity/` — statement data: *"This information should be used for accounting reconciliation. This data is what is being used in our statement page"* — SPEC-LIVE `.paths["/v3/accounts/activity/"].get.description`. Filters: `timestamp_min/max`, `source`, `market_id`, `order_id`, `limit`, `sort`, `pagination_last_seq`, `pagination_last_subseq`, `event_info` — SPEC-LIVE `.paths["/v3/accounts/activity/"].get.parameters`. Note: **no `sequence_number` filter here** — `sequence_number_min/max` are filters on `GET /v3/orders/` instead (see below).
- `GET /v3/account_activity_csv/{start_datetime}/{end_datetime}/` — gzipped CSV export; the hourly constraint **is** documented in the spec: *"Start and end datetimes have to be separated by an hour, also these have to be exactly on the hour."* — SPEC-LIVE `.paths["/v3/account_activity_csv/{start_datetime}/{end_datetime}/"].get.description`.
- `GET /v3/orders/` — *"Retrieve current orders on Smarkets, these include open and recently settled orders."* — SPEC-LIVE summary; states `created|partial|filled|settled` with `outcome` per Q6.8 above. Linkage: `sequence_number` *"refers to the sequence number in the account activity - statement endpoint"* — SPEC-LIVE order schema; filters available on this route: `id`, `market_id`, `contract_id`, `state`, `side`, `sort`, `limit`, `created_datetime_min/max`, `sequence_number_min/max`, `pagination_last_id` — SPEC-LIVE `.paths["/v3/orders/"].get.parameters`.
- `GET /v3/orders/fullcover/` — *"Get all fullcover orders for an account"* — SPEC-LIVE summary; carries `reference_id`/`buy_reference_id`, `stake`, `returned_amount`, `potential_returns`, `cashed_out_quantity`, `cashed_out_amount`, `number_of_bets`, `original_contracts` (with `contract_id` per leg) — SPEC-LIVE `.paths["/v3/orders/fullcover/"].get.responses["200"]...properties.orders.items.properties`. **This is the only documented route that itemises multiple/bet-builder legs, and it is a GET only** — there is no documented POST for multiples in the public spec.
- Void → cash treatment (net settlement): voids do not move cash; internal worked reference at skill `references/exchange-netting-settlement.md` and `references/instant-match-voiding.md`. Treat the API fields above as the operative evidence and the settlement mechanics notes as internal interpretation.

---

## DOC_POINTERS

1. `https://docs.smarkets.com` — Swagger UI; loads the live spec from `https://api.smarkets.com/v0/control/openapi/?tags=trading_api` (the authoritative source; SPEC-LOCAL is a 2026-08-18 snapshot and is already stale on `GET /v3/events/`).
2. `~/smarkets-api-support/openapi/smarkets_openapi.json` — trading-tag spec snapshot (md5 `afec019e…`), same content as `~/smarkets-api-support/scrape-aug18/live_trading.json`.
3. `~/smarkets-api-support/docs/api_endpoints_reference.md` + `~/smarkets-api-support/docs/request_response_schemas.md` — flattened per-endpoint schemas/error enums derived from the snapshot; useful for error-code lists (note: `docs/request_response_schemas.md` line 163 omits `LOGIN_VERIFICATION_REQUIRED` from the login 403 list, which SPEC-LIVE includes).
4. `~/smarkets-api-support/scrape-aug18/help/api-tcs.md` — API T&Cs (preapproval of call limits, fair usage, activation/commission context).

## GAPS for api@smarkets.com

1. **Price increments in API units.** Spec only requires *"a valid tick"* and rejects otherwise with `ORDER_INVALID_INVALID_PRICE`; the tick table exists only in a help-centre article. Confirm whether that table is the authoritative tick set for API-submitted integer basis-point prices, and whether it can change without notice.
2. **Idempotency on single-order placement.** `reference_id`/`buy_reference_id` with `DUPLICATE_TRADE` semantics exist only on the fullcover response schema, not on `POST /v3/orders/`. Is a client-supplied idempotency key available (or planned) for single orders, and is `label` guaranteed unique/queryable?
3. **Post-timeout reconciliation.** `CREATE_ORDER_TIMEOUT` (503) is documented, but the spec's recovery instruction ("using the order id returned by this response") cannot apply when no order id is returned. Confirm the supported recovery procedure and whether a retry within N seconds is deduplicated.
4. **Minimum trading requirement.** No numeric minimum is published; T&Cs §6.1 only prohibit *"data extraction purposes without commensurate trading volumes"*. Confirm whether a minimum monthly trading volume/stake applies to API accounts and what it is.
5. **IP restrictions.** No allowlist feature is documented, yet `IP_NOT_TRUSTED`/`SOURCE_BLOCKED`/`CLIENT_JURISDICTION_MISMATCH` fire at login. Confirm whether static-IP allowlisting is available for a personal integration and which jurisdictions/IP ranges are acceptable.
6. **Sandbox.** Confirm there is genuinely no test/sandbox environment and no read-only paper-trading mode, so live funds are required for order testing (approved precedent wording says exactly this).
7. **Rate-limit tiering for this account.** Spec quotes 50/60s for API users on quotes and "lower" for non-API users; an unauthenticated call today returned `x-ratelimit-limit: 20`. Confirm the approved caps that will apply to this account once approved, and whether per-endpoint caps are adjustable.
8. **Streaming.** Confirm no websocket/streaming feed is offered to API customers (and that the website `sio-live` channel is not available to them), so a polling architecture is the only option.
9. **Multiples via API.** `GET /v3/orders/fullcover/` exists, but no placement/edit route for multiples appears in the public spec. Confirm whether multiples/bet-builder orders can be placed via the API at all.
10. **Void/reprice visibility per leg + reduction-factor semantics.** `reduction_factor` exists only on `GET /v3/markets/{market_ids}/contracts/` with no description (example `"0.45451"`), and is absent from order/activity schemas. Confirm (a) whether it is the multiplier to apply to matched prices/quantities, (b) whether void/reduction-factor events on a multiple are itemisable per leg through `GET /v3/orders/fullcover/` + `GET /v3/accounts/activity/` (`contract.reduce`/`contract.void` sources), and (c) how commission is netted when a bet is voided or repriced.
11. **Token renewal for long-running services.** TTL is a 30-minute sliding window; confirm whether `use_auth_v2` + `refresh_token` (or `remember: true`) is the recommended pattern for an unattended Python client, and whether session caps (`SESSION_LIMIT_REACHED`) apply per account.
12. **Cancel idempotency contradiction.** Internal troubleshooting doc says an already-cancelled `DELETE /v3/orders/{order_id}/` "succeeds regardless"; SPEC-LIVE documents a 404 path. Confirm the actual behaviour before relying on it.

## Unverified / flag before use
- Lay liability in API units (`quantity × (10000 − price) / 1e8`) — derived from the help-centre lay formula plus spec conversions; not stated in the API spec.
- Minimum quantity of 500 units (= £0.05 pot) — internal rag-context interpretation; the schema floor is `minimum: 0` and only the £0.05 minimum *stake* is documented.
- Datacenter-IP allowlisting via api@smarkets.com and jurisdiction list — internal ops note (HERMES-REF), not public documentation.
- `sio-live.smarkets.com` characterisation — internal JS-bundle discovery, not official documentation; do not cite as official.
- `reduction_factor` semantics (multiplier vs divisor, applied to price or quantity) — field exists in the spec with an example value but **no description**; do not interpret it in client code until confirmed.
