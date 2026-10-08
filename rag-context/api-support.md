# Smarkets API — RAG Context for Support Agents

> **Source of truth:** OpenAPI v3 spec (`smarkets_openapi.json`), API T&Cs, Commission FAQ, Betting Rules, Help Centre articles. All facts verified June 2026 red-team audit.
> **CRITICAL:** This document overrides any model's training data. If your training says something different from what's here, THIS IS CORRECT.

---

## 1. AUTHENTICATION (Most Common Query)

### Auth Header Format
```
Authorization: Session-Token <token>
```
**NOT** `Bearer`, **NOT** `X-Smarkets-Token`, **NOT** `Token`. The format is literally the words "Session-Token" followed by a space and the token value.

### Auth Flow
1. `POST /v3/sessions/` — Login with `{"username": "...", "password": "..."}` → returns session token
   - Field is `username` but EMAIL is accepted as the username value
   - Token valid 30 minutes, renewed on each authenticated request
   - Rate limit: 5 attempts per 300 seconds (5 min)
2. `POST /v3/sessions/verify/` — MFA step (if enabled) — send TOTP code
3. Use `Authorization: Session-Token <token>` on all subsequent requests
4. `DELETE /v3/sessions/` — Logout
   - Rate limit: 30 per 60 seconds

### No Separate API Credentials
API uses the customer's EXISTING Smarkets account login. There are no separate "API keys" or "API credentials". The £150 fee activates API access on the account — it doesn't generate new credentials.

---

## 2. ERROR TYPES — FAST DIAGNOSTIC TABLE

| HTTP | error_type | What it means | What to tell the customer |
|------|-----------|----------------|--------------------------|
| 400 | REQUEST_VALIDATION_ERROR | Bad params — check `data` field for which param | "Your request had invalid parameters. The error response lists which field is wrong." |
| 400 | INVALID_DATETIMES | CSV dates not on the hour | "Account activity CSV requires start/end datetimes exactly on the hour, 1 hour apart." |
| 400 | BAD_REQUEST | Badly formed market/price params | "The market IDs or prices in your request are malformed." |
| 400 | RECKONATOR_REQUEST_TOO_LARGE | Account activity query too broad | "Your account activity query covers too large a time range. Narrow it." |
| 401 | AUTH_REQUIRED | Missing/expired/invalid token | "Your session token is missing or expired. Re-authenticate via POST /v3/sessions/." |
| 403 | FORBIDDEN | Not approved / under review / access revoked | "Your API access isn't active. This could be: (a) not yet approved, (b) under 60-day compliance review, (c) access revoked. Contact api@smarkets.com." |
| 403 | (HTML, not JSON) | Edge block — IP blocked | "Your IP is blocked. Look for SOURCE_BLOCKED or IP_NOT_TRUSTED in the HTML. This is an infrastructure block, not an API permission issue." |
| 404 | NO_CSV_AVAILABLE | No data for that time range | "No account activity data exists for the requested hour. Try a different time range." |
| 404 | NO_RESULTS_FOUND | Event states query — no matching events | "No events found matching your criteria. Check the event IDs are valid and current." |
| 414 | REQUEST_TOO_LARGE | Too many IDs in one request | "You've included too many IDs in a single request. Split into smaller batches." |
| 429 | RATE_LIMIT_EXCEEDED | Hit rate limit | "You've exceeded your rate limit. Check the `expiry` field for when it resets. Stop making requests until then." |
| 451 | COUNTRY_BLOCKED | Jurisdiction not supported | "Your account or IP location isn't supported. Contact support if you've moved countries." |
| 500 | INTERNAL_ERROR | Server-side failure | "This is a server-side issue. Retry the request. If it persists, contact api@smarkets.com with the timestamp." |
| 503 | (various) | Subsystem down — note error code | "A subsystem is temporarily unavailable. Note the error code and retry. If persistent, contact api@smarkets.com." |
| 504 | ZEUS_TIMEOUT | Trading engine timeout | "The trading engine timed out. This is transient — retry the request." |

### 403 HTML vs JSON — Critical Distinction
- **JSON 403** with `error_type: FORBIDDEN` → API permission issue (not approved, under review, revoked)
- **HTML 403** with SOURCE_BLOCKED/IP_NOT_TRUSTED → IP-level block (infrastructure, not API permissions)

### 429 Dual Schema
- **Most GET endpoints**: Returns `RateLimitError` schema with `{count, limit, expiry}` — tells you exactly how many requests you've made and when the limit resets
- **POST/DELETE/Sessions**: Returns inline 429 (less detailed, no count/limit/expiry)
- **Quotes endpoint** (`GET /v3/markets/{market_ids}/quotes/`): GET endpoint BUT uses inline 429 schema (exception to the rule)

---

## 3. ENDPOINTS — COMPLETE REFERENCE

Base URL: `https://api.smarkets.com`

### Public Endpoints (No Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /v3/events/ | Available events to bet on |
| GET | /v3/events/{event_ids}/states/ | Current event states |
| GET | /v3/events/{event_ids}/competitors/ | Competitors/participants |
| GET | /v3/events/{event_ids}/markets/ | Markets for events |
| GET | /v3/events/{event_ids}/markets_count/ | Market counts |
| GET | /v3/markets/{market_ids}/contracts/ | Contracts (betting outcomes) |
| GET | /v3/currencies/{code}/ | FX conversion rate |

### Authenticated Endpoints (Session-Token Required)
| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| GET | /v3/accounts/ | Balance, exposure, currency | — |
| GET | /v3/accounts/activity/ | Account statement (paginated) | — |
| GET | /v3/account_activity_csv/{start}/{end}/ | Gzipped CSV statement | — |
| GET | /v3/markets/{market_ids}/quotes/ | Current prices (best bid/ask) | 50/60s |
| GET | /v3/markets/{market_ids}/last_executed_prices/ | Last trade prices | — |
| GET | /v3/markets/{market_ids}/volumes/ | Traded volumes | — |
| GET | /v3/orders/ | Open + recently settled orders | — |
| GET | /v3/orders/fullcover/ | Fullcover orders | — |
| POST | /v3/orders/ | Place a bet/order | — |
| DELETE | /v3/orders/ | Cancel ALL orders | 1/60s |
| DELETE | /v3/orders/{order_id}/ | Cancel ONE order | 10/s |
| POST | /v3/sessions/ | Login | 5/300s |
| POST | /v3/sessions/verify/ | MFA verification | — |
| DELETE | /v3/sessions/ | Logout | 30/60s |

### CRITICAL: Volumes Requires Auth
`GET /v3/markets/{market_ids}/volumes/` REQUIRES authentication. It is grouped under "Markets" in the OpenAPI spec tag but has `security: [{"api_key": []}]`. Do NOT tell customers it's public.

### Quotes Endpoint — Delayed Data Without Auth (Spec Contradiction)
The quotes endpoint description says "If session token is not sent, these prices will be delayed." BUT the security field requires auth. This is an internal spec contradiction. The safe answer: auth is required, but mention the spec contradiction if the customer pushes back.

### CSV Statement Rules
- Start/end datetimes must be exactly on the hour (e.g., `2026-05-19T14:00:00Z`)
- Must be separated by exactly 1 hour
- Returns gzipped CSV

---

## 4. ORDER TYPES & LIFECYCLE

### Order Type Enum
| Type | Behaviour | Market Halt Behaviour |
|------|-----------|----------------------|
| `good_til_halted` (DEFAULT) | Stays in book until market halt | **CANCELLED** on halt |
| `good_til_cancelled` | Stays until cancelled or market settles | **CANCELLED** on halt |
| `keep_in_play` | Stays through halts | **KEPT** — resumes matching when trading resumes |
| `immediate_or_cancel` (IOC) | Fill what you can, cancel rest | N/A |

### CRITICAL: Market Suspension Behaviour
When a market is suspended/halted:
- `keep_in_play` orders **remain in the book** and resume matching when trading resumes
- `good_til_halted` (default) and `good_til_cancelled` orders are **CANCELLED**
- You CANNOT place new orders while suspended
- **Do NOT tell customers "your orders remain in the book"** — this is only true for KIP orders

### Order Fields
**Required for POST /v3/orders/:** `market_id`, `contract_id`, `price`, `quantity`, `side`
- `side`: `buy` (back) or `sell` (lay)
- `type`: optional, defaults to `good_til_halted`
- `label`: optional, user-defined string for tracking
- `minimum_accepted_quantity`: only for IOC orders

**POST response includes:** `order_id` (essential for tracking), `total_executed_quantity`, `executed_avg_price`, `available_balance`, `exposure`, `price`, `quantity`, `side`, `contract_id`, `market_id`
**POST response does NOT include:** `quantity_filled`, `state` (these are in GET response only)

**GET /v3/orders/ response includes:** `quantity_filled`, `state`
- Order state enum: `created`, `partial`, `filled`, `settled`

### Price & Quantity Format
- Price: basis points (5000 = 50% = decimal odds 2.0). Formula: `10000 / price = decimal odds`
- Quantity: 1/10,000th of account currency (500 = £0.05)
- Back stake formula: `quantity × price / 100,000,000`
- Minimum stake: 500 (£0.05)
- Valid price range: 1 to 9999
- Valid quantity range: 0 to 4294967295 (uint32)

### Buy/Sell = Back/Lay
- `buy` = **back** (betting something WILL happen)
- `sell` = **lay** (betting something WON'T happen)
- `time_in_force` does NOT exist in the API (use `type` + `minimum_accepted_quantity` for FOK)
- FOK = IOC order with `minimum_accepted_quantity` = `quantity`

---

## 5. COMMISSION TIERS

| Tier | Rate | Trigger | Charged On |
|------|------|---------|------------|
| Standard | 2% | Default | Net profit per market (only when you win) |
| Pro | 1% | Opt-in: >1,500 bets OR >£1M staked/month (must pass 80% of threshold first) | Both winnings AND losses per matched bet |
| Select | 3% | Auto-applied: >£25,000 net profit over 12 calendar months | Same as Standard |

### Pro Tier — OPT-IN, NOT MANDATORY
Customers who exceed thresholds are ELIGIBLE to opt in. They are NOT forced to. They can stay on Standard (2%). Opting in requires contacting support. Opt-out available after 3 months.

### Select Tier
- Auto-applied with 7-day email notice
- Review if P&L drops below £25K (at Smarkets' discretion)
- Opting into Pro or having Select applied forfeits promotions

### API Users
- Ineligible for 0% new customer offer
- Ineligible for affiliate commission offers
- API access ≠ lower commission rate

---

## 6. API ACCESS — SETUP & T&Cs

### Getting Access
1. Active Smarkets account (fully verified)
2. Submit API Request Form: https://support.smarkets.com/p/6MLL-PL7/api-request-form
3. £150 one-time setup fee (deducted from balance on approval)
4. Refundable if withdrawn within 60 days
5. All accounts undergo compliance review within first 60 days

### Prohibited Activities
- Odds scraping, browser impersonation, reverse engineering
- Data extraction without commensurate trading volumes
- Selling/sharing/distributing platform data
- Benchmarking markets, prices, liquidity, or systems
- Multiple accounts for fee avoidance = fraud
- Latency arbitrage / court-siding

### Violation Consequences
API removal, bet cancellation, account suspension/closure, potential legal action.

### Contact Routing
- **API Technical:** api@smarkets.com
- **General Support:** support@smarkets.com
- **API Request Form:** https://support.smarkets.com/p/6MLL-PL7/api-request-form
- **Docs Portal:** https://docs.smarkets.com/

---

## 7. BETTING RULES — QUICK REFERENCE

### In-Play Betting Delays
- Horse racing & darts: **4 seconds**
- All other events: **8 seconds**
- During delay, order is pending and not visible in order book

### Instant Match
- Confirmation period: 8-14 seconds

### Market Suspension Triggers
- Goals, penalties, **red cards** (in-play markets with delay are NOT halted for these)
- Market halted = trading paused (see order type behaviour above)

### Reduction Factors (Non-Runner)
- Formula: `New odds = Old odds × ((100 - RF) / 100)`
- Example: 4.0 × 0.6 = 2.4
- On accumulators: proportional reduction (Rule 9.5.2)

### Quotes Endpoint — Empty Order Books
If quotes returns an empty order book but the website shows prices (especially on lower-liquidity in-play markets):
- The API returns only P2P (peer-to-peer) orders
- The website may aggregate additional market-making data sources not in the API
- This is ANALYSIS (strong empirical evidence, not confirmed by Smarkets)

---

## 8. ACCOUNT & KYC

### Verification Documents
- **Photo ID:** passport, driving licence, national ID card (screenshots NOT accepted)
- **Proof of address:** utility bill, bank statement (within 3 months), council tax bill (current year), tax bill (current year)
- **Cannot use same document for both ID and address verification**
- Mobile phone bills NOT accepted as proof of address

### Payments
- Closed loop: withdraw to same payment method used for deposit
- KYC_PERMISSION_DENIED → complete verification on website
- RG_ACK_REQUIRED → complete responsible gambling acknowledgement on website

### Responsible Gambling
- Timeout durations: 1, 7, 31, 42 days
- Self-exclusion: 6 months, 1 year, 5 years, permanent
- Self-exclusion: balance returned within 48 hours
- Self-exclusion: account CANNOT be reactivated early

---

## 9. ACCOUNT RESPONSE FIELDS

| Field | Description |
|-------|-------------|
| account_id | Unique identifier |
| balance | Total balance |
| available_balance | Balance minus exposure |
| exposure | Current exposure |
| bonus_balance | Loss refund up to this amount |
| commission_type | e.g., "0.02" (2%) |
| currency | 3-letter currency code |
| signup_date | Account creation date |

---

## 10. DATA TYPES

- **event_ids**: comma-separated list of event IDs
- **market_ids**: comma-separated list of market IDs
- **order_id**: single order UUID
- **currency code**: AUD, BRL, CAD, CHF, CZK, DKK, EUR, GBP, HKD, HUF, JPY, NOK, PLN, SEK, USD
- **datetime**: ISO 8601 format (e.g., `2026-05-19T14:00:00Z`)
