# Smarkets API for No-Code Builders — The Full FAQ

*For Zapier, Make, n8n, Bubble, Google Sheets users. No coding needed. If you can copy a URL, a header and a few field names exactly, you can use this API.*
*There is no official Zapier app, Make app or SDK. You use each tool's generic "HTTP request / API call" module.*
*Checked against live docs Oct 2026. If this page and docs.smarkets.com disagree, docs.smarkets.com wins.*

## How to use this page

- New here? Read top to bottom once: What it is -> Getting access -> First login -> First price check -> First bet.
- Stuck? Ctrl+F / Cmd+F the error or code name (401, 403, 429, INSUFFICIENT_FUNDS, INVALID_DATETIMES).
- Building? Jump to Speed limits and the three working setups at the end.

## All the links in one place

- Interactive API docs (read + try every endpoint in your browser): https://docs.smarkets.com/
- Raw spec (for the curious): https://api.smarkets.com/v0/control/openapi/?tags=trading_api
- API Request Form (how you apply): https://support.smarkets.com/p/6MLL-PL7/api-request-form
- API rules (Access, Integration and T&Cs — the binding version): https://help.smarkets.com/hc/en-gb/articles/34697834941085-Smarkets-API-Access-Integration-T-Cs
- Commission explained: https://help.smarkets.com/hc/en-gb/articles/212654665-Smarkets-commission-FAQ
- Help Centre (betting rules, general help): https://help.smarkets.com/hc/en-gb
- The API itself (every call starts with this): https://api.smarkets.com
- API tech help (bugs, error codes, limits): api@smarkets.com
- Account, money, ID, application help: support@smarkets.com

Save both emails now. You will need them.

---

# PART 1 — WHAT IT IS

## What is the Smarkets API?

A way for your tools to talk to the Smarkets exchange directly instead of you clicking the website.

With it you can check live prices, place and cancel bets, check your balance and exposure, and download your statement — all from an automation.

In plain words: your tool sends a web address plus some fields. Smarkets sends a structured reply back. That is all "REST + JSON" means.

- REST = you call a URL with a method (GET = read, POST = place, DELETE = cancel).
- JSON = the reply is labelled data like `{"balance": 100000}`. Your tool parses it into fields you can map.

## Is it the exchange or SBK?

The API is for the Smarkets exchange only.

- Smarkets exchange = you bet against other customers. You can back AND lay. Prices come from other users' orders. Commission applies.
- SBK = Smarkets' sportsbook app. You bet against the house. No lay side, no order book, no API.

Same login can work on both (ask support to enable dual access) but balances and products are separate. If your's strategy mentions Bet Builders, accas, cash out or free bets, that is SBK language — the API does not do those. The API does singles on the exchange: back or lay one outcome at a time.

## What can I do with it?

- List events, markets, outcomes and competitors.
- Read live prices, last matched prices and traded volumes.
- Place, list and cancel exchange orders.
- Read balance, exposure and account activity.
- Automate your own trading on markets approved for your account.

## What can I NOT do with it?

- No test mode with fake money. Every bet is real money.
- No read-only or data-only plan. One product: prices + betting together.
- No push feed, webhook out, websocket or streaming. Poll on a timer instead. The old streaming address (stream.smarkets.com:3801) is dead.
- No multiples, accas, Bet Builders or cash out via API. Those are SBK/website features.
- No collecting large amounts of prices without betting, no sharing or selling data, no comparing prices to sell elsewhere, no hiding API calls as browser traffic, no reverse engineering, no extra accounts, no latency arbitrage or court-siding. Full list in Rules below. Breaks go warning -> suspension -> closure.

## Is it for me?

Yes if:

1. You have a no-code tool with a generic HTTP module (names below).
2. You can copy values exactly — one wrong letter in a header or field name fails.
3. You have or will open a fully verified Smarkets exchange account and pay the £150 setup fee.

No if you only place bets by hand. Use the website or app — cheaper and faster.

## Which button do I click in my tool?

Same idea everywhere, different label:

- Zapier: "Webhooks by Zapier" -> "Custom Request".
- Make: "HTTP" -> "Make a request".
- n8n: "HTTP Request" node.
- Bubble: "API Connector" plugin.
- Google Sheets: Extensions -> Apps Script with `UrlFetchApp.fetch()` (needs a few lines of script — ask for help or use Make/Zapier instead).

Every call needs four things: Method (GET/POST/DELETE), URL, Headers, Body (for POST). Login gives you a token. Every call after that adds one header with that token.

---

# PART 2 — GETTING ACCESS (ONBOARDING)

## Who can apply?

- 18+ (21+ in the US), in a supported jurisdiction (UK, Ireland, Malta, Sweden plus others — ask if unsure).
- Fully registered and verified Smarkets exchange account.
- Not self-excluded, not on a gambling timeout, not a Smarkets employee/contractor.
- Able to describe what you will build in plain words.

Smarkets can still refuse or revoke access at its discretion, even if you tick every box. Approval is not guaranteed.

## How much does it cost?

- £150 one-off setup fee (or equivalent in your currency). Taken from your balance when approved, not when you apply. You need at least £150 in the account.
- Refundable if you permanently quit API use within 60 days — email support@smarkets.com to withdraw.
- After that: normal exchange commission on winnings. No API discount. API users cannot take the 0% new-customer offer or affiliate deals.

Some use cases can carry extra fees or restrictions (see Section 5 of the API T&Cs). Smarkets can change commercial terms with notice — continuing to use the API after a change means you accept it.

## Your journey step by step

**Step 1 — Create and verify your Smarkets account.**
Do this before anything else at smarkets.com. Electronic checks run first (does not affect credit score). If they fail, upload documents:

- Photo ID: passport, driving licence with photo, or national ID card. Photo or scan, all four corners visible, not angled. Screenshots not accepted.
- Proof of address: bank/building society statement, utility bill (both within 3 months), or council tax / tax bill (current year), or residency certificate (3 months). Paper or PDF. Screenshots not accepted. Mobile phone bills not accepted.
- You cannot use the same document for ID and address.
- Smarkets document review target: within 72 hours. Busy periods slip.
- You may also be asked for source of funds / wealth later (payslips, bank statements, savings). Standard regulation, not personal. You can decline but the account will be restricted.

Until verification completes you can hit deposit blocks, bet blocks or login blocks. Finish it on the website — the API starts working by itself after, no setup change needed.

**Step 2 — Fund the account.**
Deposit at least enough to cover the £150 fee plus your first stakes. Visa Debit or Instant Bank Transfer is simplest (instant, free, £10 min). Deposits must be in your account currency and from a payment method in your own name. See Money movement below for closed-loop withdrawals.

**Step 3 — Skim the docs.**
Open https://docs.smarkets.com/ and confirm your plan fits "viewing prices and placing bets". If your plan is really "collect prices for a model / website / Discord group" without betting, stop — that breaches the T&Cs.

**Step 4 — Apply via the Request Form.**
https://support.smarkets.com/p/6MLL-PL7/api-request-form
Write 3-5 plain sentences: what you will build, which tool, which sports/markets, roughly how often you will check prices and how many bets. Example: "Make scenario checking 50 pre-match football markets every minute, placing 5-10 back bets a day, plus a Sheets log every 15 minutes." That is enough. You must keep Smarkets updated if the setup changes a lot later.

**Step 5 — Wait for approval.**
Reviewed case by case, no fixed SLA. You can use the website while you wait. If it has been a while, nudge api@smarkets.com (tech) or support@smarkets.com (account/application). Once approved the £150 leaves your balance and API access activates.

**Step 6 — 60-day compliance review.**
Every new API account gets one. You can trade during it. Some restrictions can apply. You do nothing unless contacted.

**Step 7 — Build in this order: login -> balance check -> price check -> bet.**
Do not start with auto-betting. Prove login, then prove you can read, then place one small manual-triggered bet (£0.05-£1), then automate.

## What do I get when approved?

No API key in the post. You log in with your normal Smarkets email + password. The login reply contains a temporary `token`. That token IS your key for the next calls.

---

# PART 3 — MONEY AND COMMISSION (READ BEFORE YOU BET)

## What commission do I pay?

Standard: 2% of net profit per market. Only when you win that market. Losing markets pay nothing. Calculated per market, not per bet — three bets on one market net off first, commission on the net.

API access does not lower it. Website, app and API all pay the same tiers.

## The three tiers

- Standard 2% — everyone starts here. Net profit per market only.
- Pro 1% — opt-in for volume. Needs 1,500+ bets OR £1M+ staked in a calendar month. You can ask once past 80% of either. Contact support to opt in — it is never automatic, you can stay on 2% if you prefer. Different maths: charged per matched bet on wins AND losses, not net per market. Only worth it at real volume. Leaving needs 3 months. Opting in forfeits any commission promotion permanently.
- Select 3% — auto-applied with 7 days email notice if you clear £25k net profit over the previous 12 months. Review possible if P&L drops back below £25k (ask support, discretionary). Also forfeits promotions.

Check yours via GET /v3/accounts/ -> `commission_type`: "0.02" = Standard, "0.01" = Pro, "0.03" = Select.

Worked example (Standard): back £10 at 3.0, wins -> profit £20, commission £0.40, you keep £19.60 profit. Lay side equivalent nets the same way per market.

## Promos?

API users are ineligible for the 60-day 0% new-customer offer and affiliate commission offers. Do not plan around them.

---

# PART 4 — YOUR FIRST LOGIN (DO THIS ONCE, REUSE FOREVER)

## The idea in one paragraph

Login with email + password -> save the `token` from the reply -> paste it into a header on every other call. Token lasts about 30 minutes of use and rotates about every 20 minutes (see below). Logout when done. That is the whole auth system.

## Call 1 — Login

- Method: POST
- URL: https://api.smarkets.com/v3/sessions/
- Header: `Content-Type: application/json`
- Body:
```json
{
  "username": "your.email@example.com",
  "password": "yourpassword"
}
```

Notes that fix 90% of first-login failures:

1. Field MUST be called `username` even though the value is your email. `email` fails with REQUEST_VALIDATION_ERROR.
2. Success is HTTP 201, not 200. Set your tool to accept 200 OR 201 or a working login shows as failed.
3. Read the field called `token` (long string). Not `session_token`. Save it to a variable / Data Store.
4. The reply also contains `refresh_token`, `stop` (expiry hint) and `verify`/`factor` (MFA status). Save `refresh_token` too if your tool supports cookies (see 20-minute note).

In Sheets Apps Script the same call is `UrlFetchApp.fetch(url, {method: "post", contentType: "application/json", payload: JSON.stringify({username: email, password: pw})})` then `JSON.parse(resp).token`.

## Every call after — attach the token

- Header: `Authorization: Session-Token YOUR_TOKEN`
- Exact words `Session-Token`, one space, then token. Not `Bearer`. Not `X-Smarkets-Token`. Not in the URL. Not in the body.

Prove it with a balance check: GET https://api.smarkets.com/v3/accounts/ + that header. Returns `account_id`, `balance`, `available_balance`, `exposure`, `currency`, `commission_type`, `signup_date`. If balance comes back, login works.

## MFA (authenticator app) users

Login returns a limited token. Add one call before anything else:

- POST https://api.smarkets.com/v3/sessions/verify/ + your current 6-digit code.

Then place bets. Symptom you skipped this: login looks fine but every order returns 401.

Lost your MFA device? Email support from your registered address with proof of ID to disable it.

## Logout

- DELETE https://api.smarkets.com/v3/sessions/ with the same Authorization header.
- Limit 30 per 60 seconds. Optional but tidy for scheduled runs. Scheduled-every-15-min setups often just login -> work -> logout each run.

## How long does login last?

About 30 minutes, renewed by each authenticated call — but tokens also rotate on a ~20 minute cycle (verified live Oct 2026: header-only setups die around 19-20 min even while polling).

- Short runs (under 15 min): ignore. Fresh login each run dodges it entirely.
- Long runs: add a branch — on any 401, run Login once, replace the stored token, retry that step once, then stop and alert if it fails again. Never loop login.
- Advanced (n8n / code): send `Cookie: User-Session-Token=<token>; Refresh-Token=<refresh_token>` with every call and adopt each renewed `User-Session-Token` from responses. Log response cookies — the rotation is only visible there.
- Never hammer login to work around expiry: 5 tries per 5 minutes, then 429 lockout for ~4-5 min. During debugging that burns fast.

## Login errors — matcher

- INVALID_CREDENTIALS (401) — email or password wrong. Reset on smarkets.com.
- PASSWORD_RESET_NEEDED (401) — reset on smarkets.com first.
- INVALID_TOKEN (400) — wrong MFA code. Generate a fresh 30-second code.
- DEVICE_NOT_TRUSTED / IP_NOT_TRUSTED (403) — finish device trust on smarkets.com.
- SESSION_LIMIT_REACHED (403) — too many open sessions. Logout elsewhere first.
- USER_SUSPENDED (403) — contact support@smarkets.com.
- USER_SELF_SUSPENDED / USER_ON_TIMEOUT / USER_EXCLUDED (403) — timeout or self-exclusion active. Wait it out or contact support.
- SOURCE_BLOCKED / CLIENT_JURISDICTION_MISMATCH (403) — source or country mismatch. Contact support.
- COUNTRY_BLOCKED (451) — Smarkets not licensed there. No workaround — a server in that country must move.
- 429 on login — you hit 5 per 5 min. Wait for the window, check the `expiry` time.

---

# PART 5 — FINDING EVENTS, MARKETS AND PRICES

## The 4 levels (learn once)

1. Event — the thing happening (Arsenal vs Chelsea).
2. Market — what you can bet on in it (Match Winner, Over/Under 2.5 Goals).
3. Contract — the outcome (Arsenal Win / Draw / Chelsea Win).
4. Order — your bet on a contract.

You walk down: get event ID -> get its markets -> get a market's contracts -> place order on a contract. Wrong ID at any level = 404.

## Which call for what

Free lists (no login needed):

- GET /v3/events/ — what is on. Filter via query params in docs.
- GET /v3/events/{ids}/states/ — open / halted / settled. Check before betting.
- GET /v3/events/{ids}/competitors/ — teams, runners, participants.
- GET /v3/events/{ids}/markets/ — markets for events (max 50 IDs per call).
- GET /v3/events/{ids}/markets_count/ — how many markets each event has.
- GET /v3/markets/{ids}/contracts/ — outcomes in a market (max 100 IDs per call).
- GET /v3/currencies/{code}/ — FX rate (codes: AUD BRL CAD CHF CZK DKK EUR GBP HKD HUF JPY NOK PLN SEK USD).

Live numbers (always send your login header):

- GET /v3/markets/{ids}/quotes/ — current order book (best bid/ask + depth).
- GET /v3/markets/{ids}/last_executed_prices/ — what actually traded last + when.
- GET /v3/markets/{ids}/volumes/ — how much traded.
- GET /v3/orders/ — your open + recently settled orders.
- GET /v3/orders/fullcover/ — fullcover orders if any (a multiple-bet type; cannot be placed on Smarkets, list only).
- GET /v3/accounts/ and GET /v3/accounts/activity/ — balance and paginated statement.

Full URLs are https://api.smarkets.com + path, e.g. https://api.smarkets.com/v3/events/

IDs are comma-separated lists in the URL: `/v3/events/id1,id2/states/`. One call can carry many IDs up to that endpoint's cap (see Speed limits).

## Walkthrough: price for one football match

1. GET /v3/events/ -> find "Arsenal vs Chelsea", note `id` e.g. 12345.
2. GET /v3/events/12345/markets/ -> find "Match Winner", note `market_id`.
3. GET /v3/markets/{market_id}/contracts/ -> note three `contract_id`s (Home/Draw/Away).
4. GET /v3/markets/{market_id}/quotes/ with login header -> live book. Pick a price from here for your order.
5. GET /v3/events/12345/states/ -> confirm open before placing.

Do the same walkthrough once by hand in docs.smarkets.com (it fills your token for you), then copy the working URLs into your tool.

## Empty quotes but website shows a price?

Usually fine, not broken. Quotes shows only other customers' peer-to-peer orders. The website can show extra pricing sources the API does not expose. Thin in-play markets are often empty via API. Cross-check last_executed_prices for what really traded. If still confused, email api@smarkets.com with the market ID.

## Can I get prices pushed to me?

No. No webhooks out, no websocket, no streaming. REST polling on a timer is the only documented way. Anyone mentioning sio-live or stream hosts found via DevTools is looking at website internals, not the API — do not build on them.

---

# PART 6 — PLACING YOUR FIRST BET

## The call

- POST https://api.smarkets.com/v3/orders/ + Authorization header + JSON body with 5 required fields: `market_id`, `contract_id`, `price`, `quantity`, `side`.

Minimal example (back £2 at 2.0):

```json
{
  "market_id": "123456",
  "contract_id": "789",
  "price": 5000,
  "quantity": 20000,
  "side": "buy",
  "type": "good_til_halted",
  "label": "make-arsenal-1"
}
```

`type` and `label` are optional but you should use them (see below).

## Side: buy vs sell

- `buy` = back = WILL happen ("Arsenal will win").
- `sell` = lay = WON'T happen ("Arsenal won't win"). Lay ties up liability — needs enough available balance.

Migrating from Betfair? buy=BACK, sell=LAY. There is no `time_in_force` field — Smarkets uses `type` + `minimum_accepted_quantity` instead.

## Price: the odds conversion

API price is NOT decimal odds. Formula: decimal odds = 10000 / price.

| You want | Send | Maths |
|---|---|---|
| 1.11 (heavy favourite) | 9000 | 10000/9000 |
| 1.39 | 7194 | 10000/7194 |
| 2.0 (evens) | 5000 | 10000/5000 |
| 4.0 (3/1) | 2500 | 10000/2500 |
| 10.0 (9/1) | 1000 | 10000/1000 |

Valid 1 to 9999 and must sit on a valid exchange tick (not every number valid). Rejected with ORDER_INVALID_INVALID_PRICE? Copy a price from quotes instead of typing your own.

## Quantity: the stake conversion

API quantity is in 1/10,000ths of your currency. Pounds = quantity / 10000.

| You want | Send |
|---|---|
| £0.05 (minimum) | 500 |
| £0.08 | 800 |
| £1 | 10000 |
| £2 | 20000 |
| £10 | 100000 |

Max is 4294967295 (32-bit limit — you will never hit it). Back-stake maths from the spec: quantity x price / 100000000. Example: 100000 x 5000 / 100000000 = £5 back stake.

Top ticket of all time: "I sent 800 expecting £2." 800 IS £0.08. For £2 send 20000.

## Type: what happens when things change

Leave blank -> `good_til_halted`.

| Type | Market goes live | Market halts | Use when |
|---|---|---|---|
| `good_til_halted` (default) | Kept | Cancelled | Normal pre-match into live |
| `keep_in_play` (KIP) | Kept | Kept, resumes after | You want to survive pauses (goals, VAR) |
| `good_til_cancelled` | Cancelled | Cancelled | Pre-match only, never carry live |
| `immediate_or_cancel` (IOC) | Fills now or cancels rest | — | Take what is available now, do not queue |

Only KIP survives a halt. Do not assume "my orders stay in the book" — only KIP does.

Fill-or-kill = IOC + `minimum_accepted_quantity` = `quantity` (all or nothing). Fill-at-least-X = IOC + `minimum_accepted_quantity` lower than quantity. Always set it explicitly on IOC — omitting it can accept a zero fill. No `time_in_force` field exists.

## Label: tag everything

Free text like "zapier-arsenal-1" or "make-strategy-B-2026-10-17". Shows in order history. Costs nothing, saves hours when filtering in Sheets or debugging two strategies sharing one account.

## What the reply tells you

POST reply includes: `order_id` (save it — how you track/cancel), `total_executed_quantity` (how much matched instantly — key for IOC), `executed_avg_price` (null if nothing matched), `available_balance`, `exposure`, plus echo of price/quantity/side/contract/market.

It does NOT include `quantity_filled` or `state` — those only come from GET /v3/orders/ (states: created, partial, filled, settled).

## Live delays are normal

- Horse racing + darts: 4 seconds. Everything else: 8 seconds. During delay your order is pending and invisible — not an error.
- Instant Match: 8-14 second confirmation instead of a delay.
- You cannot place new orders while a market is halted. In-play markets with a delay are NOT halted for every goal/penalty/red — the delay absorbs them.

---

# PART 7 — CHECKING, CANCELLING, BALANCE

## Check my bets

GET https://api.smarkets.com/v3/orders/ -> open + recently settled. Each has `quantity_filled` and `state` (created / partial / filled / settled). Filter by your `label` in Sheets.

Placed but not showing? It filled instantly (check last_executed_prices), or was cancelled because the market closed/halted, or you are looking at the wrong account/environment.

## Cancel

- One: DELETE https://api.smarkets.com/v3/orders/{order_id}/ (10 per second).
- All: DELETE https://api.smarkets.com/v3/orders/ — max 1 per 60 seconds, kills EVERYTHING open. Never wire this to auto-retry or a flapping trigger.
- Cannot cancel? Order already filled/cancelled/settled, wrong ID, or not yours. Check GET first. After settlement nothing can be cancelled. Re-sending cancel for an already-cancelled order succeeds silently.

## Balance, exposure, available

GET https://api.smarkets.com/v3/accounts/ fields: `balance` (total), `exposure` (locked in open orders), `available_balance` (balance minus exposure — what you can actually stake), `bonus_balance`, `commission_type`, `currency`, `account_id`, `signup_date`.

"I have money but cannot bet" = exposure. Cancel an open order to free it.

## Statement

- Paginated: GET https://api.smarkets.com/v3/accounts/activity/ (params timestamp_max, offset, limit). Good for "last N transactions" in Sheets.
- CSV hour: GET https://api.smarkets.com/v3/account_activity_csv/{start}/{end}/ — strict: both ISO 8601 on the hour (2026-05-19T14:00:00Z), exactly 1 hour apart. Else 400 INVALID_DATETIMES. No data that hour -> 404 NO_CSV_AVAILABLE. Reply is gzipped CSV: Make/n8n add a Gunzip/Decompress step; Zapier needs a Code step or Sheets import; Bubble needs a file handling plugin.

---

# PART 8 — SPEED LIMITS (READ BEFORE YOU POLL)

## The two layers

- Global: 1200 calls per 60 seconds per account, across ALL endpoints and ALL tools/servers sharing that account. Unauthenticated public calls (no token) do not count against it — but you need auth for live prices anyway.
- Per-endpoint stricter caps on 7 endpoints. These fire first.

| Call | Cap | What it means for no-code |
|---|---|---|
| List events GET /v3/events/ | 600 / 60s | Fine normally |
| Prices GET quotes | 50 / 60s approved (about 20 if not yet approved) | Your main constraint |
| Login POST /v3/sessions/ | 5 / 300s | Never loop login |
| Logout DELETE /v3/sessions/ | 30 / 60s | Fine |
| Place POST /v3/orders/ | 10 / second | Fine unless bursting |
| Cancel one DELETE /v3/orders/id/ | 10 / second | Fine |
| Cancel all DELETE /v3/orders/ | 1 / 60s | Keep off retry |

Everything else shares the 1200 pool with no individual cap.

Responses can carry `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` (seconds to reset; occasionally negative/missing — wait at least 5s). Log them in n8n/Make for tuning.

## Hitting 429 (too fast)

- Most GETs return structured 429 with `count` (used), `limit` (cap), `expiry` (when window resets, RFC 2822 date). Stop until `expiry`, then halve your rate.
- Quotes, orders and sessions return a shorter 429 WITHOUT count/limit/expiry. Wait ~60s and slow down.
- Seeing a lower limit header than docs (e.g. 20 not 50 on quotes)? Header is ground truth for your account tier — usually means not yet approved as API user. Approval lifts it. Approved but still wrong? Email api@smarkets.com.
- Repeat violations can suspend then permanently revoke API access. Slow down first time, every time.

## Batching: the single biggest win

Every list endpoint takes many IDs in ONE call. Bigger batch = fewer calls.

| Call | Max IDs per call |
|---|---|
| quotes | 200 |
| volumes | 300 |
| event states | 300 |
| competitors | 300 |
| contracts | 100 |
| last_executed_prices | 100 |
| markets by event | 50 |
| markets_count | 50 |

Maths: 1,500 markets at 200 per call = 8 calls per sweep. At 50 calls/min that is a full refresh about every 10 seconds. Same 1,500 at 1 per call = blocked instantly.

Over the cap gives a confusing 404 `{"error_type":"NOT_FOUND","data":{"description":"Nothing matches the given URI"}}`. Count your IDs — the route is not dead, your batch is too big. Verified live: quotes 200 OK / 201 fails; volumes 300 OK / 301 fails.

Before asking for a limit increase, double your batch first — it usually removes the need. Increases are discretionary and currently rarely granted; ask via api@smarkets.com with your use case, batch size and volumes, and expect to be asked to batch first.

## Polling recipes

Safe: 1 scenario polling quotes every 10s batched at 200 = 6 calls/min. Huge headroom.

Blocked: 5 scenarios each polling every 5s unbatched = 60+/min on quotes alone, plus balance checks. Merge into one timer scenario that fans results out (Router in Make, Loop in n8n, Paths in Zapier).

Sharing one account across Zapier + Make + VPS stacks against the same 1200. Give each job its own cadence and a shared sheet for last-poll time if needed.

Cache what barely changes (event lists, contracts) for minutes; poll only quotes/balance fast. Prefer batch endpoints over one-ID loops. Never poll login, never poll cancel-all.

---

# PART 9 — ERRORS (FIND YOURS, FIX IT)

Status codes: 2xx = worked (200 OK, 201 created). 4xx = your request needs fixing. 5xx = Smarkets side, wait and retry.

## Quick matcher

- 401 AUTH_REQUIRED — token missing/expired/MFA missing/20-min rotation. Re-login (full flow), finish MFA verify, check header exactly `Authorization: Session-Token …`. Long jobs: re-login-once-then-retry-once branch.
- 403 FORBIDDEN (JSON `error_type: FORBIDDEN`) — account permission. Not approved / in 60-day review / revoked / outside approved markets / endpoint blocks below. Check fee paid + approval. Email api@smarkets.com with IDs.
- 403 HTML page (starts `<!DOCTYPE`, Cloudflare) or codes SOURCE_BLOCKED / IP_NOT_TRUSTED — network edge block, common on datacentre/VPS/cloud IPs or unsupported country. Not a password problem. Prove by running same call from home. No self-serve unblock. Contact support; server in unsupported jurisdiction must move.
- 400 REQUEST_VALIDATION_ERROR — wrong field/ID/price. Read `data` — it names the bad field. IDs must come from the level above. Login with `email` instead of `username` fails here.
- 400 BAD_REQUEST — malformed market/price params. Same fix.
- 400 INVALID_DATETIMES — CSV times not on hour / not 1h apart. Snap to `:00:00Z`, end = start + 1h.
- 400 RECKONATOR_REQUEST_TOO_LARGE — activity query too broad. Narrow dates.
- 404 NO_CSV_AVAILABLE — no statement data that hour. Try another hour.
- 404 NO_RESULTS_FOUND — states query matched nothing. Check IDs current.
- 404 "Nothing matches the given URI" on a batch — too many IDs. Split to caps above.
- 414 REQUEST_TOO_LARGE — too many IDs. Same, smaller batches.
- 429 RATE_LIMIT_EXCEEDED — too fast. Wait to `expiry` (or ~60s for quotes/orders/sessions), batch more, poll slower.
- 451 COUNTRY_BLOCKED — account or IP country unsupported. Contact support if you moved.
- 500 INTERNAL_ERROR / 503 / 504 ZEUS_TIMEOUT — Smarkets side (trading engine timeout etc). Wait, retry once with backoff. Still failing with timestamp + endpoint + code -> api@smarkets.com. Note the subsystem code (e.g. EVENTS_UNAVAILABLE) — it tells engineering where to look.

## Bet rejected? Match the code name

- ORDER_REJECTED_INSUFFICIENT_FUNDS — available tied in exposure. Cancel an order or stake less. Check GET /v3/accounts/ available, not total.
- ORDER_INVALID_INVALID_PRICE — not on tick. Copy from quotes.
- ORDER_INVALID_INVALID_QUANTITY — under 500. Increase.
- ORDER_REJECTED_MARKET_HALTED / ORDER_CANCELLED_MARKET_HALTED / TRADING_SUSPENDED — paused (goal, VAR, withdrawal, halt). Wait, re-check states, retry. Next time use keep_in_play to survive halts.
- ORDER_REJECTED_MARKET_SETTLED / CONTRACT_SETTLED / MARKET_NOT_OPEN / MARKET_NOT_FOUND / CONTRACT_NOT_FOUND — market done or wrong ID. Re-fetch events -> markets -> contracts.
- ORDER_REJECTED_STAKE_LIMIT_EXCEEDED / LIMIT_EXCEEDED / CAPACITY_REACHED — over account/market cap. Contact support.
- ORDER_REJECTED_CROSSED_SELF — would match your own order. Change price.
- ORDER_REJECTED_THROTTLE_EXCEEDED — placing too fast. Slow to under 10/s.
- RG_ACK_REQUIRED (403) — do the gambling acknowledgement on smarkets.com (popup, try a market page if hidden). Instant fix, no setup change.
- KYC_PERMISSION_DENIED / ACCOUNT_UNVERIFIED (403) — finish verification on website.
- NO_DEPOSITS (403) — fund first.
- ACTION_BLOCKED / ACCOUNT_SUSPENDED (403) — contact support.
- CREATE_ORDER_TIMEOUT / ORDER_UNAVAILABLE / AUTH_UNAVAILABLE / KYC_SERVICE_* (503) — subsystem down. Wait, retry once, escalate with code if persistent.

## Cancel rejected?

Order already filled/cancelled/settled, wrong UUID, or not yours. GET first. After settlement nothing cancels. Re-cancel of an already-cancelled order succeeds silently — safe to retry once.

---

# PART 10 — BETTING RULES YOU WILL ACTUALLY HIT

Full rules: Help Centre -> Betting Rules (General 1-11 + sport). Below is what breaks automations.

- Settlement: ASAP after the official result from the governing body on the day. Later amendments do not change it. Can be delayed if uncertain, voided if unresolvable, resettled if settled in error or new info (disqualification, cheating) emerges.
- Voids (all voided -> stake back): event cancelled, not concluded within 36h of scheduled start, postponed more than 36h past original start, change of opponents or venue, modified event length. Change of surface alone does NOT void. Dead heats split winnings proportionately.
- Football default: 90 minutes + stoppage only. Extra time/penalties do NOT count unless stated (exception: "To Advance" includes them). Own goals do not count for goalscorer markets. Cards: yellow 1, straight red 2, two yellows + red 3, max 3 per player; subs/managers do not count. Abandoned -> void unless already decided (e.g. half-time result if abandoned second half); if no resumption news within 3h, undecided bets voided.
- Tennis: first set not completed -> all void (except already-decided lines). Retirement after set one -> retiree loses Match Winner, Set Betting voided. Venue/surface change -> bets stand. Final-set Championship Tie Break counts as 1 game.
- Horse racing: first past the post then weighed-in result counts; later appeals ignored. Non-runner -> bets on it voided; if places >= runners all voided. Ante-post stands run or not. Place terms by runners: 5-7 pays 2, 8-15 pays 3, 16+ non-handicap 3, 16+ handicap 4 (market name wins if different).
- Reduction factors (non-runner): New odds = Old odds x ((100 - RF) / 100). Example 4.0 with 25% RF -> 3.0. Win market: RF under 2.5% -> stands; 2.5%+ -> matched adjusted, unmatched cancelled, market reopened. Place market: ANY RF adjusts winnings, unmatched cancelled. Can apply after the race if a non-runner is found late.
- In-play: delays 4s racing/darts, 8s everything else. Markets with a delay are NOT halted for every goal/penalty/red — the delay covers it. Instant Match has 8-14s confirmation; a material event inside it can void the bet. Betting after the outcome is known is voided. Keep Bets In-Play must be set per bet (Rule 10) — unmatched non-KIP dies at halt but keeps queue if KIP.
- Trade out (exchange) is per contract and never guaranteed — fails if suspended or odds moved. SBK cash out is a different product (full bet, house counter-bet).
- Clearly erroneous bets: report within 60 minutes to support@smarkets.com with time, contract/market, matched price and reason, before the result stands (unless exceptional). Outliers beyond ±20% of fair price can be looked at later at Smarkets' discretion. If the other side already traded out you can remain liable for the difference.

Why was my bet voided? Walk: abandoned/cancelled/36h? -> non-runner RF? -> bet-builder leg voided (same-event builder: ANY voided leg voids the WHOLE bet, stake back, even if other legs lost; cross-event: voided leg just reduces odds)? -> erroneous? -> resettled in error?

---

# PART 11 — ACCOUNT, MONEY MOVEMENT, SAFER GAMBLING

## Deposits

Free, mostly instant, £10 min (£25 for PayPal), in your account currency, from your own method. Visa Debit or Instant Bank Transfer recommended. Bank Transfer takes 5-10 business days. E-wallets (Skrill/Neteller) cap lower per transaction. Name must match the account or it fails.

Set deposit limits at smarkets.com Settings -> Limits (daily/weekly/monthly, net and/or gross). Lowering is instant. Raising needs a cooling period (~72h). UK defaults can apply (£4,999.99 monthly net + £1,000 daily net for newer accounts; raising can need proof of income).

## Withdrawals + closed loop (why withdrawals "stick")

Withdraw to the SAME method you deposited with (anti-money-laundering law, not optional). Per method: Net Deposits = Deposits - Withdrawals. You must zero each positive method before skimming profit elsewhere.

Example: deposit £100 Visa + £50 Mastercard. To take £150 to Mastercard, first withdraw £100 to Visa (zeroing it), then move the rest.

Timings: Instant Bank Transfer ~12h, Trustly/e-wallets 1-2 days, cards 1-6 days, Bank Transfer 5-10 days (£20 min, last resort when nothing else works, currency must match, needs statement + verification). E-wallets: 4th+ withdrawal in 7 days takes 24h. Some Mastercards only return net deposits — profit must leave another way. Card gone? Deposit min with the new card then ask support to remove the old (may need bank statements + card photo showing first 6/last 4 + name/expiry only).

Stuck? Check: above minimum? Withdrawing to deposit method? Card used too many times in 12h? Address/country changed? Deposited via a removed method? Else add a fresh Instant Bank Transfer deposit or ask support about bank transfer.

## Timeouts, self-exclusion, RG

Same controls on API as website — no exemption.

- RG_ACK_REQUIRED: do the acknowledgement popup on smarkets.com (try a market page). Lifts instantly.
- Timeout: 1, 7, 31 or 42 days. Locks everything including cashier withdrawals (contact support to pull funds mid-timeout). Auto-reopens. Cannot be undone early.
- Self-exclusion: 6 months, 1 year, 5 years or permanent. Balance back within 48h. Never reopens early; when a fixed term ends you must contact support to reopen (not automatic). Permanent never reopens.
- Deposit/loss/stake limits in Settings -> Limits.
- UK multi-operator exclusion: GAMSTOP. Blocking software: GamBlock, BetBlocker, NetNanny. Help: Gamblers Anonymous, GamCare, GambleAware, NHS, National Problem Gambling Clinic, Gambling Therapy; US 1-800-GAMBLER.
- Source of funds/wealth or affordability checks can land anytime: job/income, payslips/P60/SA302, card/bank/savings statements, solicitor letter for property. Smarkets never contacts your employer. Provide or face restriction.

---

# PART 12 — RULES THAT PROTECT YOUR ACCOUNT

Allowed: viewing prices and placing bets on approved markets, automating your own trading. Tell Smarkets if the setup changes materially.

Banned (API T&Cs Sections 2/5/6/7): odds scraping, concealing API calls as browser traffic, browser impersonation, reverse engineering, requesting lots of data without matching trading, sharing/selling/distributing prices/market/event data without written approval, benchmarking markets/prices/liquidity/systems, extra accounts to dodge fees/commission (fraud), latency arbitrage, court-siding, anything Smarkets deems harmful to the exchange.

Monitored: request patterns, data-to-trade ratios, trading behaviour, rate-limit circumvention. Do not circumvent limits to the detriment of others.

Penalties: warning -> temporary suspension -> permanent API/account removal, plus bets voided/transactions cancelled and possible legal action. Serious (fraud, data theft) can skip to removal. Access can be withdrawn anytime without notice; Smarkets is not liable for losses from restricted access.

Security is on you: email, password, tokens. Never in shared templates, public sheets, client-side pages or public repos. If leaked: change password on smarkets.com immediately, DELETE sessions, email support@smarkets.com. No account sharing — one person per account.

---

# PART 13 — GETTING HELP + WORKING SETUPS

## Who do I email?

- API bugs, error codes, limits, batching, auth: api@smarkets.com
- Account, payments, verification, application, RG, closed loop: support@smarkets.com
- SBK app (not API): support@getsbk.com, live chat 09:00-23:00 GMT logged in, phone +44 207 617 7413 (09:00-19:00).
- Outages: status.smarkets.com and @SmarketsTech.

## What to include (copy this template)

1. Full error: status + `error_type` + `data` (+ `expiry` if 429) + whether a 403 body was JSON or HTML (open the raw response — `<!DOCTYPE` = HTML).
2. Exact call: method + URL + field names (redact token/password).
3. Expected vs actual.
4. When it started, poll rate (calls/min), batch size (IDs/call), one tool or many sharing the account, VPS/cloud or home IP, approved API user or pending.

Example: "GET /v3/markets/<id>/quotes/ -> 429 since 10:20 UTC, polling 1 ID every 5s from Make (12/min), approved user, home IP. Expected prices. No expiry field in body."

## Three setups that work

**A. Sheets tracker (every 15 min) — start here.**
Timer -> Login (fresh each run) -> GET /v3/accounts/ -> GET /v3/orders/ -> write rows (time, label, contract, price/10000, quantity/10000, state) -> Logout. Fresh login dodges the 20-min rotation. 4 calls per 15 min — nowhere near limits.

**B. Price alert (every 1-10 min).**
Timer -> Login -> ONE batched GET quotes with up to 200 IDs -> Filter (e.g. decimal 10000/price < 2.5) -> notify (email/Slack/Sheets) -> Logout. Never one scenario per market. 1500 markets = 8 calls. About every 10s at full tilt fits 50/min; every minute is 8/min — comfortable.

**C. Auto-bet (manual trigger first, automate later).**
Trigger -> GET states (open?) -> GET accounts (available enough?) -> POST orders with label + keep_in_play if wanted -> log order_id + total_executed_quantity. Add: on 401 -> Login once -> retry once -> alert and stop. Add: check INSUFFICIENT_FUNDS before placing (available < stake + exposure buffer -> skip). Never auto-retry cancel-all; never loop login; cap to 10 placements/second.

**Cloud 403s (Zapier/Make/n8n Cloud)?**
Cloud runs on datacentre IPs, challenged more. Prove it: run the same call from home. Home works + cloud gives HTML 403 = host IP, not your setup. Do not hammer through the block. Email support with the template + both IPs' behaviour.

---

# PART 14 — GLOSSARY (PLAIN ENGLISH)

- Event / Market / Contract / Order — match -> bet type -> outcome -> your bet.
- Back (buy) / Lay (sell) — WILL happen / WON'T happen.
- Price — odds as 10000/decimal. 5000 = 2.0.
- Quantity — stake as £x10000. 20000 = £2.
- Exposure / Available / Balance — locked / spendable / total. Available = balance - exposure.
- Token / Session — temporary pass from login, ~20-30 min life.
- MFA / TOTP / Verify — authenticator code + extra login step.
- KIP / GTH / GTC / IOC / FOK — survive halt / die on halt / die going live / take-now-or-cancel / all-or-nothing.
- Quotes / Last executed / Volumes — live book / last trade / how much traded.
- 401 / 403 / 404 / 429 / 451 / 5xx — logged out / not allowed / not found / too fast / country blocked / our side.
- Batch / Poll — many IDs one call / re-check on a timer.
- RF (reduction factor) — odds cut when a horse withdraws.
- Void — stake back, bet never happened.
- Dead heat — tie, winnings split.
- Halt / Suspend — trading paused (goal, VAR, withdrawal).
- In-play delay / Confirmation — 4s/8s wait / 8-14s Instant Match wait.
- Trade out — exit one contract (exchange). Cash out — exit whole bet (SBK).
- Closed loop / Net deposits — profit must exit via deposit method / deposits minus withdrawals per method.
- Rate limit / Expiry / Headers — call cap / when it resets / Limit-Remaining-Reset metadata.
- RG_ACK / KYC — gambling popup on website / ID checks.
- Fullcover — multiple-bet type, list-only via API.
- Commission type 0.02/0.01/0.03 — Standard 2% / Pro 1% / Select 3%.

---

*Sources: live OpenAPI spec, docs.smarkets.com, API T&Cs, Commission FAQ, Help Centre betting rules + payments + safer gambling, plus repeat ticket patterns (auth traps, 800-vs-20000, 20-min rotation verified Oct 2026, batch 404s, quotes two-tier 50 vs 20, empty P2P books). Last updated Oct 2026. Not covered? Email api@smarkets.com with the four items in Getting help.*
