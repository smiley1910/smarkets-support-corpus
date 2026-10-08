# Smarkets API - Troubleshooting Guide

> Common API issues, their causes, and step-by-step resolution.
> Source: Official Smarkets documentation and API spec.

---

## 1. Authentication Issues

### 1.1 "AUTH_REQUIRED" (401)
**Error:** `{"error_type": "AUTH_REQUIRED", "data": "..."}`

**Causes:**
- Missing or malformed Authorization header
- Expired session token
- Invalid session token
- Header-only clients: dropped at the ~20 minute session token rotation, even while polling (verified 2026-10-01)

**Checklist:**
- [ ] Is your Authorization header formatted correctly: `Authorization: Session-Token <token>`?
- [ ] Has your session token expired? Tokens have a limited lifetime - re-authenticate via `POST /v3/sessions/`
- [ ] Did you complete MFA verification? Check if your account has MFA enabled and use `POST /v3/sessions/verify/`
- [ ] Are you sending the token in the correct header? It must be `Authorization`, not `X-API-Key` or custom headers

**Resolution:**
1. Call `POST /v3/sessions/` with your credentials to get a fresh token
2. If MFA enabled, follow up with `POST /v3/sessions/verify/`
3. Use the new token in subsequent requests
4. Long sessions: send `Cookie: User-Session-Token=<token>; Refresh-Token=<refresh_token>` with every request and adopt each renewed `User-Session-Token`. A header-only token is rejected at the ~20 minute rotation (fix verified live 2026-10-01).

### 1.2 "FORBIDDEN" (403)
**Error:** `{"error_type": "FORBIDDEN", "data": "..."}`

**Causes:**
- Account not approved for API access
- API access has been suspended or revoked
- Trying to access endpoints or data outside your approved scope
- Account under compliance review (first 60 days)

**Checklist:**
- [ ] Has the GBP150 setup fee been paid and processed?
- [ ] Has your API application been formally approved?
- [ ] Are you within the first 60-day compliance review period?
- [ ] Have you been rate-limited or suspended recently?
- [ ] Are you trying to access markets/events outside your pre-approved scope?

**Resolution:**
1. Verify API access status by checking your account or contacting support@smarkets.com
2. If in the 60-day compliance window, ensure your account passes review
3. Submit a new API Request Form if access was never granted
4. Contact api@smarkets.com for access issues

---

## 2. Rate Limiting

### 2.1 "RATE_LIMIT_EXCEEDED" (429)
**Error:**
```json
{
  "error_type": "RATE_LIMIT_EXCEEDED",
  "data": {
    "count": 150,
    "limit": 100,
    "expiry": "2026-05-19T23:00:00Z"
  }
}
```

**Causes:**
- Exceeding your pre-approved call limit for the current period
- Too many requests in too short a time window
- Aggressive polling of quotes or prices

**Checklist:**
- [ ] What is your approved call limit? (check expiry field in error data)
- [ ] Are you polling quotes/prices more frequently than needed?
- [ ] Are you placing/cancelling orders in rapid succession?
- [ ] Are multiple API clients running under the same account?

**Resolution:**
1. Stop making requests until the `expiry` timestamp
2. Implement exponential backoff when approaching limits
3. Cache quotes/prices rather than polling continuously
4. Batch requests where possible (e.g., multiple event IDs in one call)
5. If your use case genuinely requires higher limits, contact api@smarkets.com

**Best Practices:**
- Use the `count`, `limit`, and `expiry` fields in the error to understand your usage pattern
- Track your request count locally to anticipate limit breaches
- Subscribe to WebSocket feeds for real-time data instead of polling HTTP

---

## 3. Request Validation Errors

### 3.1 "REQUEST_VALIDATION_ERROR" (400)
**Error:** `{"error_type": "REQUEST_VALIDATION_ERROR", "data": "description of the error"}`

**Common Causes:**

| Issue | Example |
|-------|---------|
| Invalid event IDs | `events/abc123/` (wrong format) |
| Invalid market IDs | Wrong ID format or non-existent market |
| Missing required fields | Order without price or quantity |
| Wrong data types | String where number expected |
| Bad datetime format | Wrong format in account_activity_csv |
| Too many IDs | 414 REQUEST_TOO_LARGE — batch your IDs into smaller groups |
| Query too broad | RECKONATOR_REQUEST_TOO_LARGE — narrow date range |

**Checklist:**
- [ ] Check the `data` field in the error for specific validation message
- [ ] Verify event/market IDs exist and are in the correct format
- [ ] For order placement: are all required fields present? (price, quantity, side, contract_id)
- [ ] For account activity CSV: are start/end datetimes on the hour, exactly 1 hour apart?

**Resolution:**
1. Read the error message in `data` carefully - it describes exactly what's wrong
2. Fix the invalid parameter based on the error description
3. For IDs: ensure they match the format returned by `/v3/events/` or `/v3/markets/`

---

## 4. Order Issues

### 4.1 Order Not Placed / Rejected
**Problem:** `POST /v3/orders/` returns an error or order is not visible in `GET /v3/orders/`

**Checklist:**
- [ ] Is the market open and accepting bets? Check event/market state
- [ ] Do you have sufficient available balance? (`available_balance` in `/v3/accounts/`)
- [ ] Is the price you're offering within the current spread?
- [ ] Is the contract ID valid and for the correct market?
- [ ] Are you trying to bet on a restricted/pre-approved-only market?
- [ ] Is your account under compliance review restrictions?

**Resolution:**
1. Check account balance: `GET /v3/accounts/`
2. Verify market is open: `GET /v3/events/{event_ids}/states/`
3. Review the error response for specific rejection reason
4. If price is too aggressive, check current quotes via `GET /v3/markets/{market_ids}/quotes/`

### 4.2 Order Not Appearing
**Problem:** Order placed successfully (200 response) but doesn't show in `GET /v3/orders/`

**Possible causes:**
- Order was immediately filled (check last executed prices)
- Order was cancelled by the system (e.g., market closed)
- Look at recently settled orders - the endpoint returns both open AND recently settled

### 4.3 Cannot Cancel Order
**Problem:** `DELETE /v3/orders/{order_id}/` fails

**Checklist:**
- [ ] Is the order ID correct?
- [ ] Has the order already been filled/cancelled?
- [ ] Has the market/event settled?
- [ ] Is the order yours? (you can only cancel your own orders)

**Resolution:**
1. Verify the order status via `GET /v3/orders/`
2. Once a market has settled, orders can no longer be cancelled
3. If the order was already cancelled, the DELETE is idempotent - it succeeds regardless

---

## 5. Data & Market Issues

### 5.1 No Events Returned
**Problem:** `GET /v3/events/` returns empty or unexpected results

**Checklist:**
- [ ] Are there events currently available for your account's jurisdiction?
- [ ] Is your account restricted to certain event types?
- [ ] Check query parameters - are date filters too narrow?

### 5.2 Market Data Seems Wrong
**Problem:** Quotes or prices look incorrect or stale

**Checklist:**
- [ ] Check `GET /v3/markets/{market_ids}/last_executed_prices/` for actual traded prices
- [ ] Compare with `GET /v3/markets/{market_ids}/quotes/` for current order book
- [ ] Verify the market ID is correct
- [ ] Note: quotes show the best bid/ask on the order book, not necessarily what will fill

### 5.3 Account Activity CSV Issues

**Error Types:**
- `INVALID_DATETIMES` (400) - Datetimes must be exactly on the hour, separated by exactly 1 hour
- `NO_CSV_AVAILABLE` (404) - No activity data for that time range

**Expected datetime format:** ISO 8601 (e.g., `2026-05-19T20:00:00Z`)
**Constraints:**
- Start and end must be exactly 1 hour apart
- Both must be on the hour (:00 seconds)
- Example: start=`2026-05-19T14:00:00Z`, end=`2026-05-19T15:00:00Z`

---

## 6. Account & Permission Issues

### 6.1 API Access Revoked / Suspended

**Possible causes from T&Cs:**
- Exceeded rate limits repeatedly
- Use of API outside approved scope (scraping, benchmarking, etc.)
- Failed 60-day compliance review
- Suspicious activity detected (browser impersonation, concealed calls)
- Changes to technical setup not communicated to Smarkets

**Resolution:**
1. Contact api@smarkets.com or support@smarkets.com to understand why
2. If rate-limit related, reduce call frequency and re-apply
3. If compliance-related, provide requested documentation
4. Note: API access can be withdrawn at any time without notice per Section 5

### 6.2 Setup Fee Questions

- Fee: GBP150 one-time, deducted upon approval
- **Refundable** if you withdraw from API within first 60 days
- API customers are ineligible for affiliate/0% commission offers
- Standard Customer Commission applies

---

## 7. Connection & Network Issues

### 7.1 Timeouts / Connection Errors

**Checklist:**
- [ ] Is `https://api.smarkets.com` reachable from your network?
- [ ] Are you behind a firewall or proxy that blocks API traffic?
- [ ] Is your DNS resolving correctly?
- [ ] Are you using HTTPS (not HTTP)?
- [ ] Check for TLS/SSL certificate issues

**Resolution:**
- Try `curl -v https://api.smarkets.com/v3/events/` to test connectivity
- Verify DNS resolves to a valid IP
- Check if your IP is blocked or throttled

### 7.2 Stale / Cached Data

**Resolutions:**
- Include cache-busting headers (`Cache-Control: no-cache`)
- Use WebSocket streams for real-time data
- Don't cache quotes/prices for more than a few seconds
- Check `last_executed_prices` for the most recent trade

---

## 8. Quick Diagnostic Steps

For any API issue, follow this systematic flow:

```
1. Is it Auth?
   -> 401? Check token format, expiry, MFA
   -> 403? Check access approval, compliance status

2. Is it Rate Limiting?
   -> 429? Stop requests until expiry, review usage

3. Is it Validation?
   -> 400? Check `data` field for specific error

4. Is it a Server Error?
   -> 500? Retry with backoff, contact api@smarkets.com if persistent

5. Is it Data?
   -> Wrong results? Verify IDs, check event/market state
```

---

## Key URLs Reference

| Resource | URL |
|----------|-----|
| API Base URL | https://api.smarkets.com |
| Swagger Docs | https://docs.smarkets.com |
| OpenAPI Spec | https://api.smarkets.com/v0/control/openapi/?tags=trading_api |
| API Request Form | https://support.smarkets.com/p/6MLL-PL7/api-request-form |
| Help Centre | https://help.smarkets.com/hc/en-gb |
| API Support Email | api@smarkets.com |
| General Support | support@smarkets.com |
| Document Upload | https://docs.smarkets.com/ |
