# 🏢 Smarkets API Support — Agent Knowledge Base

**Status:** ✅ Live | **Owner:** API Support Team | **Last reviewed:** May 2026 | **Labels:** `api-support` `triage` `training` `external-facing`

> **How to use this page:** A customer reports an API issue. Ctrl+F what they're saying (e.g. "401", "token expired", "order rejected", "rate limit") to jump to the relevant section. If nothing matches, escalate to tech support.

---

## 📋 Table of Contents

- [🔍 Quick-Find Index](#quick-find-index)
- [🧠 How API Calls Work](#how-api-calls-work)
- [🔐 401 — Login / Token Issues](#401--login--token-issues-not-logged-in)
- [🚫 403 — Permission Problems](#403--permission-problems-not-allowed)
- [🔑 Login Errors (All Codes)](#login-errors-post-v3sessions)
- [⚠️ 400 — Bad Request / Wrong Data](#400--bad-request--wrong-data)
- [🔎 404 — Not Found / Missing Data](#404--not-found--missing-data)
- [📦 414 — Request Too Large](#414--request-too-large)
- [⏱️ 429 — Too Many Requests](#429--too-many-requests)
- [🌍 451 — Country Blocked](#451--country-blocked)
- [🔴 500, 503 & 504 — Smarkets Server Issues](#500-503--504--smarkets-server-issues)
- [📝 Order Rejection Codes (POST /v3/orders/)](#order-rejection-codes-post-v3orders)
- [🗑️ Cancel-Order Rejection Codes (DELETE /v3/orders/{id}/)](#cancel-order-rejection-codes-delete-v3ordersorder_id)
- [📊 Quick Reference Table](#quick-reference-table)
- [❓ Frequently Asked Questions](#frequently-asked-questions)
- [🚨 When to Flag for Technical Support](#when-to-flag-for-technical-support)

---

## 🔍 Quick-Find Index

{info:title=How to use this index}
If a customer says any of these exact phrases, Ctrl+F the phrase here to find the right section.
{info}

| If the customer says... | Jump to section |
|---|---|
| "I'm getting a 401" / "My token isn't working" / "It says AUTH_REQUIRED" | [401 — Login / token issues](#401--login--token-issues-not-logged-in) |
| "I keep getting logged out" / "My session expired" | [401 — Login / token issues](#401--login--token-issues-not-logged-in) |
| "I'm getting a 403" / "It says FORBIDDEN" | [403 — Permission problems](#403--permission-problems-not-allowed) |
| "I was working fine and now I'm blocked" | [403 — Permission problems](#403--permission-problems-not-allowed) |
| "I can't login at all" / "My password isn't working" / "INVALID_CREDENTIALS" | [Login errors (all codes)](#login-errors-post-v3sessions) |
| "It says COUNTRY_BLOCKED" / "I'm in the wrong country?" | [451 — Country blocked](#451--country-blocked) |
| "I can't place bets" / "My order was rejected" / "ORDER_REJECTED" | [Order rejection codes (POST /v3/orders/)](#order-rejection-codes-post-v3orders) |
| "I can't cancel my order" / "ORDER_CANCEL_REJECTED" | [Cancel-order rejection codes (DELETE /v3/orders/{id}/)](#cancel-order-rejection-codes-delete-v3ordersorder_id) |
| "I'm getting a 400" / "It says REQUEST_VALIDATION_ERROR" | [400 — Bad request / wrong data](#400--bad-request--wrong-data) |
| "The CSV export isn't working" / "INVALID_DATETIMES" | [400 — Bad request / wrong data](#400--bad-request--wrong-data) |
| "I'm getting 404" / "It says NO_CSV_AVAILABLE" | [404 — Not found / missing data](#404--not-found--missing-data) |
| "The event I'm looking for doesn't appear" | [404 — Not found / missing data](#404--not-found--missing-data) |
| "It says NO_RESULTS_FOUND" | [404 — Not found / missing data](#404--not-found--missing-data) |
| "It says REQUEST_TOO_LARGE" / "I sent many IDs" | [414 — Request too large](#414--request-too-large) |
| "I'm getting 429 errors" / "I've been rate limited" | [429 — Too many requests](#429--too-many-requests) |
| "I keep hitting my rate limit" / "RATE_LIMIT_EXCEEDED" | [429 — Too many requests](#429--too-many-requests) |
| "I'm getting a 500" / "Internal server error" | [500, 503, 504 — Smarkets server issues](#500-503--504--smarkets-server-issues) |
| "It says 503" / "Service unavailable" | [500, 503, 504 — Smarkets server issues](#500-503--504--smarkets-server-issues) |
| "It says 504" / "Gateway timeout" | [500, 503, 504 — Smarkets server issues](#500-503--504--smarkets-server-issues) |
| "It says ZEUS_TIMEOUT" | [500, 503, 504 — Smarkets server issues](#500-503--504--smarkets-server-issues) |
| "My account is suspended" | [403 — Permission problems](#403--permission-problems-not-allowed) |
| "How do I get API access?" / "The GBP150 fee" | [Frequently asked questions](#frequently-asked-questions) |
| "Can I get 0% commission?" | [Frequently asked questions](#frequently-asked-questions) |
| "Am I allowed to scrape data?" | [Frequently asked questions](#frequently-asked-questions) |
| "I already tried waiting and it still doesn't work" | [When to flag for technical support](#when-to-flag-for-technical-support) |
| "This doesn't match anything on this page" | [When to flag for technical support](#when-to-flag-for-technical-support) |

---

## 🧠 How API Calls Work

A customer's application sends a request to `https://api.smarkets.com`. Smarkets responds with a **three-digit status code** that tells you whether the request succeeded or what went wrong.

| Code range | What it means | Whose problem is it? |
|---|---|---|
| **2xx** (200, 201, 204) | ✅ The request succeeded | No problem |
| **4xx** (400, 401, 403, 404, 414, 429, 451) | ❌ The customer's request had a problem | **Customer** — guide them to fix it |
| **5xx** (500, 503, 504) | ❌ Smarkets' systems had a problem | **Smarkets** — log and escalate |

Your role is to identify which problem the customer has encountered and provide the appropriate guidance. If the issue falls outside the patterns below, flag it for technical support.

---

## 🔐 401 — Login / Token Issues ("Not logged in")

{info:title=Common customer complaints — Ctrl+F these phrases}
"I'm getting a 401 error" / "My token isn't working" / "It says AUTH_REQUIRED" / "I keep getting logged out" / "My session expired" / "I was working and suddenly it stopped"
{info}

**What it means:** The customer's session token is missing, expired, or invalid.

{tip}
**How it works (simple explanation):** Using the Smarkets API requires a "session token" — like a ticket you get when you log in. Every request must present this ticket. The ticket is "valid for 30min, but if you make an authenticated request with it, it will be renewed for the next 30min." If the customer doesn't use the API for 30 minutes, the ticket expires and they need to log in again.
{tip}

**Things to check (in order):**

1. **Has the token expired?** — Tokens last 30 minutes without activity. They need to log in again via `POST /v3/sessions/` to get a fresh token.

2. **Is the header formatted correctly?** — The token must be sent in the `Authorization` header exactly like this:
   `Authorization: Session-Token <their_token>`

3. **Is two-factor authentication (MFA) enabled?** — After logging in, MFA requires an extra step: `POST /v3/sessions/verify/` with their TOTP code. Without this, the token is not fully authorised.

4. **Did they switch from paper trading to live trading (or vice versa)?** — Switching environments invalidates existing tokens. They need a fresh token from the new environment.

**What to tell the customer:**
> Your session token has expired. Tokens are valid for 30 minutes without activity. To resolve this, log in again via `POST /v3/sessions/` with your email and password to receive a fresh token. Once obtained, include it in the `Authorization` header using the format `Authorization: Session-Token <your_token>` for all subsequent requests.
> 
> Note that login is rate-limited to 5 attempts every 5 minutes — if you receive a 429 during login, you must wait before trying again.

**When to flag for technical support:**
- 401 on POST requests but GET requests work fine (possible mixed authentication methods)
- The customer mentions "cookies", "auth v2", or "refresh tokens" (newer authentication schemes not covered here)
- The error response contains `data: None` (no further detail to identify the problem)
- The customer is getting 401 from the logout endpoint (`DELETE /v3/sessions/`) — this shouldn't happen normally

---

## 🚫 403 — Permission Problems ("Not allowed")

{info:title=Common customer complaints — Ctrl+F these phrases}
"I'm getting a 403 error" / "It says FORBIDDEN" / "I was working fine and now I'm blocked" / "My account can't do this" / "It says ACCOUNT_UNVERIFIED" / "It says RG_ACK_REQUIRED" / "It says KYC_PERMISSION_DENIED" / "My account is suspended"
{info}

**What it means:** The customer's account lacks permission for the requested action.

{warning:title=🚨 Critical distinction}
**There are two types of 403. The response body tells you which one.** If the response is **JSON**, it's an API permission issue. If the response is **HTML**, it's a Cloudflare network block. These have totally different fixes.
{warning}

---

### Type A: API-level 403 (response is JSON)

The response starts with `{"error_type": "FORBIDDEN", ...}`. This means the account itself is blocked from this action.

| Reason | What's going on |
|---|---|
| **Not approved for API access yet** | They need to submit the [API Request Form](https://support.smarkets.com/p/6MLL-PL7/api-request-form) and pay the GBP150 fee |
| **Under 60-day compliance review** | "All customers will be subject to a compliance review of their account within the first 60 days." This is normal — wait for it to pass |
| **Access suspended or revoked** | They may have violated terms (scraping, sharing data, etc.) |
| **Endpoint-specific 403s** | See table below |

**Endpoint-specific 403 error codes (POST /v3/orders/):**

| Code | Meaning |
|---|---|
| `ACCOUNT_UNVERIFIED` | Registration incomplete |
| `NO_DEPOSITS` | No money deposited |
| `KYC_PERMISSION_DENIED` | Identity not verified |
| `ACTION_BLOCKED` | Specific action blocked |
| `RG_ACK_REQUIRED` | Responsible gambling acknowledgement not completed |

**What to tell the customer:**
> This means your account does not have permission for that action. If you are within your first 60 days of API access, this is expected — your account is undergoing compliance review. If the issue persists beyond that period, contact api@smarkets.com to check your access status.

---

### Type B: Cloudflare network block (response is HTML)

{error:title=Not an API issue — escalate to technical team}
**Response starts with `<!DOCTYPE` or mentions "Cloudflare".** This is a network-level block at the edge, not an API authentication issue.
{error}

**What to tell the customer:**
> This is a network-level block from Cloudflare, not an issue with your API credentials. It commonly affects requests from VPS, server, or data centre IP addresses. Smarkets does not offer IP whitelisting. Please contact our support team for assistance with this type of block.

---

## 🔑 Login Errors (POST /v3/sessions/)

{info:title=Common customer complaints — Ctrl+F these phrases}
"I can't log in" / "It says INVALID_CREDENTIALS" / "My password isn't working" / "It says DEVICE_NOT_TRUSTED" / "It says SESSION_LIMIT_REACHED" / "It says COUNTRY_BLOCKED" / "I keep getting locked out"
{info}

**What it means:** Something is preventing the customer from completing the login process.

{tip}
**Quick tip:** Login is rate-limited to **5 attempts per 300 seconds (5 minutes)**. If they try too many times, they'll get a 429 and must wait.
{tip}

**All login error codes — copy and Ctrl+F on this table:**

| Search for this code | HTTP | What it really means | What to tell them |
|---|---|---|---|
| `INVALID_CREDENTIALS` | 401 | Email/username or password is wrong | Reset password on smarkets.com |
| `PASSWORD_RESET_NEEDED` | 401 | The password must be reset before logging in | Reset password on smarkets.com |
| `INVALID_DEVICE_COOKIE` | 400 | Missing or broken device identifier | Ensure the request includes the device cookie |
| `INVALID_TOKEN` | 400 | Wrong TOTP code during MFA verification | Generate a new TOTP code and try again |
| `DEVICE_NOT_TRUSTED` | 403 | This device hasn't been marked as trusted | Complete device trust verification on smarkets.com |
| `USER_SUSPENDED` | 403 | Account has been suspended by Smarkets | Contact support@smarkets.com |
| `USER_SELF_SUSPENDED` | 403 | The customer put their own account on timeout | Wait for the timeout period to end |
| `USER_ON_TIMEOUT` | 403 | Too many failed login attempts — cooling off | Wait before trying again |
| `USER_EXCLUDED` | 403 | Account is self-excluded (responsible gambling) | Contact support for exclusion management |
| `SESSION_LIMIT_REACHED` | 403 | Too many active sessions already open | Log out from other sessions first |
| `IP_NOT_TRUSTED` | 403 | The IP address is not recognised | Complete device trust verification |
| `SOURCE_BLOCKED` | 403 | The traffic source is blocked | Contact support@smarkets.com |
| `CLIENT_JURISDICTION_MISMATCH` | 403 | Account country doesn't match the IP address | Contact support@smarkets.com |
| `COUNTRY_BLOCKED` | 451 | Smarkets not available in this country | No resolution available |

---

## ⚠️ 400 — Bad Request / Wrong Data

{info:title=Common customer complaints — Ctrl+F these phrases}
"I'm getting a 400 error" / "It says REQUEST_VALIDATION_ERROR" / "The CSV export is failing" / "It says INVALID_DATETIMES" / "It says BAD_REQUEST" / "My order won't go through"
{info}

**What it means:** The data the customer sent is wrong — incorrect format, missing fields, or malformed parameters.

{tip}
**How it works:** Validation errors always return a JSON body with `"error_type": "REQUEST_VALIDATION_ERROR"` and a `data` field explaining exactly what's wrong. **Read the `data` field — it tells you precisely what to fix.**
{tip}

**Common 400 error codes:**

| Search for this code | What it means | Fix |
|---|---|---|
| `INVALID_DATETIMES` | CSV start/end times are wrong | Start and end "have to be separated by an hour, also these have to be exactly on the hour" (e.g. 2:00 PM to 3:00 PM) |
| `BAD_REQUEST` | Parameters are badly formed (markets/prices endpoints) | Check the parameter format |
| `REQUEST_VALIDATION_ERROR` | Something is wrong with the request | Read the `data` field — it tells you what to fix |
| `RECKONATOR_REQUEST_TOO_LARGE` | Account activity query is too broad | Narrow the date range or reduce filters |

**What to tell the customer:**
> The API rejected your request because something in the data was incorrect. The `data` field in the error response will tell you precisely what is wrong.
> 
> Common causes:
> - **Account activity CSV:** the start and end times must be exactly on the hour (e.g. 2:00 PM to 3:00 PM) and exactly one hour apart
> - **Placing an order:** required fields such as `price`, `quantity`, `contract_id`, or `side` may be missing
> - **IDs:** event, market, and contract IDs must be in the correct format (numeric strings)
> - **Too many IDs in one request:** split the request into smaller batches (the API returns 414 REQUEST_TOO_LARGE when you exceed the limit)
> - **Account activity request too large:** narrow your date range
> 
> Check the error message carefully — it describes exactly what needs to be corrected.

**When to flag for technical support:**
- The `data` field in the error response is empty or unclear
- You cannot determine which parameter is invalid from the error message
- The customer asks for specific valid values for `price` or `quantity` (these require exchange tick knowledge)
- Invalid price, invalid quantity, or other specialist order rejection codes (see [Order Rejection section](#order-rejection-codes-post-v3orders))

---

## 🔎 404 — Not Found / Missing Data

{info:title=Common customer complaints — Ctrl+F these phrases}
"I'm getting a 404" / "The CSV export is empty" / "The event I'm looking for doesn't appear" / "It says NO_CSV_AVAILABLE" / "It says NO_RESULTS_FOUND" / "I can't find this order" / "ORDER_CANCEL_REJECTED_NOT_FOUND"
{info}

**What it means:** The resource the customer is requesting does not exist.

**Common 404 scenarios:**

| Search for this code | What happened | Fix |
|---|---|---|
| (generic 404) | Wrong ID — event, market, contract, or order doesn't exist | Verify the ID |
| `NO_CSV_AVAILABLE` | No activity data for the requested time range | Try a different date range |
| `NO_RESULTS_FOUND` | No events matched the query parameters | Adjust the search criteria |
| `ORDER_CANCEL_REJECTED_NOT_FOUND` | The order may have been filled and no longer exists | Verify the order ID via `GET /v3/orders/` |

**What to tell the customer:**
> The API cannot find what you are looking for. This usually means one of the following:
> - The event, market, contract, or order ID you are using is incorrect or doesn't exist
> - For the account activity CSV: no activity data exists for the time range you specified (you will receive a `NO_CSV_AVAILABLE` error)
> - For event states: no events match your criteria (you will receive a `NO_RESULTS_FOUND` error)
> - For cancelling an order: the order may have already been filled or doesn't exist
> 
> Verify your IDs by cross-referencing them against responses from the `/v3/events/` or `/v3/accounts/` endpoints.

**When to flag for technical support:**
- The customer insists their IDs are correct but continues receiving 404 responses
- The endpoint itself appears to be incorrect (the customer may have the wrong URL)
- The customer needs guidance navigating Smarkets' event hierarchy to locate the correct IDs

---

## 📦 414 — Request Too Large

{info:title=Common customer complaints — Ctrl+F these phrases}
"I'm getting a 414 error" / "It says REQUEST_TOO_LARGE" / "My events query stopped working" / "I sent many IDs at once"
{info}

**What it means:** The customer sent too many IDs in a single request. The API has limits on how many IDs it will accept at once.

**Which endpoints this affects:** Events, markets, contracts, and account activity endpoints that accept arrays of IDs.

**What to tell the customer:**
> The API rejected your request because it contained too many IDs. You need to split your request into smaller batches. Try reducing the number of IDs you send at once and send multiple separate requests instead.

**When to flag for technical support:**
- The customer is unsure what the ID limit is per request
- The customer needs to process a very large number of IDs efficiently

---

## ⏱️ 429 — Too Many Requests

{info:title=Common customer complaints — Ctrl+F these phrases}
"I'm getting 429 errors" / "I've been rate limited" / "It says RATE_LIMIT_EXCEEDED" / "I can't log in — too many attempts" / "I keep hitting my limit"
{info}

**What it means:** The customer has exceeded their pre-approved rate limit. They need to wait before making more requests.

{tip}
**The error response includes three useful fields:**
- `count` — how many requests they've already made
- `limit` — their approved maximum
- `expiry` — ISO timestamp of when the limit resets
{tip}

**Known per-endpoint rate limits:**

| Endpoint | Limit |
|---|---|
| Quotes (`GET /v3/markets/{ids}/quotes/`) | 50 requests per 60 seconds |
| Login (`POST /v3/sessions/`) | 5 requests per 300 seconds (5 minutes) |
| Cancel all orders (`DELETE /v3/orders/`) | 1 request per 60 seconds |
| Cancel one order (`DELETE /v3/orders/{id}/`) | 10 requests per second |
| Logout (`DELETE /v3/sessions/`) | 30 requests per 60 seconds |

{warning}
Per Section 5 of the API terms: "exceeding them may lead to temporary suspension" and "repeated violations could result in API or account access being permanently revoked."
{warning}

**What to tell the customer:**
> You have exceeded your pre-approved rate limit. The error response includes an `expiry` timestamp showing when the limit resets — you must wait until that time before making further requests.
> 
> To reduce how often you hit the limit:
> - Cache price data instead of polling the quotes endpoint repeatedly
> - Batch multiple IDs into a single request where the API supports it
> - Consider using the WebSocket feed for real-time data rather than HTTP polling
> - Note that login is limited to 5 attempts every 5 minutes
> 
> If your use case genuinely requires higher limits, contact api@smarkets.com to discuss.

**When to flag for technical support:**
- The customer is hitting limits despite very low apparent usage (possible multiple clients sharing the same account)
- The customer's account has been suspended due to repeated rate limit violations
- The customer needs assistance setting up WebSocket feeds
- The customer mentions Cloudflare-based rate limiting rather than API rate limiting

---

## 🌍 451 — Country Blocked

{info:title=Common customer complaints — Ctrl+F these phrases}
"I'm getting a 451 error" / "It says COUNTRY_BLOCKED" / "I can't access the API from my location" / "I'm travelling and it stopped working"
{info}

**What it means:** Smarkets does not offer services in the customer's country or the country their IP address is coming from.

**What to tell the customer:**
> Your location or account jurisdiction is not supported by Smarkets. This is a geographic restriction and is not related to your credentials or API setup. If you believe this is an error, contact support@smarkets.com to discuss.

**When to flag for technical support:**
- The customer is located in a normally supported country but is receiving this error (possible mismatched account jurisdiction)
- The customer wishes to discuss jurisdiction restrictions

---

## 🔴 500, 503 & 504 — Smarkets Server Issues

{info:title=Common customer complaints — Ctrl+F these phrases}
"I'm getting 500 errors" / "Internal server error" / "Service unavailable" / "Gateway timeout" / "It says ZEUS_TIMEOUT" / "It says KYC_SERVICE_UNAVAILABLE" / "It says EVENTS_UNAVAILABLE"
{info}

**What it means:** Something went wrong on Smarkets' side. This is **not caused by the customer**. Nothing they do differently will fix it.

{error:title=Cause is on Smarkets side — do not blame the customer}
500 = Smarkets system crashed. 503 = Specific subsystem is down. 504 = Backend timed out. All are server-side issues. Tell the customer to wait and retry, then escalate to api@smarkets.com if it persists.
{error}

**The three types:**

| HTTP | Name | Meaning |
|---|---|---|
| 500 | Internal Server Error | A Smarkets system crashed. Retry in a few minutes. |
| 503 | Service Unavailable | A specific Smarkets system is down. The error code tells you which one (see table below). |
| 504 | Gateway Timeout | A Smarkets backend system didn't respond in time. |

**503 error codes — which system is affected:**

| Search for this code | System affected |
|---|---|
| `KYC_SERVICE_UNAVAILABLE`, `KYC_SERVICE_INTERNAL_ERROR` | KYC verification system (order placement) |
| `AUTH_UNAVAILABLE` | Authentication system (login, orders) |
| `ORDER_UNAVAILABLE` | Order processing system |
| `CREATE_ORDER_TIMEOUT`, `CANCEL_ORDER_TIMEOUT`, `CANCEL_ALL_TIMEOUT` | Order processing — timed out |
| `CANCEL_ALL_UNAVAILABLE` | Cancel-all orders system |
| `EVENTS_UNAVAILABLE`, `EVENTS_INTERNAL_ERROR`, `EVENTS_API_RATE_LIMIT` | Events/markets data system |
| `CHARTS_INTERNAL_ERROR`, `CHARTS_UNAVAILABLE` | Price charts system |
| `MDS_SERVICE_UNAVAILABLE` | Market data service (prices, volumes) |
| `FOREX_SERVICE_UNAVAILABLE`, `FOREX_SERVICE_INTERNAL_ERROR` | Currency conversion system |
| `RECKONATOR_UNAVAILABLE` | Account activity/reconciliation system |
| `PROMOTION_SERVICE_UNAVAILABLE` | Promotions system (order retrieval) |
| `ZEUS_UNAVAILABLE`, `ZEUS_CONNECTION_ERROR` | Core trading engine (order retrieval) |

**What to tell the customer:**
> This is a server-side issue, not a problem with your request. A 500 means a temporary system failure. 503 and 504 errors mean a specific Smarkets system is temporarily unavailable or timing out.
> 
> Please wait a few minutes and try again. If the issue persists, report it to api@smarkets.com with the full error details, including the specific error code — this helps the engineering team identify the affected system.

**When to flag for technical support:**
- Always flag 500, 503, and 504 errors — they are server-side and should be reported to api@smarkets.com
- Note the specific error code — it helps identify which system is affected
- If the customer says "I tried waiting and it still happens" — this confirms a real outage, escalate

---

## 📝 Order Rejection Codes (POST /v3/orders/)

{info:title=Common customer complaints — Ctrl+F these phrases}
"My order was rejected" / "I can't place a bet" / "It says ORDER_REJECTED_INSUFFICIENT_FUNDS" / "It says ORDER_INVALID_INVALID_PRICE" / "It says KYC_PERMISSION_DENIED"
{info}

**What it means:** The API refused to place an order. Each rejection has a specific code that tells you exactly why.

{tip}
**The code itself tells you what's wrong — no interpretation needed.** Ask the customer for the exact error code from the response.
{tip}

---

### 💰 Group 1: Money and limits

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_INSUFFICIENT_FUNDS` | Not enough money in the account | Check available balance via `GET /v3/accounts/`. Open orders also consume balance through exposure |
| `ORDER_REJECTED_STAKE_LIMIT_EXCEEDED` | Bet is too large for the account's limit | Reduce the stake or contact support to adjust limits |
| `ORDER_REJECTED_LIMIT_EXCEEDED` | Too many open orders already | Cancel some existing orders before placing new ones |
| `NO_DEPOSITS` | No money has ever been deposited | Make a deposit first |

---

### 📊 Group 2: Market state

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_MARKET_SETTLED` | The market has already finished | Bets can no longer be placed — the event has concluded |
| `ORDER_REJECTED_CONTRACT_SETTLED` | That specific betting option has settled | Choose a different contract within the same market |
| `ORDER_REJECTED_MARKET_NOT_OPEN` | The market isn't accepting bets yet | Wait until the market opens |
| `ORDER_REJECTED_MARKET_HALTED` | Trading was paused (e.g. during in-play delay) | Wait for the market to resume |
| `ORDER_REJECTED_TRADING_SUSPENDED` | Trading is temporarily suspended | Wait for trading to resume |
| `ORDER_CANCELLED_MARKET_HALTED` | Order was cancelled because the market was halted | Wait and re-submit |
| `ORDER_CANCELLED_TRADING_SUSPENDED` | Order was cancelled because trading was suspended | Wait and re-submit |

---

### 🔢 Group 3: Wrong values

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_INVALID_INVALID_PRICE` | The price is not a valid tick on the exchange | Price must be in percentage basis points. Example: 5000 = 50%. To convert to decimal odds, divide 10000 by it. Example: 10000 / 5000 = 2.0 |
| `ORDER_INVALID_INVALID_QUANTITY` | The stake amount is not valid | Minimum is 500 (= 0.05 GBP). The units are 1/10000 of one unit of the user's currency |

---

### 🔄 Group 4: Conflicts and throttling

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_CROSSED_SELF` | They're trying to match their own opposing order | Adjust the price so it doesn't conflict with their own existing orders |
| `ORDER_REJECTED_THROTTLE_EXCEEDED` | Placing orders too fast | Slow down — wait a bit before the next order |

---

### 🔍 Group 5: Not found

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_MARKET_NOT_FOUND` | That market ID doesn't exist | Verify the market ID |
| `ORDER_REJECTED_CONTRACT_NOT_FOUND` | That contract ID doesn't exist | Verify the contract ID |

---

### 👤 Group 6: Account issues

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_ACCOUNT_SUSPENDED` | Account is suspended | Contact support@smarkets.com |
| `KYC_PERMISSION_DENIED` | Identity verification not completed | Verify their identity on smarkets.com |
| `ACCOUNT_UNVERIFIED` | Account registration incomplete | Complete registration and verification |
| `RG_ACK_REQUIRED` | Responsible gambling acknowledgement needed | Complete the RG acknowledgement on smarkets.com |
| `ACTION_BLOCKED` | A specific action was blocked | Contact support@smarkets.com |
| `COUNTRY_BLOCKED` (returns as 451) | Country region is restricted | Smarkets not available in this region |

---

### 📏 Group 7: Market capacity

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_CAPACITY_REACHED` | Maximum orders reached for this market | Try a different market or wait |
| `ORDER_CANCELLED_INSUFFICIENT_LIQUIDITY` | Not enough other people betting to fill the order | Reduce the quantity or adjust the price |

---

### ⚙️ Group 8: System issues

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_SERVICE_TEMPORARILY_UNAVAILABLE` | Smarkets system is temporarily down | Wait and retry — server-side issue |
| `ORDER_CANCELLED_MEMBER_REQUESTED` | Order was cancelled by the customer themselves | This is informational — the cancellation was intentional |
| `ORDER_CANCELLED_ADMIN_REQUESTED` | Order was cancelled by Smarkets admin | If unexpected, contact api@smarkets.com |

---

## 🗑️ Cancel-Order Rejection Codes (DELETE /v3/orders/{order_id}/)

{info:title=Common customer complaints — Ctrl+F these phrases}
"I can't cancel my order" / "It says ORDER_CANCEL_REJECTED" / "The delete order endpoint isn't working" / "It says ORDER_CANCEL_REJECTED_NOT_FOUND" / "It says ORDER_CANCEL_REJECTED_TOO_LATE"
{info}

**What it means:** The API refused to cancel an order. These are **different** from the order-placing rejection codes above.

{tip}
**Note:** Cancel-all (`DELETE /v3/orders/`) has a rate limit of **1 request per 60 seconds**. Single cancellation (`DELETE /v3/orders/{id}/`) has a limit of **10 requests per second**.
{tip}

| Search for this code | HTTP | What it means | What to tell them |
|---|---|---|---|
| `ORDER_CANCEL_REJECTED_NOT_FOUND` | 404 | The order ID doesn't exist | Verify the order ID via `GET /v3/orders/` |
| `ORDER_CANCEL_REJECTED_NOT_LIVE` | 400 | The order is already filled or cancelled | No action needed — it's already resolved |
| `ORDER_CANCEL_REJECTED_TOO_LATE` | 400 | The market has already settled | Orders can't be reversed after settlement |
| `ORDER_CANCEL_REJECTED_INSUFFICIENT_FUNDS` | 400 | Not enough funds to process the cancellation | Rare — contact api@smarkets.com |
| `ORDER_CANCEL_REJECTED_TRADING_SUSPENDED` | 400 | Trading is suspended | Wait for trading to resume |
| `ORDER_CANCEL_REJECTED_ACCOUNT_SUSPENDED` | 400 | Account is suspended | Contact support@smarkets.com |
| `ORDER_CANCEL_REJECTED_MARKET_NOT_FOUND` | 400 | The market for this order doesn't exist | Verify the order and market IDs |
| `ORDER_CANCEL_REJECTED_THROTTLE_EXCEEDED` | 400 | Too many cancellation attempts | Wait — limit is 10 cancellations per second |
| `ORDER_CANCEL_REJECTED_STAKE_LIMIT_EXCEEDED` | 400 | Account stake limit issue | Contact support |
| `ORDER_CANCEL_REJECTED_CAPACITY_REACHED` | 400 | Market at max cancellation capacity | Try again shortly |
| `ORDER_CANCEL_REJECTED_LIMIT_EXCEEDED` | 400 | Hit the cancellation limit for this period | Wait for the limit to reset |
| `ORDER_CANCEL_REJECTED_INVALID_QUANTITY` | 400 | Invalid partial cancellation amount | Verify the quantity parameter |
| `ORDER_CANCEL_REJECTED_SERVICE_TEMPORARILY_UNAVAILABLE` | 400 | Smarkets system temporarily down | Wait and retry — server-side issue |

---

## 📊 Quick Reference Table

| HTTP | Plain English | What to do | Search for this error code |
|---|---|---|---|
| 400 | Customer sent wrong data | Read the `data` field in the error — it says what's wrong | REQUEST_VALIDATION_ERROR, INVALID_DATETIMES, BAD_REQUEST, RECKONATOR_REQUEST_TOO_LARGE |
| 401 | Not logged in / token expired | Get a fresh token via `POST /v3/sessions/` | AUTH_REQUIRED |
| 403 (JSON) | No permission — account-level | Check API approval, compliance review, or suspension | FORBIDDEN, KYC_PERMISSION_DENIED, ACCOUNT_UNVERIFIED, NO_DEPOSITS, RG_ACK_REQUIRED, ACTION_BLOCKED |
| 403 (HTML) | Cloudflare network block | **Not an API issue** — flag for technical support | Response starts with `<!DOCTYPE` |
| 404 | Data doesn't exist | Verify IDs or check time ranges | NO_CSV_AVAILABLE, NO_RESULTS_FOUND, ORDER_CANCEL_REJECTED_NOT_FOUND |
| 414 | Too many IDs in one request | Split into smaller batches | REQUEST_TOO_LARGE |
| 429 | Hit rate limit — too fast | Wait until the `expiry` time in the error | RATE_LIMIT_EXCEEDED |
| 451 | Country not supported | Geographic restriction — not a credentials issue | COUNTRY_BLOCKED |
| 500 | Smarkets crashed internally | Customer should wait and retry | INTERNAL_ERROR |
| 503 | Specific Smarkets system is down | Wait and retry; note the error code for engineering | KYC_SERVICE_UNAVAILABLE, EVENTS_UNAVAILABLE, ZEUS_UNAVAILABLE, etc. |
| 504 | Smarkets backend timed out | Wait and retry; flag if persistent | ZEUS_TIMEOUT, RECKONATOR_UNAVAILABLE |

---

## ❓ Frequently Asked Questions

### "How do I get API access?"

Submit the [API Request Form](https://support.smarkets.com/p/6MLL-PL7/api-request-form). After approval, a **GBP150 administration fee** is deducted from their account balance. Per Section 3: "Should you choose to permanently withdraw from API usage within the first 60 days, your setup fee will be refunded." All new API accounts undergo a **compliance review** during this 60-day period (Section 2).

### "Can I get the 0% commission?"

**No.** Per Section 3: "API customers are ineligible for any affiliate commission offers, as well as the 60 day 0% commission offer for new customers." Standard Customer Commission applies.

### "Am I allowed to scrape odds or market data?"

**No.** Per Section 2: "All other uses are strictly prohibited, including but not limited to, odds scraping, concealing API calls, browser impersonation or reverse engineering." Violations may result in API removal, bet cancellation, account suspension or closure, and legal action.

### "Can I share market data with a friend or third party?"

**No.** Per Section 5: "You may not share, sell or distribute platform data — such as prices, market status, events or business information — with third parties without written approval from Smarkets."

### "How do I cancel an order?"

Use `DELETE /v3/orders/{order_id}/` to cancel a specific order, or `DELETE /v3/orders/` to cancel **all** open orders.

| Action | Rate limit |
|---|---|
| Cancel one order | 10 requests per second |
| Cancel all orders | 1 request per 60 seconds |

### "How long does a session token last?"

Tokens are "valid for 30min, but if you make an authenticated request with it, it will be renewed for the next 30min." So as long as they use the API regularly, the token stays alive. Login is limited to **5 attempts every 5 minutes**.

### "What does a 504 error mean?"

A 504 Gateway Timeout means a Smarkets backend system didn't respond in time. Common codes: `ZEUS_TIMEOUT` (core trading engine timeout on order retrieval) and `RECKONATOR_UNAVAILABLE` (activity/reconciliation timeout). Retry after a short wait; escalate to api@smarkets.com if persistent.

### "Which API endpoints don't need a token?"

Events, competitors, contracts, and currencies can be accessed without authentication. Market data endpoints (quotes, prices) require authentication. Prices without a token will be delayed. Session endpoints (login, logout, MFA) also don't need prior authentication.

### "Who do I escalate to?"

| Issue | Contact |
|---|---|
| Technical API support | api@smarkets.com |
| General support / account issues | support@smarkets.com |
| Swagger documentation | docs.smarkets.com |
| Help centre | help.smarkets.com/hc/en-gb |

---

## 🚨 When to Flag for Technical Support

If you've read through this guide and can't find the answer, or if the customer's situation matches one of these, **pass it to technical support**:

| Situation | Why it's outside this guide |
|---|---|
| **Cloudflare/edge blocks** — response is HTML | Not an API issue — requires network investigation |
| **Account suspensions and compliance disputes** | Requires human judgement and sensitive handling |
| **"curl works but my code doesn't"** | Development/debugging issue — not API support |
| **WebSocket feed setup** | Separate system with different documentation |
| **Auth v2, refresh tokens, or cookies** | Newer authentication scheme not covered here |
| **Persistent 500, 503, or 504 errors** | Server-side — report to api@smarkets.com |
| **Customer shares raw request/response data you can't interpret** | Better to escalate than guess |
| **Anything that doesn't match a known pattern** | It's safer to escalate than provide wrong advice |

---

*Last updated: May 2026 | Owner: API Support Team | Source: help.smarkets.com, docs.smarkets.com, live OpenAPI v3 spec | Audit: Full cross-reference against live spec conducted May 2026*
