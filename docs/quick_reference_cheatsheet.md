# Smarkets API - Quick Reference Cheat Sheet

> One-page quick reference for support agents. When in doubt, consult the full docs.

---

## AUTH FLOW

```
1. POST /v3/sessions/          -> get session_token
2. POST /v3/sessions/verify/   -> if MFA enabled
3. Authorize: Session-Token <token>  -> use in all subsequent requests
4. DELETE /v3/sessions/        -> logout
```

---

## CORE ENDPOINTS (all under https://api.smarkets.com)

### Read Data (GET)
| Endpoint | What it gives you |
|----------|-------------------|
| /v3/events/ | All available events |
| /v3/events/{ids}/states/ | Current state of events |
| /v3/events/{ids}/competitors/ | Competitors/participants |
| /v3/events/{ids}/markets/ | Markets for given events |
| /v3/markets/{ids}/contracts/ | Contracts (betting outcomes) |
| /v3/markets/{ids}/quotes/ | Current prices (best bid/ask) |
| /v3/markets/{ids}/last_executed_prices/ | Last trade prices |
| /v3/markets/{ids}/volumes/ | Traded volumes |
| /v3/orders/ | Your open + recently settled orders |
| /v3/orders/fullcover/ | Fullcover orders |
| /v3/accounts/ | Balance, exposure, currency |
| /v3/accounts/activity/ | Account statement (paginated) |
| /v3/currencies/{code}/ | FX rate for a currency |

### Write Data (POST/DELETE)
| Endpoint | What it does |
|----------|--------------|
| POST /v3/orders/ | Place a bet/order |
| DELETE /v3/orders/ | Cancel ALL orders |
| DELETE /v3/orders/{id}/ | Cancel ONE order |

### Account Statement CSV
| Endpoint | Requirements |
|----------|--------------|
| GET /v3/account_activity_csv/{start}/{end}/ | Start & end: on the hour, 1 hour apart |

---

## ERROR TYPES (FAST ID)

| HTTP | error_type | Meaning |
|------|-----------|---------|
| 400 | REQUEST_VALIDATION_ERROR | Bad params - check data field |
| 400 | INVALID_DATETIMES | CSV dates not on the hour |
| 400 | BAD_REQUEST | Badly formed params (markets/prices) |
| 400 | RECKONATOR_REQUEST_TOO_LARGE | Account activity query too broad |
| 401 | AUTH_REQUIRED | Bad/expired token |
| 403 | FORBIDDEN | No permission / not approved |
| 404 | NO_CSV_AVAILABLE | No data for that time range |
| 404 | NO_RESULTS_FOUND | Event states - no matching events |
| 414 | REQUEST_TOO_LARGE | Too many IDs in one request |
| 429 | RATE_LIMIT_EXCEEDED | Hit your limit - check expiry |
| 451 | COUNTRY_BLOCKED | Jurisdiction not supported |
| 500 | INTERNAL_ERROR | Server problem - retry |
| 503 | (various) | Subsystem down - note the code |
| 504 | ZEUS_TIMEOUT | Trading engine timeout |

**RateLimitError data:**
```json
{"count": N, "limit": N, "expiry": "ISO_TIMESTAMP"}
```

---

## COMMON SUPPORT QUESTIONS

**Q: How do I get API access?**
A: Submit the API Request Form at https://support.smarkets.com/p/6MLL-PL7/api-request-form. GBP150 setup fee. Approval required.

**Q: What's the GBP150 for?**
A: One-time admin setup fee. Refundable if you cancel API within 60 days.

**Q: Can I get the 0% commission?**
A: No. API customers are ineligible for affiliate/0% commission offers.

**Q: Why am I getting 403?**
A: Not approved, under 60-day compliance review, or access revoked.

**Q: How do I cancel an order?**
A: `DELETE /v3/orders/{order_id}/` - or cancel ALL with `DELETE /v3/orders/`

**Q: Rate limits?**
A: Pre-approved per account. Check `expiry` in the error. Stop until it resets.

**Q: Am I allowed to scrape odds?**
A: No. Strictly prohibited. Odds scraping, browser impersonation, reverse engineering = account suspension.

**Q: Can I share market data?**
A: No. Cannot share, sell, or distribute platform data without written approval.

**Q: Contact for API issues?**
A: api@smarkets.com

---

## USEFUL CURL TESTS

```bash
# Login
curl -X POST https://api.smarkets.com/v3/sessions/ -H "Content-Type: application/json" -d '{"email":"...","password":"..."}'

# Get account (with token)
curl https://api.smarkets.com/v3/accounts/ -H "Authorization: Session-Token <token>"

# Get events
curl https://api.smarkets.com/v3/events/ -H "Authorization: Session-Token <token>"

# Get quotes
curl "https://api.smarkets.com/v3/markets/{market_ids}/quotes/" -H "Authorization: Session-Token <token>"

# Cancel all orders
curl -X DELETE https://api.smarkets.com/v3/orders/ -H "Authorization: Session-Token <token>"
```

---

## DATA TYPES REFERENCE

- **event_ids**: comma-separated list of event IDs
- **market_ids**: comma-separated list of market IDs
- **order_id**: single order UUID
- **currency code**: AUD, BRL, CAD, CHF, CZK, DKK, EUR, GBP, HKD, HUF, JPY, NOK, PLN, SEK, USD
- **datetime**: ISO 8601 format (e.g., `2026-05-19T14:00:00Z`)

---

## ACCOUNT RESPONSE FIELDS
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
