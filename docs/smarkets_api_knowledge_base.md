# Smarkets API Knowledge Base

> **Source of Truth:** This document is compiled from the official Smarkets documentation at:
> - https://help.smarkets.com/hc/en-gb/articles/34720906181021-Smarkets-API-Documentation-Resources
> - https://help.smarkets.com/hc/en-gb/articles/34697834941085-Smarkets-API-Access-Integration-T-Cs
> - https://docs.smarkets.com/ (Swagger/OpenAPI portal)
> - https://api.smarkets.com/v0/control/openapi/?tags=trading_api (raw OpenAPI spec)

---

## Table of Contents
1. [Overview](#overview)
2. [Getting API Access](#getting-api-access)
3. [Authentication](#authentication)
4. [API Endpoints Overview](#api-endpoints-overview)
5. [Rate Limits & Fair Usage](#rate-limits--fair-usage)
6. [Common Errors](#common-errors)
7. [Terms & Conditions Summary](#terms--conditions-summary)
8. [Support Contact](#support-contact)

---

## Overview

The Smarkets API provides programmatic access to the Smarkets exchange engine, enabling:

- **Market Data:** Real-time access to order books and price history
- **Order Management:** Automated placing, cancelling, and updating of bets
- **Account Management:** Real-time balance tracking and transaction history

**API Base URL:** `https://api.smarkets.com`

**API Version:** 3 (OAS3 / OpenAPI 3.0.2)

**Contact:** api@smarkets.com

---

## Getting API Access

### Requirements

1. **Active Smarkets Account** - Fully registered and verified
2. **Administration Fee** - One-time GBP150 (or currency equivalent) for activation
3. **Application Approval** - Access granted via application process

*Note: API customers are ineligible for affiliate commission offers and the 60-day 0% commission offer for new customers.*

### How to Apply

1. **Review the Documentation** - Familiarise yourself with endpoints and rate limits at https://docs.smarkets.com/
2. **Submit Your Request** - Complete the API Request Form at https://support.smarkets.com/p/6MLL-PL7/api-request-form
3. **Verification & Setup** - Smarkets team reviews your application. Once approved, the deposit is deducted from your balance and API keys are activated.

### Setup Fee

- GBP150 one-time administrative setup fee
- Deducted from account balance upon successful registration
- **Refundable** if you withdraw from API usage within the first 60 days
- All accounts subject to standard Customer Commission

---

## Authentication

### Session-Based Authentication

The API uses a session-token based auth system:

1. **Login:** `POST /v3/sessions/` - Get a session token
2. **Authorize:** Send token as `Session-Token` in the `Authorization` header
3. **Verify MFA (if enabled):** `POST /v3/sessions/verify/`
4. **Logout:** `DELETE /v3/sessions/`

### Token Rotation: long sessions need the cookies (verified 2026-10-01)

Login returns a session token and a refresh token and sets them as cookies (`User-Session-Token`, `Refresh-Token`). Session tokens rotate on a ~20 minute cycle; a client that sends only the `Authorization` header is rejected with `401 AUTH_REQUIRED` at the first rotation, even while polling. To hold a session past 20 minutes, send both tokens with each request, `Cookie: User-Session-Token=<token>; Refresh-Token=<refresh_token>`, and adopt each renewed `User-Session-Token`. Verified live: header-only client died at 19m58s; cookie client survived past its 30 minute stop.

### Auth Header Format
```
Authorization: Session-Token <your_token>
```

### Security Scheme
- Type: API Key
- Header name: `Authorization`
- In: header

---

## API Endpoints Overview

### Sessions (Session Management)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /v3/sessions/ | Login to get a session token |
| DELETE | /v3/sessions/ | Logout / delete current session |
| POST | /v3/sessions/verify/ | Verify MFA during login |

### Accounts (Account Information)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /v3/accounts/ | Retrieve account info (balance, exposure, currency, etc.) |
| GET | /v3/accounts/activity/ | Account activity for reconciliation (query params: timestamp_max, offset, limit) |

### Events (Available Events)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /v3/events/ | Retrieve available events to bet on |
| GET | /v3/events/{event_ids}/states/ | Get current states for events by ID |

### Competitors
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /v3/events/{event_ids}/competitors/ | Get competitors for a set of events |

### Markets
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /v3/events/{event_ids}/markets/ | Get markets by event IDs (after getting events) |
| GET | /v3/events/{event_ids}/markets_count/ | Get market counts by event IDs |

### Contracts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /v3/markets/{market_ids}/contracts/ | Get contracts by market IDs |

### Volumes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /v3/markets/{market_ids}/volumes/ | Get traded volumes by market IDs |

### Prices
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /v3/markets/{market_ids}/last_executed_prices/ | Get last executed price + timestamp for each contract |
| GET | /v3/markets/{market_ids}/quotes/ | Get current prices/quotes from the exchange |

### Currencies
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /v3/currencies/{code}/ | Get conversion rate for a specific currency |

### Orders (Placing & Managing Bets)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /v3/orders/ | Place orders on the exchange |
| GET | /v3/orders/ | Retrieve current orders (open + recently settled) |
| DELETE | /v3/orders/ | Cancel ALL orders |
| DELETE | /v3/orders/{order_id}/ | Cancel a specific order |
| GET | /v3/orders/fullcover/ | Get all fullcover orders for an account |

### Account Activity (CSV Statement)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /v3/account_activity_csv/{start_datetime}/{end_datetime}/ | Get gzipped CSV of account activity. Start/end must be on the hour, separated by exactly 1 hour. |

---

## Rate Limits & Fair Usage

### Key Rules
- Smarkets pre-approves call limits per period
- Exceeding limits leads to **temporary suspension**
- Repeated violations can result in **permanent API or account access revocation**
- Smarkets is not liable for losses from restricted API access
- They reserve the right to withdraw API access at any time without notice

### Prohibited Activities
- Using the API outside the scope of the agreement
- Interfering with or disrupting API features
- Using the API strictly for data extraction without commensurate trading volumes
- Selling, renting, or redistributing API data without written consent
- Monitoring or benchmarking services for competitive purposes
- Transmitting material that could harm software, hardware, or networks
- Circumventing rate limits to the detriment of others

### Fair Usage Policy (Section 6)
6.1 All API, data, documentation, and materials accessed via smarkets.com are governed by this policy. By connecting, you agree to adhere to access, call, and usage limits. Circumvention may result in temporary or permanent restriction.

---

## Common Errors

### Error Response Format
All errors return JSON with:
```json
{
  "error_type": "ERROR_TYPE_CODE",
  "data": {} // error-specific payload
}
```

### Error Types
| Error Type | HTTP Status | Description |
|------------|-------------|-------------|
| INTERNAL_ERROR | 500 | Server-side failure |
| RATE_LIMIT_EXCEEDED | 429 | Rate limit hit (includes `count`, `limit`, `expiry` in data) |
| REQUEST_VALIDATION_ERROR | 400 | Invalid request parameters |
| AUTH_REQUIRED | 401 | Missing or invalid authentication |
| FORBIDDEN | 403 | Insufficient permissions |
| INVALID_DATETIMES | 400 | Bad datetime format (account activity CSV) |
| NO_CSV_AVAILABLE | 404 | CSV not available for given time range |
| NO_RESULTS_FOUND | 404 | Event states query returned no results |
| BAD_REQUEST | 400 | Badly formed request parameters (markets/prices endpoints) |
| REQUEST_TOO_LARGE | 414 | Too many IDs in a single request |
| RECKONATOR_REQUEST_TOO_LARGE | 400 | Account activity query too broad |
| COUNTRY_BLOCKED | 451 | Account or IP jurisdiction not supported |

### RateLimitError Data Schema
```json
{
  "error_type": "RATE_LIMIT_EXCEEDED",
  "data": {
    "count": <number>,     // current request count
    "limit": <number>,     // your rate limit
    "expiry": <string>     // when the limit resets
  }
}
```

---

## Terms & Conditions Summary

### Section 1 - API Usage
- API enables authorised users to access the exchange directly
- Automated interactions only after completing request form + receiving approval
- Smarkets retains full discretion to refuse API access at any time
- Customer T&Cs and Betting Rules also apply

### Section 2 - Authorisation
- API is for viewing market prices and placing bets ONLY
- **Strictly prohibited:** odds scraping, concealing API calls, browser impersonation, reverse engineering
- Violations can result in: API removal, bet cancellation, account suspension/closure, legal action
- All customers undergo a compliance review within the first 60 days

### Section 3 - Setup Fee & Commission
- GBP150 one-time fee (refundable within 60 days)
- Standard Customer Commission applies
- API customers ineligible for affiliate/0% commission offers

### Section 4 - Ongoing Requirements
- Must provide details of technical setup and API interaction plans
- Must keep Smarkets updated of any changes to technical setup

### Section 5 - Restrictions
- Usage restricted to pre-approved events and markets
- No sharing/selling/distributing platform data (prices, market status, events)
- No benchmarking of markets, prices, liquidity, or systems
- Call limits pre-approved per period
- Smarkets can withdraw access at any time without notice

### Section 6 - Fair Usage
- Governs all API, data, documentation, materials
- Must adhere to access, call, and usage limits
- Circumvention = temporary or permanent restriction

---

## Support Contact

- **API Technical Support:** api@smarkets.com
- **General Support:** support@smarkets.com
- **Document Upload Portal:** https://docs.smarkets.com/
- **API Request Form:** https://support.smarkets.com/p/6MLL-PL7/api-request-form
- **Help Centre:** https://help.smarkets.com/hc/en-gb
