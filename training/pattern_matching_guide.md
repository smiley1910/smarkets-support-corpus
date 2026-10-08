# Smarkets API Support — Agent Knowledge Base

> A reference guide for support agents handling Smarkets API enquiries.
> No technical background required — match the customer's problem to the right section.
> **How to use: copy the customer's complaint and press Ctrl+F to find it here.**
> Compiled from the official Smarkets API documentation at help.smarkets.com and the live OpenAPI v3 specification at api.smarkets.com.

---

## Quick-Find Index

If a customer says any of these, Ctrl+F that phrase here:

| If the customer says... | Jump to section |
|---|---|
| "I'm getting a 401" / "My token isn't working" / "It says AUTH_REQUIRED" | [401 — Login / token issues](#401--login--token-issues-not-logged-in) |
| "I keep getting logged out" / "My session expired" | [401 — Login / token issues](#401--login--token-issues-not-logged-in) |
| "I'm getting a 403" / "It says FORBIDDEN" | [403 — Permission problems](#403--permission-problems-not-allowed) |
| "I was working fine before and now I'm blocked" | [403 — Permission problems](#403--permission-problems-not-allowed) |
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

## How API Calls Work

A customer's application sends a request to `https://api.smarkets.com`. Smarkets responds with a three-digit status code that tells you whether the request succeeded or what went wrong.

- **2xx codes** (200, 201, 204) — the request succeeded
- **4xx codes** (400, 401, 403, 404, 414, 429, 451) — the customer's request had a problem
- **5xx codes** (500, 503, 504) — Smarkets' systems had a problem

Your role is to identify which problem the customer has encountered and provide the appropriate guidance. If the issue falls outside the patterns below, flag it for technical support.

---

## 401 — Login / token issues ("Not logged in")

**What the customer may say:**
- *"I'm getting a 401 error"*
- *"My token isn't working"*
- *"It says AUTH_REQUIRED"*
- *"I keep getting logged out"*
- *"My session expired"*
- *"I was working and suddenly it stopped"*

**What it means:** The customer's session token is missing, expired, or invalid.

**How it works (simple explanation):**
Using the Smarkets API requires a "session token" — like a ticket you get when you log in. Every request must present this ticket. The ticket is "valid for 30min, but if you make an authenticated request with it, it will be renewed for the next 30min." If the customer doesn't use the API for 30 minutes, the ticket expires and they need to log in again.

**Things to check (in order):**

**1. Has the token expired?** — Tokens last 30 minutes without activity. They need to log in again via `POST /v3/sessions/` to get a fresh token.

**2. Is the header formatted correctly?** — The token must be sent in the `Authorization` header exactly like this:
`Authorization: Session-Token <their_token>`

**3. Is two-factor authentication (MFA) enabled?** — After logging in, MFA requires an extra step: `POST /v3/sessions/verify/` with their TOTP code. Without this, the token is not fully authorised.

**4. Did they switch from paper trading to live trading (or vice versa)?** — Switching environments invalidates existing tokens. They need a fresh token from the new environment.

**What to tell the customer:**
> "Your session token has expired. Tokens are valid for 30 minutes without activity. To resolve this, log in again via `POST /v3/sessions/` with your email and password to receive a fresh token. Once obtained, include it in the `Authorization` header using the format `Authorization: Session-Token <your_token>` for all subsequent requests.
>
> Note that login is rate-limited to 5 attempts every 5 minutes — if you receive a 429 during login, you must wait before trying again."

**When to flag for technical support:**
- 401 on POST requests but GET requests work fine (possible mixed authentication methods)
- The customer mentions "cookies", "auth v2", or "refresh tokens" (escalate; known case: 401s at ~20 minutes are fixed by sending the session and refresh cookies with each request and adopting the renewed session token)
- The error response contains `data: None` (no further detail to identify the problem)
- The customer is getting 401 from the logout endpoint (`DELETE /v3/sessions/`) — this shouldn't happen normally

---

## 403 — Permission problems ("Not allowed")

**What the customer may say:**
- *"I'm getting a 403 error"*
- *"It says FORBIDDEN"*
- *"I was working fine and now I'm blocked"*
- *"My account can't do this"*
- *"It says ACCOUNT_UNVERIFIED"*
- *"It says RG_ACK_REQUIRED"*
- *"It says KYC_PERMISSION_DENIED"*
- *"My account is suspended"*

**What it means:** The customer's account lacks permission for the requested action.

**Critical: there are two types of 403. The response body tells you which one.**

### Type A: API-level 403 (response is JSON)

The response starts with `{"error_type": "FORBIDDEN", ...}`. This means the account itself is blocked from this action. Possible reasons:

| Reason | What's going on |
|---|---|
| **Not approved for API access yet** | They need to submit the API Request Form (https://support.smarkets.com/p/6MLL-PL7/api-request-form) and pay the GBP150 fee |
| **Under 60-day compliance review** | "All customers will be subject to a compliance review of their account within the first 60 days." This is normal — wait for it to pass |
| **Access suspended or revoked** | They may have violated terms (scraping, sharing data, etc.) |
| **Endpoint-specific 403s** | `ACCOUNT_UNVERIFIED` (registration incomplete), `NO_DEPOSITS` (no money deposited), `KYC_PERMISSION_DENIED` (identity not verified), `ACTION_BLOCKED` (specific action blocked), `RG_ACK_REQUIRED` (responsible gambling acknowledgement not completed) |

**What to tell the customer:**
> "This means your account does not have permission for that action. If you are within your first 60 days of API access, this is expected — your account is undergoing compliance review. If the issue persists beyond that period, contact api@smarkets.com to check your access status."

### Type B: Cloudflare network block (response is HTML)

The response starts with `<!DOCTYPE` or mentions "Cloudflare". This is NOT an API issue — it's a network-level block at the edge.

**What to tell the customer:**
> "This is a network-level block from Cloudflare, not an issue with your API credentials. It commonly affects requests from VPS, server, or data centre IP addresses. Smarkets does not offer IP whitelisting. Please contact our support team for assistance with this type of block."

**When to flag for technical support:**
- The response body is HTML (Cloudflare/edge block)
- The customer wishes to dispute a compliance decision or account suspension
- The customer is unsure how to tell JSON from HTML responses

---

## Login errors (POST /v3/sessions/)

**What the customer may say:**
- *"I can't log in"*
- *"It says INVALID_CREDENTIALS"*
- *"My password isn't working"*
- *"It says DEVICE_NOT_TRUSTED"*
- *"It says SESSION_LIMIT_REACHED"*
- *"It says COUNTRY_BLOCKED"*
- *"I keep getting locked out"*

**What it means:** Something is preventing the customer from completing the login process.

**All login error codes (copy and Ctrl+F):**

| Error code | HTTP | What it really means | What to tell them |
|---|---|---|---|
| `INVALID_CREDENTIALS` | 401 | Email/username or password is wrong | Reset their password on smarkets.com |
| `PASSWORD_RESET_NEEDED` | 401 | The password must be reset before logging in | Reset their password on smarkets.com |
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

**Note on rate limiting:** Login is limited to 5 attempts per 300 seconds (5 minutes). If they try too many times, they'll get a 429 and must wait.

---

## 400 — Bad request / wrong data

**What the customer may say:**
- *"I'm getting a 400 error"*
- *"It says REQUEST_VALIDATION_ERROR"*
- *"The CSV export is failing"*
- *"It says INVALID_DATETIMES"*
- *"It says BAD_REQUEST"*
- *"My order won't go through"*

**What it means:** The data the customer sent is wrong — incorrect format, missing fields, or malformed parameters.

**How it works:** Validation errors always return a JSON body with `"error_type": "REQUEST_VALIDATION_ERROR"` and a `data` field explaining exactly what's wrong. Common examples:

| Error code | What it means | Fix |
|---|---|---|
| `INVALID_DATETIMES` | CSV start/end times are wrong | Start and end "have to be separated by an hour, also these have to be exactly on the hour" (e.g. 2:00 PM to 3:00 PM) |
| `BAD_REQUEST` | Parameters are badly formed (markets/prices endpoints) | Check the parameter format |
| `REQUEST_VALIDATION_ERROR` | Something is wrong with the request | Read the `data` field — it tells you precisely what to fix |
| `RECKONATOR_REQUEST_TOO_LARGE` | Account activity query is too broad | Narrow the date range or reduce filters |

**What to tell the customer:**
> "The API rejected your request because something in the data was incorrect. The `data` field in the error response will tell you precisely what is wrong.
>
> Common causes:
> - **Account activity CSV:** the start and end times must be exactly on the hour (e.g. 2:00 PM to 3:00 PM) and exactly one hour apart
> - **Placing an order:** required fields such as `price`, `quantity`, `contract_id`, or `side` may be missing
> - **IDs:** event, market, and contract IDs must be in the correct format (numeric strings)
> - **Too many IDs in one request:** split the request into smaller batches
> - **Account activity request too large:** narrow your date range
>
> Check the error message carefully — it describes exactly what needs to be corrected."

**When to flag for technical support:**
- The `data` field in the error response is empty or unclear
- You cannot determine which parameter is invalid from the error message
- The customer asks for specific valid values for `price` or `quantity` (these require exchange tick knowledge)
- Invalid price, invalid quantity, or other specialist order rejection codes (see the Order Rejection table below)

---

## 404 — Not found / missing data

**What the customer may say:**
- *"I'm getting a 404"*
- *"The CSV export is empty"*
- *"The event I'm looking for doesn't appear"*
- *"It says NO_CSV_AVAILABLE"*
- *"It says NO_RESULTS_FOUND"*
- *"I can't find this order"*
- *"ORDER_CANCEL_REJECTED_NOT_FOUND"*

**What it means:** The resource the customer is requesting does not exist.

**Common 404 scenarios:**

| Scenario | Error code | What happened |
|---|---|---|
| **Wrong ID** | (generic 404) | The event, market, contract, or order ID is incorrect |
| **CSV — no data for that time** | `NO_CSV_AVAILABLE` | No activity data exists for the requested time range |
| **Event states — no matches** | `NO_RESULTS_FOUND` | No events matched the query parameters |
| **Cancel order — already filled** | `ORDER_CANCEL_REJECTED_NOT_FOUND` | The order may have been filled and no longer exists |

**What to tell the customer:**
> "The API cannot find what you are looking for. This usually means one of the following:
> - The event, market, contract, or order ID you are using is incorrect or doesn't exist
> - For the account activity CSV: no activity data exists for the time range you specified (you will receive a `NO_CSV_AVAILABLE` error)
> - For event states: no events match your criteria (you will receive a `NO_RESULTS_FOUND` error)
> - For cancelling an order: the order may have already been filled or doesn't exist
>
> Verify your IDs by cross-referencing them against responses from the `/v3/events/` or `/v3/accounts/` endpoints."

**When to flag for technical support:**
- The customer insists their IDs are correct but continues receiving 404 responses
- The endpoint itself appears to be incorrect (the customer may have the wrong URL)
- The customer needs guidance navigating Smarkets' event hierarchy to locate the correct IDs

---

## 414 — Request too large

**What the customer may say:**
- *"I'm getting a 414 error"*
- *"It says REQUEST_TOO_LARGE"*
- *"My events query stopped working"*
- *"I sent many IDs at once"*

**What it means:** The customer sent too many IDs in a single request. The API has limits on how many IDs it will accept at once.

**Which endpoints are affected:** Events, markets, contracts, and account activity endpoints that accept arrays of IDs.

**What to tell the customer:**
> "The API rejected your request because it contained too many IDs. You need to split your request into smaller batches. Try reducing the number of IDs you send at once and send multiple separate requests instead."

**When to flag for technical support:**
- The customer is unsure what the ID limit is per request
- The customer needs to process a very large number of IDs efficiently

---

## 429 — Too many requests

**What the customer may say:**
- *"I'm getting 429 errors"*
- *"I've been rate limited"*
- *"It says RATE_LIMIT_EXCEEDED"*
- *"I can't log in — too many attempts"*
- *"I keep hitting my limit"*

**What it means:** The customer has exceeded their pre-approved rate limit. They need to wait before making more requests.

**How it works:** The error response includes three useful fields:
- `count` — how many requests they've already made
- `limit` — their approved maximum
- `expiry` — when the limit resets (ISO timestamp)

**Known per-endpoint rate limits:**

| Endpoint | Limit |
|---|---|
| Quotes (`GET /v3/markets/{ids}/quotes/`) | 50 requests per 60 seconds |
| Login (`POST /v3/sessions/`) | 5 requests per 300 seconds (5 minutes) |
| Cancel all orders (`DELETE /v3/orders/`) | 1 request per 60 seconds |
| Cancel one order (`DELETE /v3/orders/{id}/`) | 10 requests per second |
| Logout (`DELETE /v3/sessions/`) | 30 requests per 60 seconds |

Per Section 5 of the API terms: "exceeding them may lead to temporary suspension" and "repeated violations could result in API or account access being permanently revoked."

**What to tell the customer:**
> "You have exceeded your pre-approved rate limit. The error response includes an `expiry` timestamp showing when the limit resets — you must wait until that time before making further requests.
>
> To reduce how often you hit the limit:
> - Cache price data instead of polling the quotes endpoint repeatedly
> - Batch multiple IDs into a single request where the API supports it
> - Consider using the WebSocket feed for real-time data rather than HTTP polling
> - Note that login is limited to 5 attempts every 5 minutes
>
> If your use case genuinely requires higher limits, contact api@smarkets.com to discuss."

**When to flag for technical support:**
- The customer is hitting limits despite very low apparent usage (possible multiple clients or systems sharing the same account)
- The customer's account has been suspended due to repeated rate limit violations
- The customer needs assistance setting up WebSocket feeds
- The customer mentions Cloudflare-based rate limiting rather than API rate limiting

---

## 451 — Country blocked

**What the customer may say:**
- *"I'm getting a 451 error"*
- *"It says COUNTRY_BLOCKED"*
- *"I can't access the API from my location"*
- *"I'm travelling and it stopped working"*

**What it means:** Smarkets does not offer services in the customer's country or the country their IP address is coming from.

**What to tell the customer:**
> "Your location or account jurisdiction is not supported by Smarkets. This is a geographic restriction and is not related to your credentials or API setup. If you believe this is an error, contact support@smarkets.com to discuss."

**When to flag for technical support:**
- The customer is located in a normally supported country but is receiving this error (possible mismatched account jurisdiction)
- The customer wishes to discuss jurisdiction restrictions

---

## 500, 503 & 504 — Smarkets server issues

**What the customer may say:**
- *"I'm getting 500 errors"*
- *"Internal server error"*
- *"Service unavailable"*
- *"Gateway timeout"*
- *"It says ZEUS_TIMEOUT"*
- *"It says KYC_SERVICE_UNAVAILABLE"*
- *"It says EVENTS_UNAVAILABLE"*

**What it means:** Something went wrong on Smarkets' side. This is NOT caused by the customer. Nothing they do differently will fix it.

**The three types:**

| HTTP | Name | Meaning |
|---|---|---|
| 500 | Internal Server Error | A Smarkets system crashed. Retry in a few minutes. |
| 503 | Service Unavailable | A specific Smarkets system is down. The error code tells you which one (see table below). |
| 504 | Gateway Timeout | A Smarkets backend system didn't respond in time. |

**503 error codes and which system is affected:**

| Error code | System affected |
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
> "This is a server-side issue, not a problem with your request. A 500 means a temporary system failure. 503 and 504 errors mean a specific Smarkets system is temporarily unavailable or timing out.
>
> Please wait a few minutes and try again. If the issue persists, report it to api@smarkets.com with the full error details, including the specific error code — this helps the engineering team identify the affected system."

**When to flag for technical support:**
- Always flag 500, 503, and 504 errors — they are server-side and should be reported to api@smarkets.com
- Note the specific error code — it helps identify which system is affected
- If the customer says "I tried waiting and it still happens" — this confirms a real outage, escalate

---

## Order rejection codes (POST /v3/orders/)

**What the customer may say:**
- *"My order was rejected"*
- *"I can't place a bet"*
- *"It says ORDER_REJECTED_INSUFFICIENT_FUNDS"*
- *"It says ORDER_INVALID_INVALID_PRICE"*
- *"It says KYC_PERMISSION_DENIED"*

**What it means:** The API refused to place an order. Each rejection has a specific code that tells you exactly why.

### Group 1: Money and limits

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_INSUFFICIENT_FUNDS` | Not enough money in the account | Check available balance via `GET /v3/accounts/`. Open orders also consume balance through exposure |
| `ORDER_REJECTED_STAKE_LIMIT_EXCEEDED` | Bet is too large for the account's limit | Reduce the stake or contact support to adjust limits |
| `ORDER_REJECTED_LIMIT_EXCEEDED` | Too many open orders already | Cancel some existing orders before placing new ones |
| `NO_DEPOSITS` | No money has ever been deposited | Make a deposit first |

### Group 2: Market state

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_MARKET_SETTLED` | The market has already finished | Bets can no longer be placed — the event has concluded |
| `ORDER_REJECTED_CONTRACT_SETTLED` | That specific betting option has settled | Choose a different contract within the same market |
| `ORDER_REJECTED_MARKET_NOT_OPEN` | The market isn't accepting bets yet | Wait until the market opens |
| `ORDER_REJECTED_MARKET_HALTED` | Trading was paused (e.g. during in-play delay) | Wait for the market to resume |
| `ORDER_REJECTED_TRADING_SUSPENDED` | Trading is temporarily suspended | Wait for trading to resume |
| `ORDER_CANCELLED_MARKET_HALTED` | Order was cancelled because the market was halted | Wait and re-submit |
| `ORDER_CANCELLED_TRADING_SUSPENDED` | Order was cancelled because trading was suspended | Wait and re-submit |

### Group 3: Wrong values

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_INVALID_INVALID_PRICE` | The price is not a valid tick on the exchange | Price must be in percentage basis points. Per the docs: "Example: 5000 = 50%. To convert to decimal odds, divide 10000 by it. Example: 10000 / 5000 = 2.0." |
| `ORDER_INVALID_INVALID_QUANTITY` | The stake amount is not valid | Minimum is 500 (= 0.05 GBP). Per the docs: "The units are 1/10000 * one unit of the user's currency." |

### Group 4: Conflicts and throttling

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_CROSSED_SELF` | They're trying to match their own opposing order | Adjust the price so it doesn't conflict with their own existing orders |
| `ORDER_REJECTED_THROTTLE_EXCEEDED` | Placing orders too fast | Slow down — wait a bit before the next order |

### Group 5: Not found

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_MARKET_NOT_FOUND` | That market ID doesn't exist | Verify the market ID |
| `ORDER_REJECTED_CONTRACT_NOT_FOUND` | That contract ID doesn't exist | Verify the contract ID |

### Group 6: Account issues

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_ACCOUNT_SUSPENDED` | Account is suspended | Contact support@smarkets.com |
| `KYC_PERMISSION_DENIED` | Identity verification not completed | Verify their identity on smarkets.com |
| `ACCOUNT_UNVERIFIED` | Account registration incomplete | Complete registration and verification |
| `RG_ACK_REQUIRED` | Responsible gambling acknowledgement needed | Complete the RG acknowledgement on smarkets.com |
| `ACTION_BLOCKED` | A specific action was blocked | Contact support@smarkets.com |
| `COUNTRY_BLOCKED` (returns as 451) | Country region is restricted | Smarkets not available in this region |

### Group 7: Market capacity

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_CAPACITY_REACHED` | Maximum orders reached for this market | Try a different market or wait |
| `ORDER_CANCELLED_INSUFFICIENT_LIQUIDITY` | Not enough other people betting to fill the order | Reduce the quantity or adjust the price |

### Group 8: System issues

| Search for this code | What it means | What to tell them |
|---|---|---|
| `ORDER_REJECTED_SERVICE_TEMPORARILY_UNAVAILABLE` | Smarkets system is temporarily down | Wait and retry — server-side issue |
| `ORDER_CANCELLED_MEMBER_REQUESTED` | Order was cancelled by the customer themselves | This is informational — the cancellation was intentional |
| `ORDER_CANCELLED_ADMIN_REQUESTED` | Order was cancelled by Smarkets admin | If unexpected, contact api@smarkets.com |

> **Tip:** Ask the customer for the exact error code. The code itself tells you precisely what is wrong — no interpretation needed.

---

## Cancel-order rejection codes (DELETE /v3/orders/{order_id}/)

**What the customer may say:**
- *"I can't cancel my order"*
- *"It says ORDER_CANCEL_REJECTED"*
- *"The delete order endpoint isn't working"*
- *"It says ORDER_CANCEL_REJECTED_NOT_FOUND"*
- *"It says ORDER_CANCEL_REJECTED_TOO_LATE"*

**What it means:** The API refused to cancel an order. These are different from the order-placing rejection codes above.

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

## Quick Reference Table

| HTTP | Plain English | What to do | Error codes to look for |
|---|---|---|---|
| 400 | Customer sent wrong data | Read the `data` field in the error — it says what's wrong | REQUEST_VALIDATION_ERROR, INVALID_DATETIMES, BAD_REQUEST, RECKONATOR_REQUEST_TOO_LARGE |
| 401 | Not logged in / token expired | Get a fresh token via `POST /v3/sessions/` | AUTH_REQUIRED |
| 403 (JSON) | No permission — account-level | Check API approval, compliance review, or suspension | FORBIDDEN, KYC_PERMISSION_DENIED, ACCOUNT_UNVERIFIED, NO_DEPOSITS, RG_ACK_REQUIRED, ACTION_BLOCKED |
| 403 (HTML) | Cloudflare network block | Not an API issue — flag for technical support | (response starts with `<!DOCTYPE`) |
| 404 | Data doesn't exist | Verify IDs or check time ranges | NO_CSV_AVAILABLE, NO_RESULTS_FOUND, ORDER_CANCEL_REJECTED_NOT_FOUND |
| 414 | Too many IDs in one request | Split into smaller batches | REQUEST_TOO_LARGE |
| 429 | Hit rate limit — too fast | Wait until the `expiry` time in the error | RATE_LIMIT_EXCEEDED |
| 451 | Country not supported | Geographic restriction — not a credentials issue | COUNTRY_BLOCKED |
| 500 | Smarkets crashed internally | Customer should wait and retry | INTERNAL_ERROR |
| 503 | Specific Smarkets system is down | Wait and retry; note the error code for engineering | KYC_SERVICE_UNAVAILABLE, EVENTS_UNAVAILABLE, ZEUS_UNAVAILABLE, etc. |
| 504 | Smarkets backend timed out | Wait and retry; flag if persistent | ZEUS_TIMEOUT, RECKONATOR_UNAVAILABLE |

---

## Frequently Asked Questions

**Q: "How do I get API access?"**
A: They need to submit the API Request Form at https://support.smarkets.com/p/6MLL-PL7/api-request-form. After approval, a GBP150 administration fee is deducted from their account balance. Per Section 3: "Should you choose to permanently withdraw from API usage within the first 60 days, your setup fee will be refunded." All new API accounts undergo a compliance review during this 60-day period (Section 2).

**Q: "Can I get the 0% commission?"**
A: No. Per Section 3: "API customers are ineligible for any affiliate commission offers, as well as the 60 day 0% commission offer for new customers." Standard Customer Commission applies.

**Q: "Am I allowed to scrape odds or market data?"**
A: No. Per Section 2: "All other uses are strictly prohibited, including but not limited to, odds scraping, concealing API calls, browser impersonation or reverse engineering." Violations may result in API removal, bet cancellation, account suspension or closure, and legal action.

**Q: "Can I share market data with a friend?"**
A: No. Per Section 5: "You may not share, sell or distribute platform data — such as prices, market status, events or business information — with third parties without written approval from Smarkets."

**Q: "How do I cancel an order?"**
A: Use `DELETE /v3/orders/{order_id}/` to cancel a specific order, or `DELETE /v3/orders/` to cancel ALL open orders. Rate limit for a single cancellation: 10 requests per second. Rate limit for cancel-all: 1 request per 60 seconds.

**Q: "How long does a session token last?"**
A: Tokens are "valid for 30min, but if you make an authenticated request with it, it will be renewed for the next 30min." So as long as they use the API regularly, the token stays alive. Login is limited to 5 attempts every 5 minutes.

**Q: "What does a 504 error mean?"**
A: A 504 Gateway Timeout means a Smarkets backend system didn't respond in time. Common codes: `ZEUS_TIMEOUT` (core trading engine timeout) and `RECKONATOR_UNAVAILABLE` (activity/reconciliation timeout). Retry after a short wait; escalate to api@smarkets.com if persistent.

**Q: "Which API endpoints don't need a token?"**
A: Events, competitors, contracts, and currencies can be accessed without authentication. Market data endpoints (quotes, prices) require authentication. Prices without a token will be delayed. Session management (login, logout, MFA) also doesn't need prior authentication.

**Q: "Who do I contact for API issues?"**
A: Technical API support: api@smarkets.com. General support: support@smarkets.com. Swagger documentation: docs.smarkets.com. Help centre: help.smarkets.com/hc/en-gb.

---

## When to Flag for Technical Support

If you've read through this guide and can't find the answer, or if the customer's situation matches one of these, pass it to technical support:

| Situation | Why |
|---|---|
| **Cloudflare/edge blocks** — response is HTML | Not an API issue — requires network investigation |
| **Account suspensions and compliance disputes** | Requires human judgement and sensitive handling |
| **"curl works but my code doesn't"** | Development/debugging issue — not API support |
| **WebSocket feed setup** | Separate system with different documentation |
| **Auth v2, refresh tokens, or cookies** | Escalate. Known case: ~20 minute 401s fixed by sending the session and refresh cookies and adopting the renewed session token |
| **Persistent 500, 503, or 504 errors** | Server-side — report to api@smarkets.com |
| **Customer shares raw request/response data you can't interpret** | Better to escalate than guess |
| **Anything that doesn't match a known pattern** | It's safer to escalate than provide wrong advice |

---

*This knowledge base is compiled from the official Smarkets API documentation. Sources: help.smarkets.com (API Resources, Access & T&Cs), docs.smarkets.com (Swagger/OpenAPI portal), and the live OpenAPI v3 specification at api.smarkets.com. Audited against the live spec as of May 2026. If you encounter a scenario not covered here, please document it so the guide can be updated.*
