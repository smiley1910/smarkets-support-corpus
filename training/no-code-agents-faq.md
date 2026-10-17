# Smarkets API for No-Code Builders — FAQ

*For Zapier, Make, n8n, Bubble, Sheets. No coding needed — you just need a tool with an "HTTP request" or "API call" module. There is no official Zapier app, Make app, or SDK.*
*Last checked against live docs: Oct 2026.*

## Start here — links you need

- Interactive API docs (try every endpoint in your browser): https://docs.smarkets.com/
- API Request Form (how you apply): https://support.smarkets.com/p/6MLL-PL7/api-request-form
- Help Centre (betting rules, general help): https://help.smarkets.com/hc/en-gb
- API rules (Access, Integration and T&Cs): https://help.smarkets.com/hc/en-gb/articles/34697834941085-Smarkets-API-Access-Integration-T-Cs
- Commission explained: https://help.smarkets.com/hc/en-gb/articles/212654665-Smarkets-commission-FAQ
- API tech help: api@smarkets.com
- Account, money, ID, application help: support@smarkets.com
- The API itself lives at: https://api.smarkets.com (all calls start with this)

## What is the API?

The Smarkets API lets your tools talk to the Smarkets exchange directly instead of you clicking on the website.

With it you can check live prices, place and cancel bets, check your balance, and download your statement — all from an automation.

It is for the Smarkets exchange (you bet against other customers). It is not for SBK (the sportsbook where you bet against the house). Balances are separate.

It speaks REST + JSON. That just means your tool sends a web address + some fields, and gets a structured reply back.

## Is it for me?

Yes if you can tick these:

- You have a no-code tool with a generic HTTP module. In Zapier it is called "Webhooks by Zapier, Custom Request". In Make it is "HTTP, Make a request". In n8n it is "HTTP Request". In Bubble it is "API Connector".
- You are comfortable copying a URL, a header, and a few field names exactly.
- You have (or will open) a fully verified Smarkets exchange account.

You do not need it if you just place bets by hand. Use the website or app.

There is no test mode with fake money, no read-only key, and no data-only feed. One product: live prices + live betting together.

## Your journey, step by step

**Step 1 — Verify your Smarkets account.**
Log in at smarkets.com and finish ID + address checks first. You cannot get API access on an unverified account. Upload a real photo ID (passport, driving licence) and a real proof of address from the last 3 months (utility bill, bank statement). Screenshots are not accepted. Mobile phone bills do not count.

**Step 2 — Read the docs.**
Open https://docs.smarkets.com/ and skim the endpoint list. You do not need to understand it all — just confirm your plan fits: viewing prices and placing bets. Collecting prices without betting, reselling data, or comparing prices to sell elsewhere is not allowed.

**Step 3 — Apply.**
Fill in the API Request Form: https://support.smarkets.com/p/6MLL-PL7/api-request-form
Describe what you will build in plain words (e.g. "price alert on Make that checks 50 football markets every minute" or "Sheets tracker that logs my bets every 15 minutes"). The team reviews case by case.

**Step 4 — Pay the £150 setup fee.**
One-off £150 (or equivalent in your currency). It is taken from your balance when approved, not when you apply. You get it back if you quit API use within 60 days — email support@smarkets.com to withdraw.

**Step 5 — Get approved and trade.**
Approval is not instant and not guaranteed. Once approved you log in with your normal Smarkets email + password — there is no separate API key to wait for. All new API accounts get a standard 60-day compliance review. You can trade during it.

**Step 6 — Build your first login (below), then your first price check, then your first bet.**

## Your first login, slowly

There is no API key. Your Smarkets email + password IS your API login. Each login gives you a temporary `token` you attach to every other call.

Build this once in your tool, then reuse it. Settings for Make / n8n / Zapier / Bubble are the same, only the button names differ.

**Call 1 — Login.**
- Method: POST
- URL: https://api.smarkets.com/v3/sessions/
- Header: Content-Type: application/json
- Body (JSON):
```json
{
  "username": "your.email@example.com",
  "password": "yourpassword"
}
```
The field MUST be called `username` even though the value is your email. Using `email` as the field name fails.

Success looks like HTTP 201 (not 200) with a body containing `token`. Save that `token` value — it is your session. Accept 200 OR 201 in your tool or the step shows as failed when it worked. The field is called `token`, not `session_token`.

**Every call after that — attach your token.**
- Header: Authorization: Session-Token YOUR_TOKEN
- Exact words `Session-Token`, one space, then the token. Not `Bearer`. Not `X-Smarkets-Token`.

Test it with: GET https://api.smarkets.com/v3/accounts/ + that header. If it returns your balance, your login works.

**If you use an authenticator app (MFA).**
Login gives you a limited token. Add one more call before anything else:
- POST https://api.smarkets.com/v3/sessions/verify/ + your 6-digit code.
Only then can you place bets. Symptom you skipped this: login works but every bet returns 401.

**Logging out.**
DELETE https://api.smarkets.com/v3/sessions/ with the same Authorization header. Optional but tidy for scheduled runs.

**Three traps everyone hits:**
1. 201 vs 200 — login returns 201. Allow both.
2. `username` vs `email` — field name must be `username`.
3. `token` vs `session_token` — read `token`.

**Why do I get logged out after ~20 minutes (401)?**
Sessions rotate about every 20 minutes even while active. For short runs (under 15 minutes) ignore this — just log in fresh each run. For long runs add a branch: if any step returns 401, run Login once, replace the token, retry that step once, then stop and alert if it fails again. Never loop login — it allows only 5 tries per 5 minutes, then locks you out.

## Finding an event and its prices

Think down 4 levels: Event (Arsenal vs Chelsea) → Market (Match Winner) → Contract (Arsenal Win / Draw / Chelsea Win) → Order (your bet). You need the IDs from each level for the next.

Free lists, no login needed:
- GET https://api.smarkets.com/v3/events/ — what is on
- GET https://api.smarkets.com/v3/events/{ids}/states/ — is it open
- GET https://api.smarkets.com/v3/events/{ids}/competitors/ — teams / runners
- GET https://api.smarkets.com/v3/events/{ids}/markets/ — bet types for an event
- GET https://api.smarkets.com/v3/markets/{ids}/contracts/ — outcomes in a market
- GET https://api.smarkets.com/v3/currencies/{code}/ — FX rate

Live numbers, always send your login header:
- GET https://api.smarkets.com/v3/markets/{ids}/quotes/ — current order book
- GET https://api.smarkets.com/v3/markets/{ids}/last_executed_prices/ — what actually traded last
- GET https://api.smarkets.com/v3/markets/{ids}/volumes/ — how much traded
- GET https://api.smarkets.com/v3/accounts/ — balance, available, exposure

Website shows a price but quotes returns empty? Usually fine. The API shows only other customers' orders. The website can show extra pricing the API does not expose. Quiet live markets are often empty via API. Check last_executed_prices to see what really traded.

There is no push feed, webhook out, or websocket. Poll quotes on a timer instead. The old streaming address (stream.smarkets.com) is dead.

## Placing your first bet

POST https://api.smarkets.com/v3/orders/ with 5 required fields: `market_id`, `contract_id`, `price`, `quantity`, `side`.

**Side (which direction).**
- `buy` = back = you think it WILL happen.
- `sell` = lay = you think it WON'T happen.

**Price (odds) — not normal odds.**
Divide 10000 by the decimal odds you want. Want 2.0? Send 5000. Want 4.0? Send 2500. Want 10.0? Send 1000. Valid range 1 to 9999. Cheapest fix for a price rejection: copy a price straight from the quotes reply instead of typing your own.

**Quantity (stake) — not pounds.**
Multiply pounds by 10000. Want £2? Send 20000. Want £10? Send 100000. Minimum is 500 (£0.05). The top support ticket here: someone sends 800 expecting £2 — that is £0.08.

**Two optional fields worth using.**
- `type` — what happens if the market pauses or goes live. Leave blank and you get `good_til_halted` (carries into live, cancelled on any halt). Set `keep_in_play` to survive pauses like goals and VAR. Set `good_til_cancelled` for pre-match only. Set `immediate_or_cancel` to take what is available now or cancel the rest. For all-or-nothing, use `immediate_or_cancel` + set `minimum_accepted_quantity` equal to `quantity`.
- `label` — your own tag, e.g. "make-arsenal-1". Free text, great for finding bets later in Sheets.

**Live delays are normal.**
Horse racing and darts pause bets 4 seconds, everything else 8 seconds. During the delay your order is pending and invisible. Instant Match bets confirm over 8–14 seconds.

## Checking, cancelling, and your balance

- Check: GET https://api.smarkets.com/v3/orders/ shows open + recently settled. Status is created, partial, filled, or settled. Save the `order_id` from each place-bet reply — that is how you track it. The place-bet reply also tells you `total_executed_quantity` (how much matched instantly) and `executed_avg_price`.
- Cancel one: DELETE https://api.smarkets.com/v3/orders/{order_id}/ (10 per second).
- Cancel everything: DELETE https://api.smarkets.com/v3/orders/ — max once per 60 seconds, kills ALL open orders. Keep it off any auto-retry.
- Balance: GET https://api.smarkets.com/v3/accounts/ gives `balance`, `available_balance`, `exposure`. Available = balance minus exposure. "I have money but cannot bet" is almost always exposure locking it in open orders — cancel one to free it.

**Statement download.**
GET https://api.smarkets.com/v3/account_activity_csv/{start}/{end}/ needs exact hours: both times ISO format on the hour (2026-05-19T14:00:00Z), exactly 1 hour apart (14:00 to 15:00). Anything else fails. Reply is a gzipped CSV — in Make/n8n add a Gunzip step; in Zapier you may need a Code step or import to Sheets.

## Speed limits, in plain English

Overall: 1200 calls per 60 seconds per account, shared across every tool and server using that account. Seven calls have stricter caps:

- List events: 600 per 60 seconds.
- Price checks (quotes): 50 per 60 seconds once approved (lower before approval).
- Login: 5 per 5 minutes. Never put login on a fast loop.
- Logout: 30 per 60 seconds.
- Place bet: 10 per second.
- Cancel one: 10 per second.
- Cancel everything: 1 per 60 seconds.

How to stay under:
1. Batch. Quotes takes up to 200 market IDs in ONE call (comma-separated). 1500 markets = 8 calls, not 1500. Volumes, states, competitors take 300 per call. Contracts and last-prices take 100. Markets-by-event takes 50. Too many IDs gives a confusing 404 "Nothing matches the given URI" — count your IDs, the route is not dead.
2. One timer, not five. Five scenarios polling every 5 seconds unbatched = blocked. One scenario polling every 10 seconds batched = safe (about 6 calls a minute).
3. Cache. Do not re-check balance or event lists every poll if they barely change.

Hitting 429 (too fast)? Most errors include `count`, `limit`, `expiry` — wait until `expiry`, then halve your poll rate. Quotes and order/session errors carry a shorter 429 with no `expiry` — wait about 60 seconds and slow down. Repeat violations can suspend API access, so slow down first time.

## Errors — what to do

- 401 AUTH_REQUIRED — logged out, MFA missing, or 20-minute rotation. Log in again (and finish MFA verify if enabled). Check the header reads exactly `Authorization: Session-Token …`.
- 403 FORBIDDEN (JSON) — not approved, in 60-day review, revoked, or outside your approved markets. Check the fee went through. Email api@smarkets.com with the event/market IDs.
- 403 as a blocked HTML page, or codes SOURCE_BLOCKED / IP_NOT_TRUSTED — network-level block, common on cloud/VPS IPs or unsupported countries. Not a password problem. Prove it by running the same call from home. No self-serve fix — contact support; a server in an unsupported country must move.
- 400 bad fields — read the `data` field, it names the bad field. Check IDs came from the level above.
- 400 INVALID_DATETIMES — statement times not on the hour or not 1 hour apart.
- 404 NO_CSV_AVAILABLE / NO_RESULTS_FOUND — no data that hour, or IDs old. Try another hour / fresh IDs.
- 404 "Nothing matches the given URI" on a batch — too many IDs. Split to the caps above.
- 414 too many IDs — same, smaller batches.
- 451 country blocked — account or IP country not supported. Contact support if you moved.
- 500 / 503 / 504 (INTERNAL_ERROR, ZEUS_TIMEOUT…) — our side. Wait, retry once. Still failing → api@smarkets.com with time, endpoint, and code.

**Bet rejected? Match the code name:**
- INSUFFICIENT_FUNDS — available balance tied up in open orders. Cancel one or stake less.
- INVALID_PRICE — not on a valid tick. Copy from quotes.
- INVALID_QUANTITY — under 500 (£0.05). Increase it.
- MARKET_HALTED / TRADING_SUSPENDED — paused for a goal, VAR, withdrawal. Wait, re-check state, retry. Use `keep_in_play` next time to survive halts.
- RG_ACK_REQUIRED — open smarkets.com, complete the gambling acknowledgement popup, retry. Instant fix.
- KYC_PERMISSION_DENIED / ACCOUNT_UNVERIFIED — finish verification on the website.
- NO_DEPOSITS — fund the account first.
- STAKE_LIMIT_EXCEEDED — over your account stake limit. Contact support.

## Money and commission

Standard commission is 2% of net profit per market — only when you win that market. API access does not lower it, and API users cannot take the 0% new-customer offer or affiliate deals.

- Pro 1% is opt-in for volume (1500+ bets or £1M+ staked in a month — ask support once past 80% of either). It charges per matched bet on wins AND losses, so only take it at real volume. You can leave after 3 months.
- Select 3% is auto-applied with 7 days email notice if you clear £25k net profit over 12 months.

Payments are closed loop: withdraw to the same method you deposited with. Name on the payment method must match the account. If a withdrawal sticks, email support@smarkets.com.

## Rules that protect your account

Allowed: viewing prices and placing bets on approved markets, automating your own trading.

Not allowed: collecting large amounts of prices without betting, sharing or selling data, comparing prices/liquidity to sell elsewhere, hiding API calls as browser traffic, reverse engineering, extra accounts to dodge fees, latency arbitrage or court-siding.

Path if broken: warning, then temporary suspension, then permanent removal with bets voided. Serious cases skip to removal. Keep your email, password, and tokens secret — never paste them into shared templates, public Sheets, or client-side pages. If leaked: change your password on smarkets.com, DELETE your sessions, email support@smarkets.com.

Responsible gambling controls apply to API users too: deposit limits, timeouts (1, 7, 31, 42 days), self-exclusion (6 months to permanent, balance back within 48 hours, cannot reopen early).

## Getting help and example setups

Email API bugs, error codes, and limit questions to api@smarkets.com. Email account, money, ID, and application questions to support@smarkets.com.

Include four things (with secrets redacted): the full error (status + error_type + data, plus expiry if 429, plus whether a 403 body was JSON or HTML), the exact call (method + URL + field names), what you expected vs what happened, and when it started plus your poll rate and whether multiple tools share the account.

Setups that work well:
- Sheets tracker: Login → accounts → orders → write rows, every 15 minutes. Fresh login each run dodges the 20-minute rotation.
- Price alert: one timer → one batched quotes call (up to 200 IDs) → filter step → notify. Never one scenario per market.
- Auto-bet: trigger → check market state (open?) → check accounts (enough available?) → place order with label → log order_id. Add: on 401, re-login once and retry once, then alert and stop. Never loop.

*Not covered here? Email api@smarkets.com with the four items above. Full endpoint reference stays at https://docs.smarkets.com/.*
