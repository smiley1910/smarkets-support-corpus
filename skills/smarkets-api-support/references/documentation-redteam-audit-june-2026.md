# Documentation Red-Team Audit (June 2026)

*Audit of `training/confluence_draft_v2.md` (CS Agent KB) and `training/customer_faq.md` (Customer FAQ) against the live OpenAPI spec.*

## How to Use This File

When updating or revising either documentation file, check this file first for known issues. Each finding lists the severity, what's wrong, the spec evidence, and the fix.

## Factual Errors (verified against live spec)

### 1. Login field name vs customer concept — CORRECTED

**Spec evidence:** POST /v3/sessions/ schema has `username` (required) and `password` (required). No `email` field.

**⚠️ CORRECTION (June 2026):** The original finding said "Change all references from 'email' to 'username'." This was WRONG. The API field is called `username` in the JSON schema, but Smarkets customers do NOT have a separate username — they authenticate with their email address. The correct approach:
- In the JSON request body: use `"username"` as the field name (the spec requires it)
- The VALUE of that field is the customer's email address: `"username": "customer@email.com"`
- In customer-facing prose: always say "email" — never "username", as customers don't have one

**Where it was wrong:** customer_faq.md line 62 said "with your email and password". The original audit changed this to "username" which was incorrect — it confused the API field name with the customer concept.

**Fix (corrected):** Keep "email" in customer-facing language. Use `username` only as the JSON field name in code examples. Add a note: "The API field is called `username` — use your email address as the value."

### 2. Default order type is `good_til_halted`, not `good_til_cancelled`

**Spec evidence:** `type` field has `default=good_til_halted` in the OpenAPI schema.

**Where it's wrong:** Both documents describe `good_til_cancelled` as the default or "most bets" type.

**Fix:** State that `good_til_halted` is the default. If a customer omits `type`, they get GTH behaviour.

### 3. Order type descriptions don't match the spec's lifetime table

**Spec evidence:**
| Order type | Market goes live | Market halted | RF applied |
|---|---|---|---|
| good_til_cancelled | Cancelled | Cancelled | Cancelled |
| good_til_halted | Kept | Cancelled | Cancelled |
| keep_in_play | Kept | Kept | Cancelled |

**Where it's wrong:** Both documents oversimplify or misstate the behaviour. GTC is described as "stays open until you cancel it" — wrong, it's cancelled in three situations by the exchange. GTH is described as "cancelled when halted" — misses its key feature (kept when market goes live). KIP is described as "survives market state changes" — vague.

**Fix:** Include the spec's lifetime table verbatim. It's the most useful reference for customers.

### 4. `type` listed as required field

**Spec evidence:** Required fields are `market_id`, `contract_id`, `price`, `quantity`, `side`. `type` is optional with default `good_til_halted`.

**Where it's wrong:** customer_faq.md line 149-156 lists `type` as a required field.

**Fix:** Move `type` to optional fields. Note the default.

### 5. "You'll receive your API credentials" is misleading

**Spec evidence:** The API uses the existing Smarkets account login (username/password → session token). There are no separate API keys in the spec. The T&Cs say "your API keys will be activated" but the actual auth flow is just the normal session login.

**Where it's wrong:** customer_faq.md line 26 step 4: "You'll receive your API credentials and can start trading."

**Fix:** Change to "Your API access will be activated — you use your existing Smarkets account credentials to log in."

## Unverified Claims Stated as Fact

### 6. WebSocket feeds — NOT in spec

The spec has zero mentions of WebSocket, streaming, or push. The FAQ states "WebSocket feeds are available" as fact. This is fabricated.

**Fix:** Remove the claim. Change to: "If you need real-time data feeds, contact api@smarkets.com."

### 7. Paper trading — NOT in spec

The spec has zero mentions of paper, sandbox, test, or staging environments. Both documents reference "paper trading" as a feature.

**Fix:** Add caveat: "A test environment may be available — contact api@smarkets.com to confirm."

### 8. IP whitelisting — NOT in spec

Both documents state "Smarkets doesn't offer IP whitelisting" as documented fact.

**Fix:** Change to "IP whitelisting is not a documented feature of the API."

### 9. "No monthly subscriptions or per-request charges" — contradicts T&Cs

T&Cs Section 5: "API usage may be subject to specific restrictions and/or incur additional fees."

**Fix:** "After the one-time setup fee, you pay normal exchange commission. Some use cases may incur additional fees — see Section 5 of the API T&Cs."

### 10. Withdrawal timelines — not from Smarkets docs

"Debit card: 1-3 business days, Bank transfer: 1-5 business days" are generic industry estimates.

**Fix:** Mark as estimates or remove specific numbers.

### 11. "The review is automated for the most part" — unverified

No basis for this claim about internal compliance review process.

**Fix:** Remove the automation claim.

### 12. "Smarkets doesn't provide official SDKs" — unverified

Not checked against any official Smarkets communication.

**Fix:** Soften to "Smarkets does not provide official SDKs as of June 2026" or verify first.

## Internal Contradictions

### 13. Commission on losses

FAQ line 271: "You only pay commission when you win" (Standard Tier).
FAQ line 291: "On the Pro Tier, commission is charged on winnings if the bet wins, and on losses if the bet loses."

Both correct for their tiers, but no cross-reference. A customer reading top-to-bottom hits a contradiction.

**Fix:** Line 271 should say "On the Standard Tier, you only pay commission when you win. Pro and Select tiers charge on both winnings and losses — see below."

## Missing Coverage (Gaps)

### 14. Missing 13 of 21 endpoints

The FAQ endpoint table lists 8 endpoints. Missing: event states, markets by event, markets_count, volumes, fullcover orders, account_activity_csv, accounts/activity.

### 15. `label` field not mentioned

Optional field for tagging trading strategies. Useful for API customers running multiple strategies.

### 16. buy/sell vs back/lay terminology crossover

No callout that Smarkets uses `buy`/`sell` while Betfair uses `BACK`/`LAY`. Migrating customers will be confused.

### 17. No valid tick structure reference

Both documents say "valid prices must be on the tick structure" but neither explains what it is. The spec doesn't either.

### 18. No maximum stake documentation

Minimum is 500 (£0.05). Maximum not mentioned in either document or the spec.

### 19. "In-play" used but never defined

The term appears in order type descriptions without explanation.

### 20. No explanation of how to access paper/live environments

If paper trading exists, the access path is undocumented.

### 21. `fullcover` endpoint unexplained

GET /v3/orders/fullcover/ exists in the spec. Neither document explains what a fullcover order is.

## Spec Verification Commands

To re-verify these findings against the live spec:

```bash
# Default order type
python3 -c "import json; spec=json.load(open('openapi/smarkets_openapi.json')); print(spec['paths']['/v3/orders/']['post']['requestBody']['content']['application/json']['schema']['properties']['type'].get('default'))"

# Login field name
python3 -c "import json; spec=json.load(open('openapi/smarkets_openapi.json')); print(spec['paths']['/v3/sessions/']['post']['requestBody']['content']['application/json']['schema'].get('required'))"

# Required fields for order creation
python3 -c "import json; spec=json.load(open('openapi/smarkets_openapi.json')); print(spec['paths']['/v3/orders/']['post']['requestBody']['content']['application/json']['schema'].get('required'))"

# WebSocket presence
python3 -c "import json; spec=json.load(open('openapi/smarkets_openapi.json')); s=json.dumps(spec); print('WebSocket' in s, 'streaming' in s.lower())"

# Paper/sandbox presence
python3 -c "import json; spec=json.load(open('openapi/smarkets_openapi.json')); s=json.dumps(spec); print(any(x in s.lower() for x in ['paper','sandbox','staging']))"
```
