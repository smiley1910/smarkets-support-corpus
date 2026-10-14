# No-Auth Quotes Endpoint — Confirmed Behaviour

> **Verified:** 2026-06-26 via public API testing (no auth, no credentials)
> **Related:** `references/quotes-endpoint-behaviour.md` (P2P-only filtering theory)

## Summary

The `GET /v3/markets/{market_ids}/quotes/` endpoint returns full P2P order book data **without any authentication**. The OpenAPI spec marks it `security: [{api_key: []}]` (required), but the actual behaviour is auth-optional with degraded freshness.

## What Works Without Auth

| Endpoint | Spec Says | Actual (no auth) |
|---|---|---|
| `GET /v3/events/` | Not required | ✅ Full event data |
| `GET /v3/events/{id}/markets/` | Not required | ✅ All markets |
| `GET /v3/markets/{id}/contracts/` | Not required | ✅ All contracts |
| `GET /v3/markets/{id}/quotes/` | **Required** | ✅ **Returns full order book (delayed)** |
| `GET /v3/markets/{id}/last_executed_prices/` | **Required** | ✅ Returns last trades + timestamps |
| `GET /v3/markets/{id}/volumes/` | **Required** | ✅ Returns traded volumes |
| `GET /v3/events/{id}/states/` | Not required | ✅ Returns match state + `coverage_delay` |

## Key Evidence This Is Intentional (Not a Bug)

1. **Endpoint description explicitly contemplates no-auth:** *"If session token is not sent, these prices will be delayed."* — this sentence only makes sense if the endpoint works without a token.

2. **Rate limit note distinguishes user types:** *"The rate limits below are applicable to API users. The rate limits for non-API users are lower."* — explicitly acknowledges unauthenticated callers.

3. **Systematic across all market data endpoints** — three endpoints marked auth-required all return data without auth. This is a pattern, not a single misconfiguration.

## Price Format (Basis Points — Denominator is 10,000, NOT 100,000)

**CRITICAL:** The price denominator is **10,000** (basis points), not 100,000. The skill docs already state "5000 = 50% = decimal odds 2.0" which confirms 10,000. If a user mentions "fraction contracts of 100000/1", the actual denominator in the API responses is still 10,000.

- Price `7194` → `7194/10000` = 71.94% → decimal odds `10000/7194` = **1.39**
- Price `5000` → `5000/10000` = 50% → decimal odds `10000/5000` = **2.00**
- Price `1000` → `1000/10000` = 10% → decimal odds `10000/1000` = **10.00**

### Conversion Functions

```python
DENOM = 10_000
QTY_DENOM = 10_000  # quantities are also /10,000 of GBP

def price_to_decimal(price):
    return round(DENOM / price, 2)

def price_to_pct(price):
    return round((price / DENOM) * 100, 1)

def qty_to_gbp(quantity):
    return round(quantity / QTY_DENOM, 2)
```

## What the Quotes Endpoint Returns (P2P Only)

The quotes endpoint returns the **raw peer-to-peer order book** — limit orders placed by Smarkets users. It does **NOT** include first-party market-making orders that the website displays.

Evidence the order book is P2P-only:
- Uneven depth across outcomes (Draw may have 1 offer level while Home has 5)
- Wide spreads on less popular outcomes
- Tiny retail-sized orders (£0.30 mixed with £320)
- Lower-tier matches may have completely empty books while the website shows prices (MM liquidity excluded)

See `references/quotes-endpoint-behaviour.md` for the full P2P-vs-MM analysis.

## The `coverage_delay` Field

Found in event state responses (`GET /v3/events/{id}/states/`) at `info.coverage_delay`:

```json
{
  "info": {
    "coverage_delay": 8,
    "is_betgenius_booked": true
  }
}
```

**Key findings:**
- `coverage_delay` only appears when `is_betgenius_booked: true`
- Events without BetGenius have `coverage_delay: null`
- It varies by event — it's a data-source property, not a uniform access-layer delay
- It appears on `api.smarkets.com` directly (not just sbkscores.com)

**Unresolved:** Whether `coverage_delay: 8` also appears in authenticated API responses. Both assessments in the conversation used the public (no-auth) API only. An authenticated comparison test is needed to determine if:
- (A) Authenticated responses also show `coverage_delay: 8` → inherent BetGenius feed latency affecting all consumers
- (B) Authenticated responses show `coverage_delay: null` or `0` → public-only delay

The circumstantial evidence (correlation with `is_betgenius_booked`, variation across events, field naming, nesting in `info` alongside data-source properties) suggests interpretation (A), but this has NOT been verified with authenticated access.

## Test Script

A working test script is at `scripts/noauth_live_football.py` in the workspace root:

```bash
python3 noauth_live_football.py --limit 5          # all live matches
python3 noauth_live_football.py --event-id 45155153  # specific event
python3 noauth_live_football.py --json               # JSON output
```
