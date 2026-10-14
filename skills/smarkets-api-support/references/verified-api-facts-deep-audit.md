# Verified Smarkets API Facts — Deep Audit (June 2026)

Every claim below was verified against primary sources during a deep red-team audit.
Sources: OpenAPI spec (`openapi/smarkets_openapi.json`), live help centre articles (via Jina reader),
API T&Cs, Commission FAQ, Betting Rules, docs.smarkets.com.

Use this file when writing or auditing customer-facing documentation.
If a claim is NOT in this file, verify it against the spec before publishing.

---

## Authentication & Sessions

| Claim | Source |
|-------|--------|
| Login endpoint: `POST /v3/sessions/` | OpenAPI spec |
| Required fields: `username` (JSON field name — value is the customer's EMAIL ADDRESS) + `password` | OpenAPI spec schema `session_create` |
| ⚠️ Customer-facing language: always say "email", never "username" — Smarkets customers do not have a separate username | User correction June 2026 |
| Response returns session token | OpenAPI spec description |
| Header format: `Authorization: Session-Token <token>` | OpenAPI spec securitySchemes + description |
| Token valid 30 minutes, renewed on each authenticated request | OpenAPI spec: POST /v3/sessions/ description + `stop` field |
| MFA verify: `POST /v3/sessions/verify/` with `code` (TOTP) + `token` | OpenAPI spec schema `totp_login` |
| Login rate limit: 5 requests per 300 seconds | OpenAPI spec description |
| Logout rate limit: 30 requests per 60 seconds | OpenAPI spec description |
| No sandbox/test/paper environment in spec | OpenAPI spec — zero mentions |
| `use_auth_v2` optional field exists for refresh_token/access_token flow | OpenAPI spec |
| Login success response: **201** (not 200) — "Token response for old and new auth v2" | OpenAPI spec responses |
| MFA verify success response: **201** — same description as login | OpenAPI spec responses |
| Logout success response: **200** — "Delete session success response" | OpenAPI spec responses |
| API base URL: `https://api.smarkets.com` (Production) — from spec `servers` field | OpenAPI spec servers |

## Orders

| Claim | Source |
|-------|--------|
| Place order: `POST /v3/orders/` | OpenAPI spec |
| Required fields: `market_id`, `contract_id`, `price`, `quantity`, `side` | OpenAPI spec schema `order_create` |
| `type` is OPTIONAL, default: `good_til_halted` | OpenAPI spec — `type` has `default: "good_til_halted"` |
| `side` enum: `["buy", "sell"]` | OpenAPI spec |
| `buy` = back, `sell` = lay | OpenAPI spec side description |
| `label` field: optional, user-defined string for strategy tagging | OpenAPI spec — documented in POST body + GET response + account activity |
| `minimum_accepted_quantity`: optional, IOC only | OpenAPI spec — "Only applicable to immediate_or_cancel order types" |
| `time_in_force` does NOT exist | OpenAPI spec — zero matches |
| Order type enum (POST): `good_til_cancelled`, `keep_in_play`, `good_til_halted`, `immediate_or_cancel` | OpenAPI spec |
| Order type enum (GET response): adds `over_the_counter`, `over_the_counter_free` | OpenAPI spec |
| Order state enum: `created`, `partial`, `filled`, `settled` | OpenAPI spec GET /v3/orders/ response |
| POST response includes `total_executed_quantity` (required field) | OpenAPI spec POST 200 response schema |
| POST response does NOT include `quantity_filled` or `state` | OpenAPI spec — not in POST 200 schema |
| GET response DOES include `quantity_filled` and `state` | OpenAPI spec GET 200 response schema |
| Quantity unit: 1/10000 of account currency (POST body description) | OpenAPI spec |
| Quantity unit alt: 1/100 of a UK penny (GET orders + account activity description — same result) | OpenAPI spec |
| Minimum stake: 500 = £0.05 | OpenAPI spec quantity example |
| Back stake formula: quantity × price / 100,000,000 | OpenAPI spec quantity description |
| Price format: percentage basis points (5000 = 50% = decimal odds 2.0) | OpenAPI spec price description |
| Price constraints: min 1, max 9999 (request body) | OpenAPI spec |
| Cancel specific order: `DELETE /v3/orders/{order_id}/` | OpenAPI spec |
| Cancel all orders: `DELETE /v3/orders/` | OpenAPI spec |
| Cancel-one rate limit: 10 requests per second | OpenAPI spec description |
| Cancel-all rate limit: 1 request per 60 seconds | OpenAPI spec description |
| Fullcover endpoint: `GET /v3/orders/fullcover/` (GET only, no POST) | OpenAPI spec |

## Order Type Lifetime Table (from spec)

| Type | Market goes live | Market halted | Reduction factor |
|------|-----------------|---------------|-----------------|
| `good_til_cancelled` | Cancelled | Cancelled | Cancelled |
| `good_til_halted` (default) | Kept | Cancelled | Cancelled |
| `keep_in_play` | Kept | Kept | Cancelled |
| `immediate_or_cancel` | N/A — executes at placement | N/A | N/A |

## Rate Limits (all from OpenAPI spec descriptions)

| Endpoint | Limit |
|----------|-------|
| Quotes `GET /v3/markets/{ids}/quotes/` | 50 per 60 seconds |
| Login `POST /v3/sessions/` | 5 per 300 seconds |
| Cancel all `DELETE /v3/orders/` | 1 per 60 seconds |
| Cancel one `DELETE /v3/orders/{id}/` | 10 per second |
| Logout `DELETE /v3/sessions/` | 30 per 60 seconds |
| POST /v3/orders/ | "per account basis" — no specific number |

## 429 Response — Two Schemas (IMPORTANT)

The spec has TWO different 429 response schemas:

- **Schema A (RateLimitError)** — used by most GET endpoints: includes structured `count`, `limit`, `expiry` fields
- **Schema B (inline)** — used by POST /v3/orders/, POST /v3/sessions/, DELETE endpoints, GET quotes: has only a generic `data` field (string or object) with NO structured sub-fields

Do NOT claim all 429 responses include count/limit/expiry.

## Error Codes (all verified in OpenAPI spec)

### Order placement 400 errors
ORDER_REJECTED_MARKET_SETTLED, ORDER_REJECTED_MARKET_NOT_FOUND, ORDER_REJECTED_LIMIT_EXCEEDED,
ORDER_INVALID_INVALID_PRICE, ORDER_INVALID_INVALID_QUANTITY, ORDER_REJECTED_INSUFFICIENT_FUNDS,
REQUEST_VALIDATION_ERROR, ORDER_REJECTED_CONTRACT_SETTLED, ORDER_CANCELLED_TRADING_SUSPENDED,
ORDER_REJECTED_MARKET_HALTED, ORDER_REJECTED_THROTTLE_EXCEEDED, ORDER_REJECTED_CROSSED_SELF,
ORDER_CANCELLED_MARKET_HALTED, ORDER_REJECTED_STAKE_LIMIT_EXCEEDED, ORDER_REJECTED_CAPACITY_REACHED,
ORDER_REJECTED_CONTRACT_NOT_FOUND, ORDER_CANCELLED_INSUFFICIENT_LIQUIDITY,
ORDER_CANCELLED_MEMBER_REQUESTED, ORDER_REJECTED_MARKET_NOT_OPEN, ORDER_REJECTED_TRADING_SUSPENDED,
ORDER_REJECTED_ACCOUNT_SUSPENDED, ORDER_REJECTED_SERVICE_TEMPORARILY_UNAVAILABLE,
ORDER_CANCELLED_ADMIN_REQUESTED

### Order placement 403 errors
KYC_PERMISSION_DENIED, NO_DEPOSITS, ACCOUNT_UNVERIFIED, ACTION_BLOCKED, FORBIDDEN, RG_ACK_REQUIRED

### Session 403 errors
DEVICE_NOT_TRUSTED, USER_SELF_SUSPENDED, IP_NOT_TRUSTED, SOURCE_BLOCKED, USER_SUSPENDED,
USER_EXCLUDED, SESSION_LIMIT_REACHED, USER_ON_TIMEOUT

### Other notable codes
- 451: COUNTRY_BLOCKED
- 414: REQUEST_TOO_LARGE
- 504/503: ZEUS_TIMEOUT, ZEUS_UNAVAILABLE, ZEUS_CONNECTION_ERROR
- 503: EVENTS_UNAVAILABLE, EVENTS_API_RATE_LIMIT, MDS_SERVICE_UNAVAILABLE, CREATE_ORDER_TIMEOUT,
  KYC_SERVICE_UNAVAILABLE, AUTH_UNAVAILABLE, FOREX_SERVICE_UNAVAILABLE

## T&Cs Verified Claims

| Claim | Source |
|-------|--------|
| £150 one-time setup fee, deducted from balance on approval | T&Cs Section 3 |
| Refundable within first 60 days if permanently withdrawing | T&Cs Section 3 |
| API users ineligible for 60-day 0% commission offer | T&Cs Section 3 |
| API users ineligible for affiliate commission offers | T&Cs Section 3 |
| All other uses prohibited: odds scraping, concealing API calls, browser impersonation, reverse engineering | T&Cs Section 2 (exact quote) |
| May not share, sell, or distribute platform data without written approval | T&Cs Section 5 |
| API must not be used to benchmark markets, prices, liquidity, or systems | T&Cs Section 5 |
| Usage restricted to pre-approved events and markets only | T&Cs Section 5 |
| May be subject to additional fees or restrictions | T&Cs Section 5 |
| Exceeding rate limits → temporary suspension; repeated violations → permanent revocation | T&Cs Section 5 |
| Compliance review within first 60 days | T&Cs Section 2 |
| Data extraction without commensurate trading volumes prohibited | T&Cs Section 6.1 |
| Multiple accounts to avoid commission thresholds = fraud | T&Cs Section 7 |
| Latency arbitrage / court-siding prohibited | T&Cs Section 7 |
| Smarkets retains full discretion to refuse API access | T&Cs Section 1 |
| Contact for API questions: support@smarkets.com (Customer Operations Team) | T&Cs Section 8 |
| Technical contact: api@smarkets.com | OpenAPI spec info.contact |

## Commission Tiers (all from Commission FAQ)

| Claim | Source |
|-------|--------|
| Standard: 2% on net profit per market, only when you win | Commission FAQ |
| Pro: 1% per matched bet, on winnings if win / on losses if lose | Commission FAQ |
| Select: 3% per matched bet, same as Pro | Commission FAQ |
| Pro trigger: >1,500 bets OR >£1M staked in a calendar month | Commission FAQ |
| Pro opt-in requires 80% of either threshold | Commission FAQ |
| Pro opt-out after 3 months | Commission FAQ |
| Select trigger: >£25,000 net profit over previous 12 calendar months | Commission FAQ |
| Select notice: 7 days by email | Commission FAQ |
| Select review: can apply if P&L drops below £25K, at Smarkets' discretion | Commission FAQ |
| Opting into Pro or having Select applied permanently forfeits commission promotions | Commission FAQ |
| Select Tier: Pro thresholds (1500 bets / £1M) do NOT apply | Commission FAQ |
| New rate applies to ALL trading activity after switching, not just new bets | Commission FAQ |

## Betting Rules (from Help Centre)

| Claim | Source |
|-------|--------|
| Reduction factor = equivalent of Rule 4 deductions | Horse Racing Rules 13.3.1 |
| RF assigned per horse's estimated % chance of winning | Horse Racing Rules 13.3.2 |
| Non-runner: all bets on that horse voided | Horse Racing Rules 13.3.3 |
| Win market: RF < 2.5% → bets stand unaltered; RF ≥ 2.5% → matched bets adjusted, unmatched cancelled | Horse Racing Rules 13.3.5 |
| Place market: RF applied to all winnings regardless of size, unmatched cancelled | Horse Racing Rules 13.3.6 |
| RF may be applied after a race if horse was non-runner | Horse Racing Rules 13.3.8 |
| RF not applied to ante-post markets | Horse Racing Rules 13.4.2 |
| In-play betting delay: 4 seconds (horse racing & darts), 8 seconds (all other events) | General Rules 8.2.1 |
| In-play markets with betting delay are NOT halted for material events (goals, penalties, red cards) | General Rules 8.2.2 |
| Instant Match confirmation period: 8-14 seconds | General Rules 8.3 |
| Settlement based on official result from governing body on day of event | General Rules 4.2 |
| Smarkets reserves right to void or resettle if new information emerges | General Rules 4.5 |

## KYC & Account Verification (from Help Centre)

| Claim | Source |
|-------|--------|
| Verification required after first deposit | Help Centre: How to verify |
| Account must be verified to issue withdrawals | Help Centre: How to verify |
| Most UK users verified electronically within minutes | Help Centre: Verification process time |
| Document review up to 24 hours | Help Centre: Verification process time |
| If not age-verified within 72 hours of first deposit, account suspended | Help Centre: How to verify |
| Accepted photo ID: passport, driving licence (with photo), national ID card | Help Centre: Documents required |
| Accepted proof of address: bank statement, utility bill (within 3 months), council tax bill (current year), tax bill (current year) | Help Centre: Documents required |
| Screenshots of online documents NOT accepted | Help Centre: Documents required |
| Mobile phone bills NOT accepted as proof of address | Help Centre: Documents required |
| Cannot use same document for ID and address verification | Help Centre: Documents required |

## Responsible Gambling (from Help Centre)

| Claim | Source |
|-------|--------|
| Timeout durations: 1, 7, 31, or 42 days | Help Centre: Take a timeout |
| Timeout: account automatically reopened at end | Help Centre: Take a timeout |
| Self-exclusion periods: 6 months, 1 year, 5 years, or permanent | Help Centre: How to self-exclude |
| Self-exclusion: balance returned within 48 hours | Help Centre: How to self-exclude |
| Self-exclusion: account cannot be reinstated during exclusion period | Help Centre: How to self-exclude |
| Deposit limits: daily, weekly, monthly; net or gross | Help Centre: Deposit limits |
| Increasing deposit limit: 72-hour cooling off period | Help Centre: Deposit limits |
| UK customers (registered after Feb 2023): £4999.99 monthly net deposit limit | Help Centre: Deposit limits |
| UK customers (registered after Mar 2023): also £1000 daily net deposit limit | Help Centre: Deposit limits |

## Payments (from Help Centre)

| Claim | Source |
|-------|--------|
| Closed loop: must withdraw to same payment source used for deposit | Help Centre: Closed Loop System |
| Some Mastercard/Maestro withdrawals limited to net deposit amount | Help Centre: Min/max withdrawals |
| UK customers cannot cancel pending withdrawals (UKGC regulation) | Help Centre: How to make a withdrawal |
| Minimum deposit: £/€10 (most methods), £/€20 (PayPal) | Help Centre: Min/max deposits |
| Minimum withdrawal: £/€10 (most), £/€20 (bank transfer) | Help Centre: Min/max withdrawals |

## Endpoints (19 unique paths, 21 operations across 11 OpenAPI tags)

### Sessions (3) — auth: these endpoints ARE the auth flow
- POST /v3/sessions/ — Login (no auth required to call)
- POST /v3/sessions/verify/ — MFA verify (no auth required to call)
- DELETE /v3/sessions/ — Logout (no auth required to call)

### Accounts (3) — auth: REQUIRED
- GET /v3/accounts/ — Account info
- GET /v3/accounts/activity/ — Account activity/statement
- GET /v3/account_activity_csv/{start}/{end}/ — Gzipped CSV

### Events (2) — auth: NOT required (public)
- GET /v3/events/ — Events list
- GET /v3/events/{ids}/states/ — Event states

### Competitors (1) — auth: NOT required (public)
- GET /v3/events/{ids}/competitors/

### Markets (3) — auth: NOT required (public)
- GET /v3/events/{ids}/markets/
- GET /v3/events/{ids}/markets_count/
- GET /v3/markets/{ids}/contracts/

### Volumes (1) — auth: REQUIRED ⚠️ (common mistake: assumed public because grouped under "Markets" tag)
- GET /v3/markets/{ids}/volumes/

### Prices (2) — auth: REQUIRED
- GET /v3/markets/{ids}/quotes/ — Current order book (spec description says "delayed without token" but security field requires auth — contradiction)
- GET /v3/markets/{ids}/last_executed_prices/

### Orders (5) — auth: REQUIRED
- POST /v3/orders/ — Place order
- GET /v3/orders/ — Retrieve orders
- DELETE /v3/orders/{id}/ — Cancel specific order
- DELETE /v3/orders/ — Cancel all orders
- GET /v3/orders/fullcover/ — Fullcover orders

### Currencies (1) — auth: NOT required (public)
- GET /v3/currencies/{code}/ — Conversion rate

## Claims NOT Verified (removed from documentation)

These claims appeared in earlier drafts but could NOT be verified against any primary source.
Do NOT re-introduce them without finding documentation support.

| Claim | Why removed |
|-------|------------|
| "WebSocket feeds exist" | Zero mention in spec |
| "Paper trading / test environment available" | Zero mention in spec |
| "IP whitelisting is available" | Zero mention in spec |
| "Withdrawal takes 1-3 / 1-5 business days" | No specific timeline in help centre |
| "Prices without a token are delayed" | Spec description SAYS "If session token is not sent, these prices will be delayed" BUT security field requires auth (`security: [{"api_key": []}]`) — internal spec contradiction. FAQ notes both sides and directs customers to contact api@smarkets.com. |
| "Website shows prices from market-making system not in API" | Not documented anywhere |
| "Order placement throttle can't be raised" | Not documented in spec or T&Cs |
| "Omitting minimum_accepted_quantity causes zero-match" | Not documented in spec |
| "Multiple environments exist" | No environments in spec |
| "RG_ACK_REQUIRED is a one-time regulatory step" | Not characterized as one-time or regulatory in docs |
| "403 HTML is specifically Cloudflare" | Cloudflare not mentioned in spec; use "edge block" |
| "All 429 responses include count/limit/expiry" | Only GET endpoints; orders/sessions use different schema |
| "Volumes endpoint is public/no-auth" | Spec: `security: [{"api_key": []}]` — auth REQUIRED. Was incorrectly grouped under "Markets" category with public endpoints. Fixed in FAQ rev 2. |
| "All open orders remain in the book during market suspension" | Contradicts order type lifetime table: GTC and GTH are CANCELLED on halt; only KIP survives. Fixed in FAQ rev 2. |
| "Pro Tier opt-in is mandatory to continue trading" | Pro Tier is optional. Customers can stay on Standard (2%). Fixed in FAQ rev 2. |
| "Select Tier applies to a small number of accounts" | "Small number" qualifier not in Commission FAQ. Removed in FAQ rev 2. |
