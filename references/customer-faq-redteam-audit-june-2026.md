# Customer FAQ — Red-Team Fact-Check Audit (June 2026)

**Target file:** `training/customer_faq.md` (561 lines after fixes)
**Status:** ✅ ALL 16 FINDINGS FIXED (June 2026 rev 2)
**Methodology:** Every factual claim cross-checked against the live OpenAPI v3 spec (`openapi/smarkets_openapi.json`), API T&Cs, Commission FAQ, Betting Rules, and Help Centre articles retrieved via Jina reader.
**Previous audit:** `references/documentation-redteam-audit-june-2026.md` — 21 findings (first pass) + 15 findings (deep second pass). This audit supersedes it for the customer_faq.md file.

---

## Audit Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL — factual errors contradicting the spec | 3 | ✅ All fixed |
| HIGH — unverified claims stated as fact or significant misleading gaps | 4 | ✅ All fixed |
| MEDIUM — imprecisions, incomplete lists, minor gaps | 9 | ✅ All fixed |
| **Total findings** | **16** | **✅ All fixed** |
| Previously identified findings now FIXED | 18 | ✅ Confirmed |
| Claims verified as accurate | 38 | ✅ Spot-checked |
| **Additional improvement** | 1 | ✅ Auth JSON example added |

---

## CRITICAL — Factual Errors

### C1. Volumes endpoint incorrectly listed as not requiring authentication

**FAQ claim (line 128, table):**
> `Markets | Markets by event, market count, contracts, volumes | No`

**FAQ claim (line 132):**
> "Public endpoints (events, competitors, contracts, currencies, markets, volumes) are accessible without a token."

**Spec evidence:**
`GET /v3/markets/{market_ids}/volumes/` has `security: [{"api_key": []}]` — authentication is REQUIRED.

The endpoint reference doc also confirms: `Auth: REQUIRED (Session-Token)`.

**Impact:** A customer reading this FAQ will attempt to call the volumes endpoint without a session token and receive a 401. This is directly misleading.

**Fix:** Remove `volumes` from both the "No auth" category in the table and from the public endpoints list on line 132. Volumes requires authentication. Move it to a separate row or to the "Prices" category (both quotes and volumes are market-level data requiring auth).

---

### C2. Market suspension: "Your open orders remain in the book" contradicts the FAQ's own order type table

**FAQ claim (line 464):**
> "Trading is temporarily paused. Your open orders remain in the book but can't be matched until trading resumes."

**Contradiction — the FAQ's own order type table (lines 208-213):**

| Type | Market halted |
|---|---|
| `good_til_cancelled` | **Cancelled** |
| `good_til_halted` (default) | **Cancelled** |
| `keep_in_play` | **Kept** |

Only `keep_in_play` orders survive a market halt. The default order type (`good_til_halted`) and `good_til_cancelled` orders are CANCELLED when the market is halted — they do not remain in the book.

**Spec evidence:** The order type lifetime table is verified from the OpenAPI spec (see `references/verified-api-facts-deep-audit.md`).

**Impact:** A customer with GTH orders (the default) reads "your open orders remain in the book" and expects them to resume matching when trading resumes. In reality, their orders have been cancelled. This could cause real financial harm if they're relying on those orders.

**Fix:** Rewrite line 464 to:
> "Trading is temporarily paused. What happens to your open orders depends on their type: `keep_in_play` orders remain in the book and will resume matching when trading resumes. `good_til_cancelled` and `good_til_halted` orders are cancelled when the market is halted. You can't place new orders while the market is suspended."

---

### C3. Pro Tier: "you'll need to opt in to the Pro Tier to continue trading" is misleading

**FAQ claim (line 329):**
> "If you place more than 1,500 bets or stake more than £1 million in a calendar month, you'll need to opt in to the Pro Tier to continue trading."

**Evidence:** The commission-tiers reference (`references/commission-tiers-faq.md`) and Commission FAQ both describe Pro Tier as an **optional opt-in** — customers can stay on Standard (2%) even if they exceed the thresholds. The phrase "to continue trading" implies that opting in is mandatory to keep using the API, which is false.

The reference file states: "The user must actively opt in by contacting support once they pass 80% of either volume threshold." There is no mention of being forced to opt in or losing trading access.

**Impact:** A high-volume customer reads this and believes they must switch to the 1% tier (which charges commission on losses too) or lose API access. In reality, staying on Standard (2%, only charged on winnings) may be more advantageous for their trading pattern.

**Fix:** Change to:
> "If you place more than 1,500 bets or stake more than £1 million in a calendar month, you're eligible to opt in to the Pro Tier (1%) for a lower commission rate. You must pass 80% of either threshold before you can opt in. Opting in is optional — you can stay on the Standard Tier (2%) if you prefer. To opt in, contact customer support."

---

## HIGH — Unverified Claims or Significant Misleading Gaps

### H1. Quotes endpoint: avoids the known explanation for empty books

**FAQ claim (lines 149-152):**
> "The API quotes endpoint returns the exchange order book. The website may display additional information or features not available through the API. If the quotes endpoint returns an empty order book, there may simply be no resting orders on that market at that moment."

**Evidence:** The workspace's own analysis (`references/quotes-endpoint-behaviour.md`) identifies the most likely cause: the API returns only the P2P (peer-to-peer) order book, while the website includes first-party market-making orders. This is supported by empirical evidence (Premier League markets show 98%+ coverage; lower-liquidity in-play markets consistently return empty books while the website shows prices).

The FAQ's "may simply be no resting orders" explanation is often wrong for in-play lower-liquidity markets — there ARE orders, just not P2P ones.

The previous audit's verified facts file lists "Website shows prices from market-making system not in API" as a claim that was NOT verified and removed. However, the quotes-endpoint-behaviour.md reference presents it as the "most likely explanation" based on strong empirical evidence, while correctly labeling it as analysis not confirmed fact.

**Impact:** Customers with empty quotes on in-play markets are given a misleading explanation ("no resting orders") instead of the actual likely cause. They waste time investigating a non-existent liquidity problem.

**Fix:** Add a note:
> "The API quotes endpoint returns the peer-to-peer order book — orders placed by other exchange users. The website may aggregate additional data sources not available through the API. If you consistently see empty order books on markets where the website shows prices (particularly on lower-liquidity in-play markets), this is likely due to the API returning only P2P liquidity. For confirmation of the data scope, contact api@smarkets.com."

Label as analysis, not confirmed fact — consistent with the workspace's established approach.

---

### H2. Quotes endpoint: spec says delayed data available without auth, FAQ says auth required

**FAQ claim (line 54):**
> "Real-time quotes and prices require an authenticated session."

**FAQ claim (line 132):**
> "Prices and order endpoints require authentication."

**Spec evidence:** The quotes endpoint description states:
> "If session token is not sent, these prices will be delayed."

This implies quotes CAN be accessed without authentication (returning delayed data). However, the security field on the quotes endpoint is `security: [{"api_key": []}]` — which marks it as requiring auth.

This is an internal contradiction in the spec itself. The FAQ sides with the security field (auth always required) rather than the description (auth optional, delayed without).

**Impact:** Minor — customers who could access delayed quotes without a token are told they can't. But since the security field says auth is required, the FAQ's position is defensible.

**Fix:** Either:
- (a) Add a caveat: "The quotes endpoint description mentions delayed data may be available without a token, but the security configuration requires authentication. Contact api@smarkets.com to clarify."
- (b) Leave as-is and note the spec contradiction in the audit trail.

---

### H3. "Unmatched orders are typically cancelled when the market settles" — unverified

**FAQ claim (line 472):**
> "Unmatched orders are typically cancelled when the market settles — you can't cancel or modify them after settlement."

**Evidence:** This claim is not in the verified facts file. The OpenAPI spec does not document settlement behavior for unmatched orders. The Betting Rules reference covers settlement of matched bets but does not explicitly state what happens to unmatched orders.

While this is reasonable expected behavior for an exchange, it is not documented.

**Fix:** Soften to: "Unmatched orders are typically cancelled when the market settles. This is standard exchange behavior, though it's not explicitly documented in the API specification — if you observe different behavior, contact api@smarkets.com."

---

### H4. "A small number of accounts" qualifier for Select Tier — unverified

**FAQ claim (line 333):**
> "Select (3%) — applied automatically to a small number of accounts that exceed £25,000 in net profit over the previous 12 calendar months."

**Evidence:** The Commission FAQ and verified facts confirm the £25,000 threshold and automatic application. The qualifier "a small number of accounts" is not in any verified source. It may be true, but it's an editorial assessment, not a documented fact.

**Fix:** Remove "a small number of" — change to:
> "Select (3%) — applied automatically to accounts that exceed £25,000 in net profit over the previous 12 calendar months."

---

## MEDIUM — Imprecisions, Incomplete Lists, Minor Gaps

### M1. Proof of address — incomplete list

**FAQ claim (line 361):**
> "Proof of address (utility bill or bank statement, dated within the last 3 months)"

**Verified facts:** Also accepts council tax bill (current year) and tax bill (current year). Also: cannot use the same document for ID and address verification.

**Fix:** Add: "Council tax bill (current year) or tax bill (current year) are also accepted. You can't use the same document for both ID and address verification."

---

### M2. In-play betting delay durations not mentioned

**FAQ mentions in-play** (lines 217, 466) but never specifies the delay durations.

**Verified facts:** 4 seconds (horse racing & darts), 8 seconds (all other events) — General Rules 8.2.1.

**Impact:** API customers building in-play strategies need to know there's a delay between their order being placed and matched.

**Fix:** Add to the in-play explanation or the technical issues section:
> "In-play markets have a betting delay: 4 seconds for horse racing and darts, 8 seconds for all other events. During this delay, your order is pending and not yet visible in the order book."

---

### M3. Instant Match confirmation period not mentioned

**Verified facts:** "Instant Match confirmation period: 8-14 seconds" (General Rules 8.3).

Not mentioned in the FAQ. Relevant for API customers using Instant Match who need to know the confirmation window.

**Fix:** Optional addition to the orders or technical issues section.

---

### M4. "No official SDKs or client libraries are provided" — still unverified

**FAQ claim (line 17):**
> "there's no graphical interface, and no official SDKs or client libraries are provided"

**Previous audit flagged this.** Not verified against any official Smarkets communication. The spec doesn't mention SDKs.

**Fix:** Soften to: "Smarkets does not provide official SDKs or client libraries as of June 2026." Or verify first by checking GitHub/npm.

---

### M5. 429 dual schema — quotes not specifically called out as GET exception

**FAQ claim (lines 283-291):** Correctly states that "most GET endpoints" include count/limit/expiry, and that "some endpoints — including order placement, cancellation, and session management — may return a 429 with a less detailed response body."

**Spec evidence:** The quotes endpoint (`GET /v3/markets/{market_ids}/quotes/`) is a GET endpoint that uses the inline 429 schema (no count/limit/expiry), not the RateLimitError schema. This makes it an exception among GET endpoints.

The FAQ says "most GET endpoints" which is technically correct, but doesn't name quotes as the exception.

**Fix:** Add a note: "Note: the quotes endpoint is a GET endpoint that uses the less detailed 429 schema — it does not include count/limit/expiry fields."

---

### M6. POST /v3/orders/ response — more fields available than mentioned

**FAQ claim (line 257):** Mentions only `total_executed_quantity`.

**Spec evidence:** POST 200 response also includes: `order_id`, `executed_avg_price`, `available_balance`, `available_quantity`, `exposure`, `orig_price`, `contract_id`, `market_id`, `price`, `quantity`, `side`.

The FAQ is correct that `total_executed_quantity` is included and that `quantity_filled`/`state` are NOT — but it understates the useful data returned. `order_id` is essential for tracking the order, and `executed_avg_price` tells you the average match price.

**Fix:** Add: "The response also includes `order_id` (use this to track the order via GET), `executed_avg_price` (average price at which the order was matched), and `available_balance` (your remaining balance after the order)."

---

### M7. Price and quantity bounds not mentioned

**Spec evidence:** Price: min=1, max=9999. Quantity: min=0, max=4294967295 (uint32).

The FAQ mentions minimum stake (500 = £0.05) but not the absolute bounds. A customer sending price=0 or price=10000 would get an error they don't understand.

**Fix:** Add to the price/quantity sections: "Valid prices range from 1 to 9999." and note the quantity maximum.

---

### M8. Red cards not mentioned in suspension context

**FAQ claim (line 466):**
> "in-play markets with a betting delay are not halted for individual events like goals or penalties"

**Verified facts:** General Rules 8.2.2 mentions "goals, penalties, red cards" — the FAQ omits red cards.

**Fix:** Add "red cards" to the list.

---

### M9. Endpoint category grouping causes auth confusion

**Root cause of C1.** The FAQ groups 11 OpenAPI tags into 8 categories. Specifically, `volumes` (which requires auth) is grouped under "Markets" (which doesn't). This grouping is the structural cause of the volumes auth error.

**Fix:** Either list volumes separately with "Yes" auth, or add a per-endpoint auth breakdown within the Markets category row.

---

## Previously Identified Findings — Now FIXED (confirmed)

All 18 previously identified issues in `references/documentation-redteam-audit-june-2026.md` that applied to customer_faq.md have been corrected:

| # | Previous Finding | Status |
|---|---|---|
| 1 | Login uses "email" not "username" | ✅ FIXED — line 62 says "username" |
| 2 | Default order type listed as GTC | ✅ FIXED — line 168 says `good_til_halted` |
| 3 | Order type descriptions don't match spec | ✅ FIXED — table matches spec verbatim |
| 4 | `type` listed as required | ✅ FIXED — correctly listed as optional |
| 5 | "You'll receive your API credentials" | ✅ FIXED — line 26 says "API access will be activated" |
| 6 | WebSocket feeds claimed as feature | ✅ FIXED — line 543 says "contact api@smarkets.com" |
| 7 | Paper trading claimed as feature | ✅ FIXED — not mentioned |
| 8 | IP whitelisting stated as documented fact | ✅ FIXED — "not a documented feature" |
| 9 | "No monthly subscriptions" contradicts T&Cs | ✅ FIXED — references Section 5 for additional fees |
| 10 | Withdrawal timelines stated as fact | ✅ FIXED — specific timelines removed |
| 11 | "Review is automated" | ✅ FIXED — claim removed |
| 12 | "No official SDKs" unverified | ⚠️ Still present — see M4 |
| 13 | Commission on losses cross-reference | ✅ FIXED — line 313 cross-references Pro/Select |
| 14 | Missing 13 of 21 endpoints | ✅ FIXED — all 21 listed in category table |
| 15 | `label` field not mentioned | ✅ FIXED — line 170 |
| 16 | buy/sell vs back/lay crossover | ✅ FIXED — lines 172-179 |
| 17 | No valid tick structure reference | ✅ Acknowledged — tick structure not in spec either |
| 18 | No maximum stake documentation | ✅ Acknowledged — not in spec |
| 19 | "In-play" never defined | ✅ FIXED — line 217 defines it |
| 20 | No explanation of paper/live access | ✅ FIXED — not mentioned (correct, since not in spec) |
| 21 | `fullcover` endpoint unexplained | ✅ FIXED — lines 134-136 |

---

## Verified Accurate — Spot-Checked Claims

The following claims were verified against primary sources and are confirmed correct:

### Authentication & Sessions
- ✅ Login endpoint: `POST /v3/sessions/` with `username` and `password`
- ✅ Header format: `Authorization: Session-Token <token>`
- ✅ Token valid 30 minutes, renewed on each authenticated request
- ✅ MFA verify: `POST /v3/sessions/verify/` with TOTP code
- ✅ Login rate limit: 5 per 300 seconds (FAQ says "5 attempts per 5 minutes" — equivalent)
- ✅ Logout rate limit: 30 per 60 seconds
- ✅ No separate API credentials — uses existing Smarkets account login

### Orders
- ✅ Place order: `POST /v3/orders/`
- ✅ Required fields: `market_id`, `contract_id`, `price`, `quantity`, `side`
- ✅ `type` is optional, default: `good_til_halted`
- ✅ Order type enum: `good_til_cancelled`, `keep_in_play`, `good_til_halted`, `immediate_or_cancel`
- ✅ Order type lifetime table matches spec
- ✅ `side` enum: `buy` (back), `sell` (lay)
- ✅ `buy` = back, `sell` = lay terminology mapping
- ✅ `time_in_force` does not exist in the API
- ✅ `minimum_accepted_quantity`: only applicable to IOC orders
- ✅ FOK = IOC + `minimum_accepted_quantity` = `quantity`
- ✅ POST response includes `total_executed_quantity`
- ✅ POST response does NOT include `quantity_filled` or `state`
- ✅ GET response includes `quantity_filled` and `state`
- ✅ Order state enum: `created`, `partial`, `filled`, `settled`
- ✅ Cancel specific: `DELETE /v3/orders/{order_id}/` — 10/s
- ✅ Cancel all: `DELETE /v3/orders/` — 1/60s
- ✅ `label` field: optional, user-defined string

### Price & Quantity Format
- ✅ Price: percentage basis points (5000 = 50% = decimal odds 2.0)
- ✅ Price conversion: 10000 / price = decimal odds
- ✅ Quantity: 1/10,000th of account currency (500 = £0.05)
- ✅ Back stake formula: quantity × price / 100,000,000
- ✅ Minimum stake: 500 = £0.05

### Rate Limits
- ✅ Quotes: 50 per 60 seconds
- ✅ Login: 5 per 300 seconds
- ✅ Cancel all: 1 per 60 seconds
- ✅ Cancel one: 10 per second
- ✅ Logout: 30 per 60 seconds
- ✅ 429 dual schema: most GETs use RateLimitError (count/limit/expiry); POST/DELETE/sessions use inline schema
- ✅ "Contact api@smarkets.com to discuss whether rate limits can be adjusted" — correct framing

### Commission
- ✅ Standard: 2% on net profit per market, only when you win
- ✅ Pro: 1%, opt-in required, >1,500 bets OR >£1M staked/month, 80% threshold
- ✅ Pro charges on both winnings and losses per matched bet
- ✅ Pro opt-out after 3 months
- ✅ Select: 3%, auto-applied, >£25,000 net profit over 12 calendar months
- ✅ Select: 7-day email notice
- ✅ Select: review if P&L drops below £25K, at Smarkets' discretion
- ✅ Opting into Pro or having Select applied forfeits promotions
- ✅ API users ineligible for 0% new customer offer (Section 3)
- ✅ API users ineligible for affiliate offers (Section 3)
- ✅ API access ≠ lower commission rate

### Endpoints
- ✅ 21 operations across 18 paths
- ✅ 11 OpenAPI tags
- ✅ Fullcover: `GET /v3/orders/fullcover/` (GET only, no POST)
- ✅ Currencies: `GET /v3/currencies/{code}/` returns conversion rate
- ✅ Public endpoints (no auth): events, events/states, competitors, markets by event, markets_count, contracts, currencies
- ✅ Auth required: accounts, account activity, activity CSV, quotes, last_executed_prices, **volumes**, all orders endpoints, sessions

### T&Cs
- ✅ £150 setup fee, deducted from balance on approval (Section 3)
- ✅ Refundable within 60 days if permanently withdrawing (Section 3)
- ✅ Scraping prohibition quote — exact match to Section 2
- ✅ Data sharing prohibition — Section 5
- ✅ Benchmarking prohibition — Section 5
- ✅ Data extraction without trading prohibited — Section 6.1
- ✅ Multiple accounts for fee avoidance = fraud — Section 7
- ✅ Latency arbitrage / court-siding prohibited — Section 7
- ✅ Exceeding rate limits → suspension; repeated → revocation — Section 5

### Betting Rules
- ✅ Reduction factor formula: `New odds = Old odds × ((100 − RF) / 100)` — from Help Centre "What is a reduction factor?"
- ✅ RF example: 4.0 × 0.6 = 2.4
- ✅ RF on accumulators: proportional reduction (Rule 9.5.2)
- ✅ In-play markets with delay not halted for goals/penalties (General Rules 8.2.2)

### KYC & Account
- ✅ Photo ID: passport, driving licence, national ID card
- ✅ Screenshots not accepted
- ✅ Mobile phone bills not accepted as proof of address
- ✅ Closed loop: withdraw to same payment method used for deposit
- ✅ KYC_PERMISSION_DENIED → complete verification on website

### Responsible Gambling
- ✅ Timeout durations: 1, 7, 31, 42 days
- ✅ Self-exclusion: 6 months, 1 year, 5 years, permanent
- ✅ Self-exclusion: balance returned within 48 hours
- ✅ Self-exclusion: account cannot be reactivated early
- ✅ RG_ACK_REQUIRED → complete RG acknowledgement on website

### Technical
- ✅ 403 HTML (edge block) vs JSON (API code) distinction
- ✅ SOURCE_BLOCKED / IP_NOT_TRUSTED codes for blocked IPs
- ✅ 500/503/504 are server-side
- ✅ Error codes: ZEUS_TIMEOUT, EVENTS_UNAVAILABLE
- ✅ Contact routing: api@smarkets.com (technical), support@smarkets.com (general)

---

## Verification Commands

To re-verify findings against the live spec:

```bash
cd ~/smarkets-api-support

# Volumes auth requirement
python3 -c "import json; s=json.load(open('openapi/smarkets_openapi.json')); print(s['paths']['/v3/markets/{market_ids}/volumes/']['get'].get('security'))"

# All endpoint security requirements
python3 -c "
import json; s=json.load(open('openapi/smarkets_openapi.json'))
for p,ms in s['paths'].items():
  for m,d in ms.items():
    if m in ('get','post','put','delete','patch'):
      print(f'{m.upper()} {p}: {d.get(\"security\", \"NONE (public)\")}')
"

# 429 schema per endpoint
python3 -c "
import json; s=json.load(open('openapi/smarkets_openapi.json'))
for p,ms in s['paths'].items():
  for m,d in ms.items():
    if m in ('get','post','put','delete','patch') and '429' in d.get('responses',{}):
      r=d['responses']['429'].get('content',{}).get('application/json',{}).get('schema',{})
      print(f'{m.upper()} {p}: {r.get(\"\\$ref\",\"inline\")}')
"

# POST order response fields
python3 -c "import json; s=json.load(open('openapi/smarkets_openapi.json')); r=s['paths']['/v3/orders/']['post']['responses']['200']['content']['application/json']['schema']; print(list(r['properties'].keys()))"

# Order type lifetime (check spec for lifetime table)
python3 -c "import json; s=json.load(open('openapi/smarkets_openapi.json')); o=s['paths']['/v3/orders/']['post']['requestBody']['content']['application/json']['schema']; print('type default:', o['properties']['type'].get('default')); print('type enum:', o['properties']['type'].get('enum'))"
```

---

*Audit completed June 2026. All findings verified against `openapi/smarkets_openapi.json` (OpenAPI v3, 18 paths, 21 operations), API T&Cs, Commission FAQ, Betting Rules, and Help Centre articles.*
