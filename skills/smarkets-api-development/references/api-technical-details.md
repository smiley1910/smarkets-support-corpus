# Smarkets API Technical Details

## OpenAPI Spec

- **URL**: `https://api.smarkets.com/v0/control/openapi/`
- **Tagged**: `?tags=trading_api` (but returns 404 on v3 control endpoint — use v0)
- **Format**: OpenAPI 2.0

## Authentication

### Login
```
POST /v3/sessions/
Content-Type: application/json
Body: {"username": "user@example.com", "password": "***"}
```

- **Success**: 201 Created (NOT 200)
- **Response body**: `{"token": "BQQBAA...", "refresh_token": "...", "factor": "complete", "stop": "2026-07-16T14:40:02Z", "verify": false, "created_social_member": false}`
- **Cookies set**: `User-Session-Token`, `Refresh-Token`, `Logged-In`, `device-cookie`
- **Rate limit**: 5 requests per 300 seconds (the tightest endpoint-specific cap)
- **Token lifetime**: 30min sliding — every authenticated call renews it for another 30min, so a bot active every few minutes rarely needs a fresh login

### Authenticated Requests
All three methods work:
1. `Authorization: Session-Token {token}` (documented standard)
2. `Authorization: Bearer {token}`
3. Cookie: `User-Session-Token={token}`

Always set `allow_redirects=False` to prevent credential leakage via 3xx redirects.

### Logout
```
DELETE /v3/sessions/
```

## Rate Limits

### Global
- 1200 requests per 60 seconds, per account, across all endpoints

### Per-Endpoint Caps

| Endpoint | Limit | RPM Equivalent |
|----------|-------|----------------|
| GET /v3/events/ | 600 per 60s | 600 |
| POST /v3/sessions/ | 5 per 300s | 1 |
| DELETE /v3/sessions/ | 30 per 60s | 30 |
| GET /v3/markets/{ids}/quotes/ | 50 per 60s (API users; lower ~20 for non-API) | 50 |
| POST /v3/orders/ | 10 per 1s | 600 |
| DELETE /v3/orders/ | 1 per 60s | 1 |
| DELETE /v3/orders/{id}/ | 10 per 1s | 600 |

Sum of documented per-endpoint caps (1882) EXCEEDS the global pool (1200). Per-endpoint caps are concurrent maximums, NOT additive allocations. The global cap takes precedence.

14 endpoints have NO documented per-endpoint limit and share the 1200 RPM global pool.

Quoted `X-RateLimit-Limit` headers are ground truth for that account's effective tier — a lower header (e.g. 20 on quotes) means the account is on the non-API tier, not that the docs are wrong.

### 429 Response Format
```json
{
  "error_type": "RATE_LIMIT_EXCEEDED",
  "data": {
    "count": 6,
    "limit": 5,
    "expiry": "Thu, 16 Jul 2026 11:21:18 GMT"
  }
}
```

- `expiry` is **RFC 2822 format**, not ISO 8601
- Parse with `email.utils.parsedate_to_datetime()`
- Also returned in response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Exception: quotes, order placement/cancellation, and session 429s use an inline schema with NO `count`/`limit`/`expiry` in the body — fall back to the `X-RateLimit-Reset` header (seconds, clamp wait to minimum 5s) or a short fixed wait, never tell the caller to "check the expiry field" on those routes.

## Event Discovery

### Search (recommended for horse racing)
```
GET /v3/search/horse/
→ {"search_result_event_ids": ["45200422", "45200439", ...], "count": 20, "pagination": {...}}
```

### Event Details
```
GET /v3/events/{comma_separated_ids}/
→ {"events": [{"id": "45200422", "name": "15:25", "type": "horse_racing_race", "start_datetime": "2026-07-16T14:25:00Z", "state": "..."}]}
```

### Important: type filtering does NOT work
```
GET /v3/events/?type=horse_racing     → 400
GET /v3/events/?type_domain=horse-racing → returns 0 events

`state=live|upcoming` IS valid, but the listing is id-ordered, not time-ordered: without `sort=id` plus following `pagination.next_page`'s `pagination_last_id`, offset-only paging returns the same stale top-level category events on every page. Walk the full pagination and filter client-side (e.g. `full_slug` prefix for golf tournaments).
```

Instead: use search endpoint, fetch events by ID, filter client-side by `type == "horse_racing_race"`.

## Markets

```
GET /v3/events/{event_id}/markets/?limit=10
→ {"markets": [{"id": "151524314", "name": "To win", ...}, {"id": "151524315", "name": "To place (top 2)", ...}]}
```

Horse racing typically has 3 markets: To win, To place (top 2), To place (top 3).

## Contracts (Horses)

```
GET /v3/markets/{market_id}/contracts/
→ {"contracts": [{"id": "420334286", "name": "English Oak"}, {"id": "420334288", "name": "Salam Dubawi"}, ...]}
```

## Quotes (Price Data)

```
GET /v3/markets/{market_id}/quotes/
→ {
  "420334286": {
    "bids": [
      {"price": 4032, "quantity": 1949900},
      {"price": 4000, "quantity": 2198998},
      ...
    ],
    "offers": [
      {"price": 4065, "quantity": 1827618},
      {"price": 4167, "quantity": 4326416},
      ...
    ]
  },
  ...
}
```

- **bids** = resting BACK orders (people wanting to back this horse). Sorted descending by price.
- **offers** = resting LAY orders (people wanting to lay this horse). Sorted ascending by price.
- **Best available BACK price** = `offers[0].price` (lowest offer = match the cheapest lay order)
- **Best available LAY price** = `bids[0].price` (highest bid = match the most generous back order)
- **Spread** = `offers[0].price - bids[0].price`

### Finding the Favourite
The favourite has the lowest decimal odds = highest price in basis points.
Compare `offers[0].price` across all contracts — the highest one is the favourite.

## Order Placement

```
POST /v3/orders/
Content-Type: application/json
Authorization: Session-Token {token}

{
  "market_id": "151524314",
  "contract_id": "420334288",
  "price": 4310,
  "quantity": 1160,
  "side": "buy",
  "type": "immediate_or_cancel",
  "label": "strategy_1"  // optional
}
```

### Price (basis points)
- Percentage in basis points: 5000 = 50% = 2.0 decimal odds
- Formula: `decimal_odds = 10000 / price`
- Valid range: 1-9999
- Must conform to a valid tick on the exchange (invalid ticks return error)

### Quantity
- Units: 1/10000 of currency unit (500 = £0.05)
- Back stake formula: `back_stake = quantity * price / 100000000`
- To calculate quantity for desired stake: `quantity = stake * 100000000 / price`
- Example: £0.05 back at price 4310 → quantity = 0.05 * 100000000 / 4310 ≈ 1160
- Minimum stake: £0.05 or currency equivalent

### Side
- `"buy"` = BACK (bet the horse will win)
- `"sell"` = LAY (bet the horse will lose)

### Order Types

| Type | Market Goes Live | Market Halted | Reduction Factor |
|------|-----------------|----------------|-----------------|
| good_til_cancelled | Cancelled | Cancelled | Cancelled |
| good_til_halted (default) | Kept | Cancelled | Cancelled |
| keep_in_play | Kept | Kept | Cancelled |
| immediate_or_cancel | N/A (immediate) | N/A | N/A |

- `immediate_or_cancel`: fill what you can immediately, cancel the rest. Use `minimum_accepted_quantity` to require a minimum fill.
- All others rest in the book until matched or cancelled by market events.

### Rate Limit
- 10 requests per 1 second (600 RPM equivalent)

## Account Endpoints

```
GET /v3/accounts/             → account info
GET /v3/accounts/activity/    → statement
GET /v3/balance/               → current balance
GET /v3/orders/                → current orders
GET /v3/orders/{order_id}/     → single order status
DELETE /v3/orders/             → cancel all orders
DELETE /v3/orders/{order_id}/  → cancel specific order
```
