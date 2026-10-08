# Smarkets API — Frequently Asked Questions

*Last updated: June 2026 (rev 2 — red-team audit fixes applied)*

---

## Getting Started

### What is the Smarkets API?

The Smarkets API lets you trade on the exchange programmatically — through your own software instead of the website. You can retrieve live prices, place and cancel orders, check your balance, and download your account activity, all via HTTP requests.

The API is REST-based and returns JSON. Full interactive documentation is available at [docs.smarkets.com](https://docs.smarkets.com).

### Who is the API for?

The API is designed for customers who want to build their own trading tools, automate strategies, or integrate Smarkets into a larger system. You'll need some programming knowledge to use it — there's no graphical interface, and Smarkets does not provide official SDKs or client libraries as of June 2026.

If you just want to place bets manually, the website and mobile app are the right tools for the job.

### How do I get API access?

1. Submit the [API Request Form](https://support.smarkets.com/p/6MLL-PL7/api-request-form)
2. Our team will review your application and get back to you
3. Once approved, a £150 administration fee is deducted from your account balance
4. Your API access will be activated — you log in with your existing Smarkets email and password, there are no separate API credentials to wait for

You need a fully registered and verified Smarkets account before you can apply.

### How much does it cost?

There's a one-time £150 setup fee (or the equivalent in your account currency). This is deducted from your account balance once your application is approved — not at the point of application.

After that, you pay normal exchange commission on your winnings. Some use cases may be subject to additional fees or restrictions — see Section 5 of the [API Terms and Conditions](https://help.smarkets.com/hc/en-gb/articles/34697834941085-Smarkets-API-Access-Integration-T-Cs) for details.

Smarkets reserves the right to change commercial terms, including fees and commission rates, with notice. Continued use of the API after any such change constitutes acceptance of the updated terms.

### Can I get a refund on the setup fee?

Yes. If you permanently withdraw from API usage within the first 60 days, the £150 fee will be refunded. After the 60-day window, the fee is non-refundable.

If you'd like to withdraw, contact support@smarkets.com to confirm.

### How long does approval take?

Applications are reviewed on a case-by-case basis. Our team will contact you once your application has been processed. If you haven't heard back and it's been a while, contact us at api@smarkets.com.

### Who is eligible for API access?

To qualify for API access, you must:

- Have a fully registered and verified Smarkets account (KYC complete)
- Be in a supported jurisdiction
- Not be self-excluded or on a gambling timeout
- Not be an employee or contractor of Smarkets or a related company

Smarkets reserves full discretion to refuse or revoke API access at any time, with or without cause (per Section 1 of the API T&Cs). Approval is not guaranteed, even if you meet all the above criteria.

### What happens during the 60-day compliance review?

All new API accounts go through a compliance review during the first 60 days. This is standard — you can still use the API during this period, but certain restrictions may apply depending on your account status. You don't need to do anything unless we contact you.

### Can I get read-only or data-only access?

No. The API is a single product with full access — market data and order management together. There's no reduced tier for data-only use, and using the API purely to collect data without trading isn't permitted under the terms.

If you're interested in market data specifically, the public endpoints for events, competitors, contracts, and currencies are accessible without authentication. Real-time quotes and prices require an authenticated session. Note: the quotes endpoint description mentions that prices may be available in a delayed form without a session token, but the security configuration requires authentication — contact api@smarkets.com to clarify if unauthenticated access is supported for your use case.

---

## Authentication & Sessions

### How do I log in?

Send a POST request to `/v3/sessions/` with your **email** and password. The API field is called `username` — use your email address as the value. The request body is JSON:

```json
{
  "username": "your.email@example.com",
  "password": "yourpassword"
}
```

You'll receive a session token in the response — include this in the `Authorization` header for all subsequent requests:

```
Authorization: Session-Token <your_token>
```

You use the same email and password as you do on the Smarkets website. There are no separate API credentials.

### How long does a session token last?

Tokens are valid for 30 minutes. Every time you make an authenticated request, the token is renewed for another 30 minutes — so as long as you're actively using the API, the token stays alive.

If the token expires (30 minutes of inactivity), you'll need to log in again to get a fresh one.

### What happens if I have MFA enabled?

If you have multi-factor authentication turned on, logging in returns a limited session token. You'll then need to verify your identity by sending a POST to `/v3/sessions/verify/` with your current TOTP code from your authenticator app.

Once verified, your token is fully authorised and you can place orders and access account features.

### Why do I keep getting 401 errors?

Usually one of these:

- **Your token has expired.** Log in again to get a new one.
- **You're not including the token in the header.** Make sure every authenticated request has `Authorization: Session-Token <your_token>`.
- **You have MFA but haven't completed the verification step.** After logging in, send your TOTP code to `/v3/sessions/verify/`.

### Is login rate-limited?

Yes — 5 attempts per 5 minutes. If you exceed this, you'll get a 429 error and need to wait before trying again.

### How do I log out?

Send a DELETE request to `/v3/sessions/`. This invalidates the current session token. Logging out is rate-limited to 30 requests per 60 seconds.

---

## Markets & Events

### How is data organised on the exchange?

Smarkets uses a four-level hierarchy:

1. **Event** — the real-world thing happening (e.g. Arsenal vs Chelsea)
2. **Market** — a specific bet type within an event (e.g. Match Winner, Over/Under 2.5 Goals)
3. **Contract** — an individual outcome within a market (e.g. Arsenal to Win, Draw, Chelsea to Win)
4. **Order** — the bet you place on a contract

You'll need the correct IDs at each level to place orders. Events and markets can be retrieved via the public endpoints — no authentication needed for those.

### How do I find available events?

Send a GET request to `/v3/events/` to retrieve events available on the exchange. The endpoint supports query parameters for filtering — see the [interactive documentation](https://docs.smarkets.com) for the full list of available parameters.

### Which endpoints are available?

The API has 21 endpoints across eight categories:

| Category | Endpoints | Auth required? |
|---|---|---|
| **Sessions** | Login, logout, MFA verify | No (these are how you get a token) |
| **Accounts** | Account info, account activity, activity CSV | Yes |
| **Events** | Events list, event states | No |
| **Competitors** | Competitors by event | No |
| **Markets** | Markets by event, market count, contracts | No |
| **Prices** | Quotes, last executed prices, **volumes** | Yes |
| **Orders** | Place, retrieve, cancel, cancel-all, fullcover | Yes |
| **Currencies** | Currency conversion rate | No |

Public endpoints (events, event states, competitors, markets by event, markets count, contracts, currencies) are accessible without a token. Prices (quotes, last executed prices, volumes) and all order endpoints require authentication.

### What is the fullcover orders endpoint?

`GET /v3/orders/fullcover/` retrieves all fullcover orders for your account. Fullcover orders are a specific order type related to full cover bets (a type of multiple bet). Full covers cannot be placed on Smarkets itself, so this endpoint will only return existing fullcover orders, if any.

### What does the currencies endpoint do?

`GET /v3/currencies/{code}/` returns the conversion rate for a specific currency. This is useful if your account currency differs from the currency a market is denominated in — the API's price and quantity values are always in your account currency, but the conversion endpoint lets you check rates if you need to reconcile across currencies.

### Why can't I access certain markets through the API?

API access is restricted to pre-approved events and markets, which are determined per account during the application process. If a market isn't available to you, it may be outside your approved scope.

If you think a market should be available, contact api@smarkets.com with the event or market details and we'll look into it.

### The quotes endpoint returns an empty order book but the website shows prices. Why?

The API quotes endpoint returns the peer-to-peer (P2P) order book — orders placed by other exchange users. The website may aggregate additional data sources not available through the API.

If the quotes endpoint returns an empty order book, there may be no P2P resting orders on that market at that moment. This is particularly common on lower-liquidity in-play markets where P2P order books are thin — the website may show prices from additional internal pricing sources that the API does not expose.

For confirmation of what data the quotes endpoint includes, contact api@smarkets.com.

---

## Placing Orders

### How do I place a bet?

Send a POST request to `/v3/orders/` with the following required fields:

- `market_id` — the market you want to bet on
- `contract_id` — the specific outcome
- `price` — the odds you want (in basis points — see below)
- `quantity` — how much you want to stake (in internal units — see below)
- `side` — `"buy"` (back) or `"sell"` (lay)

You can also include the optional `type` field to control how the order behaves (see below). If you omit it, the default is `good_til_halted`.

An optional `label` field lets you attach a user-defined string to the order — useful for identifying different trading strategies when reviewing your order history.

### What's the difference between buy/sell and back/lay?

The API uses `buy` and `sell` where other exchanges (like Betfair) use `BACK` and `LAY`:

- **`buy`** = **back** — betting that an outcome WILL happen
- **`sell`** = **lay** — betting that an outcome WON'T happen

If you're migrating from another exchange, this is the terminology mapping to keep in mind.

### How are prices formatted?

Prices are in percentage basis points out of 10,000. To convert to decimal odds, divide 10,000 by the price:

- 5000 → 10,000 ÷ 5000 = 2.0 (even money)
- 2500 → 10,000 ÷ 2500 = 4.0 (3/1)
- 1000 → 10,000 ÷ 1000 = 10.0 (9/1)

Valid prices range from 1 to 9999 and must conform to a valid tick on the exchange. The tick structure isn't published in the API documentation — if you receive an `ORDER_INVALID_INVALID_PRICE` error, the price you sent isn't on a valid tick. You can retrieve valid prices from the quotes endpoint for any market.

### How are quantities formatted?

Quantities are in 1/10,000th of your account currency:

- 500 = £0.05 (minimum stake)
- 10,000 = £1.00
- 20,000 = £2.00
- 100,000 = £10.00

The maximum quantity is 4,294,967,295 (unsigned 32-bit integer limit).

The spec describes quantity as "the sum of the total pot (back + lay) in case the order is matched." To convert quantity to back stake, multiply by the price and divide by 100,000,000. For example: quantity 100000 at price 5000 → back stake = 100000 × 5000 ÷ 100000000 = £5.00.

A common mistake: sending `quantity: 800` expecting it to mean £2.00, when it actually means £0.08. To stake £2.00, you need `quantity: 20000`.

### What order types are available?

The `type` field controls how your order behaves when market conditions change:

| Type | Market goes live | Market halted | Reduction factor applied |
|---|---|---|---|
| `good_til_cancelled` | Cancelled | Cancelled | Cancelled |
| `good_til_halted` (default) | **Kept** | Cancelled | Cancelled |
| `keep_in_play` | **Kept** | **Kept** | Cancelled |
| `immediate_or_cancel` | N/A — executes immediately | N/A | N/A |

If you don't specify a `type`, the default is `good_til_halted`. This means your order survives when the market goes live (e.g. from pre-match to in-play) but is cancelled if the market is halted or a reduction factor is applied.

**"In-play"** refers to betting on events while they're happening live — for example, betting on a football match while the game is being played. Markets transition from pre-event to in-play, and some order types handle that transition differently.

In-play markets have a betting delay: **4 seconds** for horse racing and darts, **8 seconds** for all other events. During this delay, your order is pending and not yet matched or visible in the order book.

Use `keep_in_play` if you want your order to survive both the market going live AND temporary halts. Use `good_til_cancelled` if you want the order cancelled when the market goes live (so it doesn't carry into in-play). Use `good_til_halted` (the default) if you want it to carry into in-play but be cancelled on any halt.

`immediate_or_cancel` is different — it tries to match immediately at placement time. Whatever can't be matched is cancelled. It doesn't sit in the order book.

### Does the API support Fill-or-Kill (FOK)?

Not as a separate order type. To achieve FOK behaviour, use `type: "immediate_or_cancel"` and set `minimum_accepted_quantity` to the same value as `quantity`. This tells the exchange: fill the entire amount or cancel the whole order.

If you only need partial fills to be acceptable, set `minimum_accepted_quantity` lower than `quantity` — the order will fill at least that much and cancel whatever's left.

We recommend always setting `minimum_accepted_quantity` explicitly to control how partial fills are handled.

### Is there a `time_in_force` field?

No. The Smarkets API doesn't use `time_in_force`. If you see this field in your code, it's either from your own abstraction layer or from another exchange's API. Smarkets handles order behaviour through the `type` and `minimum_accepted_quantity` fields instead.

### How do I cancel an order?

- Cancel a specific order: `DELETE /v3/orders/{order_id}/`
- Cancel all open orders: `DELETE /v3/orders/`

Rate limits: 10 cancellations per second for individual orders, 1 per 60 seconds for cancel-all.

### Why was my order rejected?

Every rejection includes a specific error code. The ones we see most often:

- `ORDER_REJECTED_INSUFFICIENT_FUNDS` — not enough available balance. Open orders lock up funds through exposure, so your available balance may be lower than your total balance.
- `ORDER_INVALID_INVALID_PRICE` — the price isn't on a valid exchange tick. Check the quotes endpoint for valid prices.
- `ORDER_INVALID_INVALID_QUANTITY` — below the minimum stake (500 = £0.05) or otherwise invalid.
- `ORDER_REJECTED_MARKET_HALTED` — the market is paused (common during in-play when events are happening).
- `RG_ACK_REQUIRED` — you need to complete the Responsible Gambling acknowledgement on the website first.
- `ORDER_REJECTED_STAKE_LIMIT_EXCEEDED` — the stake exceeds your account's limit. The maximum stake limit isn't published in the API documentation — contact support to check or adjust your limit.

Check the error code in the response — it's self-explanatory in most cases. For the full list of rejection codes, see the [interactive documentation](https://docs.smarkets.com).

### What does the POST /orders/ response include?

For `immediate_or_cancel` orders, the response includes `total_executed_quantity` — the amount that was matched at placement time. If nothing was matched, this will be zero.

The response also includes several other useful fields:
- `order_id` — use this to track the order via `GET /v3/orders/{id}/`
- `executed_avg_price` — the average price at which the order was matched (null if no executions)
- `available_balance` — your remaining balance after the order was placed
- `exposure` — your current exposure on the account

The POST response does not include `quantity_filled` or `state` fields. Those are available on the GET endpoint (`GET /v3/orders/{id}/`) if you need them.

For other order types (`good_til_cancelled`, `good_til_halted`, `keep_in_play`), the response confirms the order was accepted — matching happens when another customer takes the other side. Use the order ID from the response to check status via `GET /v3/orders/`.

---

## Rate Limits

### What are the rate limits?

Limits are per-endpoint and pre-approved per account. The documented limits:

| Endpoint | Limit |
|---|---|
| Quotes (`GET /v3/markets/{ids}/quotes/`) | 50 requests per 60 seconds |
| Login (`POST /v3/sessions/`) | 5 requests per 300 seconds |
| Cancel all orders (`DELETE /v3/orders/`) | 1 request per 60 seconds |
| Cancel one order (`DELETE /v3/orders/{id}/`) | 10 requests per second |
| Logout (`DELETE /v3/sessions/`) | 30 requests per 60 seconds |

Other endpoints have limits too, but they're not individually documented. The error response will tell you your specific limits.

### What happens when I hit a rate limit?

You'll receive a 429 error with a `RATE_LIMIT_EXCEEDED` error type. On most GET endpoints (events, orders, accounts, currencies, and others), the response includes three fields:

- `count` — how many requests you've made so far
- `limit` — your approved maximum
- `expiry` — an ISO timestamp showing when the window resets

Wait until the `expiry` time has passed before sending more requests.

Note: some endpoints — including order placement, cancellation, and session management — may return a 429 with a less detailed response body. The quotes endpoint (`GET /v3/markets/{ids}/quotes/`) is also an exception among GET endpoints — it uses the less detailed schema without count/limit/expiry fields. If you receive a 429 without structured fields, wait a short period before retrying.

### Can I get my rate limits increased?

It depends on your use case. Contact api@smarkets.com to discuss whether your rate limits can be adjusted. Approval is at Smarkets' discretion.

Approval isn't guaranteed.

### What happens if I keep exceeding limits?

Per Section 5 of the API terms, exceeding rate limits may lead to temporary suspension. Repeated violations could result in API or account access being permanently revoked.

---

## Commission

### What commission do I pay?

The default is **2% on net profit per market** (Standard Tier). On the Standard Tier, you only pay commission when you win — if your net result on a market is a loss, there's no commission charge.

Commission is calculated per market, not per individual bet. If you place multiple bets on the same market — some winning, some losing — the commission is on your overall net result for that market.

Note: the Pro and Select tiers work differently — they charge commission on both winnings and losses per matched bet. See below for details.

### Does API access give me a lower commission rate?

No. The same commission tiers apply whether you trade via the website, the mobile app, or the API. API access doesn't automatically qualify you for a lower rate.

### Can I get the 0% new customer offer?

No. API customers are ineligible for the 60-day 0% commission offer for new customers, as well as any affiliate commission offers (per Section 3 of the API T&Cs).

### What are the commission tiers?

Smarkets has three tiers:

**Standard (2%)** — the default for all accounts. Charged on net profit per market. You only pay when you win.

**Pro (1%)** — for high-volume traders. If you place more than 1,500 bets or stake more than £1 million in a calendar month, you're eligible to opt in to the Pro Tier (1%) for a lower commission rate. You must pass 80% of either threshold before you can opt in. Opting in is optional — you can stay on the Standard Tier (2%) if you prefer. To opt in, contact customer support.

On the Pro Tier, commission is charged per individual matched bet that settles — on winnings if the bet wins, and on losses if the bet loses. This is different from the Standard Tier, which only charges on net profit.

**Select (3%)** — applied automatically to accounts that exceed £25,000 in net profit over the previous 12 calendar months. You'll be notified by email 7 days before this takes effect.

Full details are on the [Commission FAQ](https://help.smarkets.com/hc/en-gb/articles/212654665-Smarkets-commission-FAQ).

### Can I opt out of the Pro Tier?

Yes, but only after 3 months. If you'd like to switch back to the Standard Tier, contact customer support.

### I'm on the Select Tier — can I get back to Standard?

If your net P&L over the previous 12 calendar months drops below £25,000, you can apply to have your commission rate reviewed. Contact customer support to request a review. Reviews are at Smarkets' discretion.

### If I opt into the Pro Tier, do I lose my 0% promotion?

Yes. Opting into the Pro Tier permanently forfeits any commission promotion on your account. The same applies if the Select Tier is applied to you.

---

## Account & Verification

### Why do I need to verify my account?

KYC (Know Your Customer) is a legal requirement for all gambling operators. Smarkets must verify your identity, age, and address before you can place bets. This applies to website and API users equally.

### What documents do I need?

Typically:
- Photo ID (passport, driving licence, or national ID card)
- Proof of address (utility bill or bank statement dated within the last 3 months, or a council tax bill or tax bill for the current year)

Screenshots of online documents are not accepted — you'll need to provide the original document or a PDF. Mobile phone bills cannot be used as proof of address. You can't use the same document for both ID and address verification.

In some cases, we may ask for source of funds or source of wealth documentation. This is a standard regulatory requirement — it's not specific to you or to API users.

### I'm getting KYC_PERMISSION_DENIED — what do I do?

Log in to smarkets.com (the website, not the API) and complete any outstanding verification steps. Once verification is complete, the API will work automatically — no code changes needed.

### Why was my payment declined?

Usually one of these:
- The name on the payment method doesn't match the name on your Smarkets account
- The payment came from a third-party account (not permitted under anti-money laundering rules)
- Your bank declined the transaction

Withdrawals must go back to the same payment method you used to deposit — this is a regulatory requirement, not a Smarkets-specific policy. If you're trying to withdraw to a different method, that's why it's being declined.

If a withdrawal is taking longer than expected, contact support@smarkets.com and they'll look into it for you.

---

## Responsible Gambling

All responsible gambling controls apply equally to API users — there is no exemption for automated trading. This includes deposit limits, loss limits, session timeouts, self-exclusion, affordability checks, and RG acknowledgements. Accounts may be restricted or suspended for RG reasons at any time, regardless of whether you trade via the website or the API.

### What is RG_ACK_REQUIRED?

This error means you need to complete the Responsible Gambling acknowledgement on the website before you can place bets — via the API or otherwise.

Log in to smarkets.com, complete the RG acknowledgement popup, then try again. The block lifts immediately — no need to change your code.

If you can't find the popup, try navigating to a market page — it should appear there.

### How do I set deposit limits?

Deposit limits can be set in your account settings on smarkets.com. They apply across all access methods (website, mobile, and API). Daily, weekly, and monthly limits are available, and can be set as net or gross amounts. Increasing a deposit limit triggers a 72-hour cooling-off period before the new limit takes effect.

### I want to self-exclude. What do I do?

You can self-exclude through the Safer Gambling section of your account on smarkets.com, or by contacting support@smarkets.com. Self-exclusion applies to your entire account — website, mobile app, and API.

### What's the difference between a timeout and self-exclusion?

A **timeout** is a temporary break — you choose a period of 1, 7, 31, or 42 days, and your account is automatically reactivated when it ends.

**Self-exclusion** is a longer-term measure. Available periods are six months, one year, five years, or permanent. Once self-excluded, your account stays closed for the full exclusion period and can't be reactivated early. Any balance on your account is returned to you within 48 hours.

Both apply across all access methods.

---

## Terms, Compliance & Usage

All use of the Smarkets API is governed by the [Smarkets API Access & Integration Terms and Conditions](https://help.smarkets.com/hc/en-gb/articles/34697834941085-Smarkets-API-Access-Integration-T-Cs). By using the API, you agree to these terms. The sections below summarise key obligations — the full T&Cs take precedence.

### What am I permitted to do with the API?

The API is intended for **viewing market prices and placing bets** on the Smarkets exchange (per Section 2 of the T&Cs). This includes:

- Retrieving live prices, quotes, and order book data
- Placing, modifying, and cancelling orders
- Checking your account balance, exposure, and activity
- Automating trading strategies on pre-approved markets

### What is explicitly prohibited?

The following are strictly prohibited under the API T&Cs:

- **Odds scraping** — extracting prices or data for use outside the exchange (Section 2)
- **Concealing API calls** — disguising API requests as browser traffic (Section 2)
- **Browser impersonation or reverse engineering** (Section 2)
- **Data resale or redistribution** — sharing, selling, or distributing platform data (prices, market status, events, business information) with third parties without written approval from Smarkets (Section 5)
- **Benchmarking** — using the API to compare Smarkets' markets, prices, liquidity, systems, or services for competitive purposes (Section 5)
- **Data harvesting** — requesting large volumes of market data without corresponding trading activity (Section 6.1)
- **Fee avoidance** — creating multiple accounts to circumvent commission thresholds (Section 7)
- **Unfair trading strategies** — latency arbitrage, court-siding, or any strategy Smarkets considers harmful to the exchange ecosystem (Section 7)

### How does Smarkets monitor API usage?

Smarkets actively monitors API usage for abuse, fair usage compliance, and adherence to rate limits. Monitoring covers request patterns, data-to-trade ratios, and trading behaviour.

If violations are detected, the escalation path is typically:

1. **Warning** — a formal notice describing the violation and required corrective action
2. **Temporary suspension** — API access suspended for a defined period
3. **Permanent removal** — API and/or account access permanently revoked

Serious violations (e.g., fraud, data theft) may result in immediate permanent removal without prior warning. Smarkets also reserves the right to cancel bets, void transactions, and pursue legal action where warranted.

### What can get my API access suspended?

- Data harvesting — requesting large volumes of market data without corresponding trading activity
- Fee avoidance — creating multiple accounts to dodge commission thresholds
- Unfair trading strategies — things like latency arbitrage or court-siding that Smarkets considers harmful to the exchange ecosystem
- Repeated rate limit violations
- Sharing or distributing platform data without permission
- Responsible gambling concerns — accounts may be restricted or suspended for RG reasons at any time

If your access is suspended and you believe it's in error, contact api@smarkets.com.

---

## Betting Rules

### What is a reduction factor?

A reduction factor is applied when a horse is withdrawn from a race. It reduces the odds of the remaining runners to account for the fact that there's now one less competitor.

The formula is: `New odds = Old odds × ((100 − reduction factor) / 100)`

For example, if a horse at odds of 4.0 gets a 40% reduction factor applied, the new odds become 4.0 × 0.6 = 2.4.

### How do reduction factors affect accumulators?

If a reduction factor is applied to a selection in your accumulator, the odds of that leg are reduced accordingly. Because accumulator odds are calculated by multiplying all legs together, reducing one leg's odds by 40% reduces the total potential payout by 40%.

The same proportional reduction happens on single bets — it just looks more dramatic on an accumulator because the absolute numbers are bigger.

Full details are in the [General Betting Rules](https://help.smarkets.com/hc/en-gb/categories/360001480411).

### What happens when a market is suspended?

Trading is temporarily paused. What happens to your open orders depends on their type: `keep_in_play` orders remain in the book and will resume matching when trading resumes. `good_til_cancelled` and `good_til_halted` (the default) orders are cancelled when the market is halted — they will not resume. You can't place new orders while the market is suspended.

Common reasons for suspension include a market transitioning from pre-match to in-play, a horse being withdrawn from a race, or technical issues. Note: in-play markets with a betting delay are not halted for individual events like goals, penalties, or red cards — the delay mechanism handles those situations.

### How are markets settled?

Markets are settled once the event is complete and the result is confirmed. Matched bets are settled at the odds they were matched at, with commission applied to net profit per market.

For Instant Match bets, there's a confirmation period of 8–14 seconds during which the match is pending. This is a standard betting rule, not an API-specific delay.

Unmatched orders are typically cancelled when the market settles. This is standard exchange behaviour, though it's not explicitly documented in the API specification — if you observe different behaviour, contact api@smarkets.com.

---

## Technical Issues

### I'm getting a 403 error from my VPS or server. Why?

If the 403 response is HTML (starts with `<!DOCTYPE`) rather than JSON, it's likely an edge block — not an API authentication issue. This commonly affects requests from data centre IPs, VPS providers, and cloud servers.

If the 403 response is JSON, check the error code — the API returns specific codes such as `SOURCE_BLOCKED` or `IP_NOT_TRUSTED` for blocked IP addresses.

IP whitelisting is not a documented feature of the API. Contact support to discuss your specific situation.

### I'm getting 500, 503, or 504 errors. What should I do?

These are server-side issues — the problem is on our end, not yours. Wait a few minutes and try again.

If the issue persists, report it to api@smarkets.com with the full error details including the specific error code (e.g. `ZEUS_TIMEOUT`, `EVENTS_UNAVAILABLE`). The error code tells our engineering team which system is affected.

### I can place bets on the website but not via the API. Why?

Several things could cause this:

- **RG_ACK_REQUIRED** — complete the Responsible Gambling acknowledgement on the website
- **Account not yet approved for API access** — check your application status
- **60-day compliance review** — temporary restrictions may apply
- **KYC_PERMISSION_DENIED** — complete identity verification on the website
- **NO_DEPOSITS** — you need to make a deposit first

The error code in the 403 response will tell you which one applies.

### I sent the correct quantity but the stake shows differently on the website.

You're likely sending the wrong unit value. The API uses 1/10,000th of your account currency for quantities. Check the conversion:

- `quantity: 800` = £0.08 (not £2.00)
- `quantity: 20000` = £2.00
- `quantity: 100000` = £10.00

See the Placing Orders section above for the full conversion table and the back stake formula from the spec.

### My order was placed but the fill amount doesn't match what I expected.

For `immediate_or_cancel` orders, the POST response includes `total_executed_quantity` — the amount actually matched. If the order book didn't have enough liquidity at your price, you may get a partial fill (if `minimum_accepted_quantity` allows it) or no fill at all.

If you set `minimum_accepted_quantity` equal to `quantity`, the order should either fill entirely or not at all. If you observe different behaviour, contact api@smarkets.com with the full request and response.

---

## Service Availability, Security & Termination

### What is the expected API uptime?

The API is designed for high availability, but Smarkets does not guarantee uninterrupted service. Planned maintenance, unexpected outages, and third-party dependencies can all cause disruptions. The API may be temporarily unavailable during market suspensions, sporting event disruptions, or system upgrades.

If you experience a sustained outage, check that it's not an account-specific issue (403/401 errors) before reporting it as a service incident. For confirmed outages, report to api@smarkets.com with the timestamp, affected endpoints, and error codes.

### Can Smarkets change or withdraw the API?

Yes. Smarkets reserves the right to modify, suspend, or withdraw the API — or any part of it — at any time, with or without notice (per the API T&Cs). This includes changing endpoints, rate limits, schemas, commercial terms, or discontinuing the service entirely.

Where practicable, Smarkets will provide advance notice of breaking changes. However, you should design your integration to handle unexpected API changes gracefully. Continued use of the API after any change constitutes acceptance of the updated terms.

### Am I responsible for keeping my credentials secure?

Yes. You are solely responsible for keeping your Smarkets account email, password, and session tokens secure. Do not share your login credentials with anyone, embed them in client-side code, or commit them to public repositories.

If you suspect your credentials have been compromised:

1. Log in to smarkets.com and change your password immediately
2. Log out of all active API sessions (`DELETE /v3/sessions/`)
3. Contact support@smarkets.com to report the incident

Smarkets is not liable for losses resulting from compromised credentials that you failed to protect. Account sharing is also prohibited under the T&Cs — each user must have their own account.

### Can Smarkets terminate my API access?

Yes. Smarkets may terminate or suspend API access at any time, with or without cause. Grounds for termination include:

- Violation of the API T&Cs
- Responsible gambling concerns
- Regulatory or legal requirements
- Account closure for any reason
- Extended inactivity

If your API access is terminated, any unmatched orders are typically cancelled and your balance is returned according to the standard withdrawal process.

---

## Contact & Support

### Who should I contact?

| What you need | Who to contact |
|---|---|
| Technical API questions, bugs, error codes | api@smarkets.com |
| General API questions, account issues, payments, verification | support@smarkets.com |
| API access application | [API Request Form](https://support.smarkets.com/p/6MLL-PL7/api-request-form) |
| General help and betting rules | [Help Centre](https://help.smarkets.com/hc/en-gb) |

### What should I include in a support email?

For the fastest resolution:
- The full error response (status code, error type, and data fields)
- The exact request you sent (URL, headers, body) — redact your session token
- What you expected to happen vs what actually happened
- How long you've been using the API and when the issue started

### Is there a real-time data feed?

For real-time data options beyond the REST API, contact api@smarkets.com to discuss what's available for your use case.

---

*This FAQ covers the most common questions about the Smarkets API. For the full interactive API documentation, visit [docs.smarkets.com](https://docs.smarkets.com). For betting rules and general help, visit the [Help Centre](https://help.smarkets.com/hc/en-gb). For the full terms governing API use, see the [API Access & Integration T&Cs](https://help.smarkets.com/hc/en-gb/articles/34697834941085-Smarkets-API-Access-Integration-T-Cs).*

*If your question isn't answered here, contact us at api@smarkets.com and our team will assist you.*
