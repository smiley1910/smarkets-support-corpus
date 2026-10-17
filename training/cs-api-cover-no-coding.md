# INTERNAL — API Cover (No Coding Required)

**INTERNAL. Do not send to customers. Owner: API Support. Oct 2026.**
**Prerequisites: none. Read top to bottom once. Then Ctrl+F per ticket.**
**Companions: `training/confluence_draft_v2.md` (code reference). VOICE_CORE_PINNED.md (reply rules). `skills/smarkets-api-support/SKILL.md` (escalation).**

## 0. Definitions

| Term | Meaning |
|---|---|
| Endpoint | URL + method. GET = read. POST = place. DELETE = cancel. |
| JSON | Labelled reply format. Recognise field names only. |
| Header | Attached pass on every request after login. |
| Event / Market / Contract / Order | Match / bet type / outcome / customer bet. |
| Buy / Sell | Back WILL happen / Lay WON'T happen. |
| Price | 10000 / decimal odds. 5000 = 2.0. |
| Quantity | £ x 10000. 20000 = £2. Minimum 500. |
| Available / Exposure / Balance | Spendable / locked in open orders / total. Available = balance - exposure. |
| Token | Pass from login. ~20-30 min life. |
| 401 / 403 / 404 / 429 / 451 / 5xx | Logged out / not allowed / not found / too fast / country / Smarkets side. |

API = Smarkets exchange only. Not SBK. No sandbox. No read-only tier. No push/streaming. No multiples/Bet Builders/cash out via API.

Step 0 on every order-type ticket: "Are you using the API or the website/SBK app?"

## 1. Onboarding

| Stage | Requirement |
|---|---|
| Verified | Photo ID + proof of address. No screenshots. No mobile bills. Target 72h. Source of funds possible later. |
| Funded | Minimum £150 + stakes. Own-name method. Account currency. |
| Applied | Request Form. Tool, markets, cadence, volume. 3-5 sentences. |
| Fee | £150 from balance on approval. Refundable on permanent quit within 60d via support@smarkets.com. |
| Approved | Login with normal email + password. No separate key. 60-day review runs concurrently. |

Build order: login -> accounts -> one batched quotes -> one £0.05-£1 manual bet -> automate.

Ask: stuck at verification, deposit, form, or login? Tool, markets/min, bets/day?
Escalate: approval disputes, jurisdiction edge cases, fee disputes.

## 2. Login

POST `https://api.smarkets.com/v3/sessions/`. Body: `{"username": "<email>", "password": "..."}`. Field is `username`. Success is 201. Read `token`.

All later calls: header `Authorization: Session-Token <token>`. Exact words. Test: GET `/v3/accounts/` returns balance.

MFA accounts: add POST `/v3/sessions/verify/` with 6-digit code before orders. Login fine + all orders 401 = skipped verify.

Logout: DELETE `/v3/sessions/`. 30/60s.

Lifetime ~30 min, rotation ~20 min. Short jobs: fresh login each run. Long jobs: on 401, login once, retry once, stop. Never loop. Limit 5/300s.

| Code | Action |
|---|---|
| INVALID_CREDENTIALS | Reset password on smarkets.com. |
| PASSWORD_RESET_NEEDED | Reset first. |
| INVALID_TOKEN | Fresh MFA code. |
| DEVICE/IP_NOT_TRUSTED | Device trust on smarkets.com. |
| SESSION_LIMIT_REACHED | Log out elsewhere. |
| USER_SUSPENDED | support@smarkets.com. |
| SELF_SUSPENDED/ON_TIMEOUT/EXCLUDED | Wait out / support. |
| SOURCE_BLOCKED/JURISDICTION_MISMATCH | Support. |
| COUNTRY_BLOCKED 451 | Unsupported. Server must move. |
| 429 on login | Wait for window. |

Ask: field names used (`username` or `email`)? Status shown (200-only check)? Minutes to fail (20 vs idle)? Scenarios sharing account? Authenticator on? Never request token values. Never request curl.
Escalate: device/session/source/jurisdiction codes. 403 on login. HTML body. POST 401 with GET fine. Cookie/auth-v2 mentions. `data: None`. Persistent 401 after fresh login + verify.

## 3. Discovery

Free (no login): events, states, competitors, markets, counts, contracts, currencies.

Login required: quotes, last_executed_prices, volumes, orders, fullcover (list-only), accounts, activity.

Order: events -> markets -> contracts -> quotes (copy price) -> states (confirm open). IDs as comma lists up to cap (section 6).

Empty quotes + website shows price = normal. Quotes = customer orders only. Website includes sources not in API. Cross-check last_executed_prices.

Ask: market ID + last_executed_prices result?
Escalate: liquid-market persistent empties with evidence. Disputed explanation.

## 4. Orders

POST `/v3/orders/`. Required: market_id, contract_id, price, quantity, side. Recommended: type, label.

Type default `good_til_halted`. Only `keep_in_play` survives halts. `good_til_cancelled` dies going live. `immediate_or_cancel` fills now or cancels rest.

FOK = IOC + minimum_accepted_quantity = quantity. Partial-ok = minimum lower. Always set explicitly. No `time_in_force` field.

Reply: order_id, total_executed_quantity, executed_avg_price (null if unmatched), available_balance, exposure. No quantity_filled/state (GET-only: created/partial/filled/settled).

Delays: 4s racing/darts, 8s rest. Pending + invisible = normal. Instant Match 8-14s confirmation; material event inside can void. No placement while halted.

| Reject | Action |
|---|---|
| INSUFFICIENT_FUNDS | Check available. Cancel order or reduce stake. |
| INVALID_PRICE | Copy from quotes. |
| INVALID_QUANTITY | Minimum 500. |
| HALTED/SUSPENDED | Wait. Re-check states. KIP next time. |
| SETTLED/NOT_FOUND/NOT_OPEN | Re-walk IDs. |
| STAKE/LIMIT/CAPACITY | Reduce or support. |
| CROSSED_SELF | Move price. |
| THROTTLE | Under 10/s. |
| RG_ACK_REQUIRED | Website popup. Instant. Do not re-apply. |
| KYC/UNVERIFIED | Verify on website. |
| NO_DEPOSITS | Fund first. |
| SUSPENDED/ACTION_BLOCKED | Support. |
| SERVICE_TIMEOUT | Wait. Retry once. |

Ask: exact code word? Available (not total)? In-play?
Escalate: IOC full-minimum partial fills (need quantity/min values + full reply + environment). Persistent service errors. Unlisted codes.

## 5. Check / Cancel / Balance / Statement

Check: GET `/v3/orders/`. Filter by label.
Cancel one: DELETE `/v3/orders/{id}/`. 10/s.
Cancel all: DELETE `/v3/orders/`. 1/60s. Never on auto-retry. Re-cancel of dead order succeeds silently. Post-settlement: no cancel.

Accounts: balance, exposure, available = balance - exposure. "Has money, cannot bet" = exposure.

Activity: GET `/v3/accounts/activity/` (timestamp_max/offset/limit).
CSV: GET `/v3/account_activity_csv/{start}/{end}/`. Both ISO 8601, on hour, exactly 1h apart. Else 400 INVALID_DATETIMES. No data = 404 NO_CSV_AVAILABLE. Too broad = RECKONATOR_REQUEST_TOO_LARGE. Gzipped CSV.

Ask: GET state + quantity_filled? Cancel-one or cancel-all? Exact CSV start/end strings? Available vs balance?
Escalate: throttle/capacity at low volume. INSUFFICIENT_FUNDS on cancel. Valid hour-window still INVALID_DATETIMES.

## 6. Limits

Global 1200/60s per account. Shared across all tools/servers/tokens.

| Call | Cap |
|---|---|
| events | 600/60s |
| quotes | 50/60s approved (~20 pre-approval, header is truth) |
| login | 5/300s |
| logout | 30/60s |
| place | 10/s |
| cancel one | 10/s |
| cancel all | 1/60s |

429 structured (most GETs): count/limit/expiry (RFC 2822). Wait to expiry, halve rate. 429 short (quotes/orders/sessions): no expiry. Wait ~60s. Repeats suspend then revoke.

Batch caps (IDs/call): quotes 200. volumes/states/competitors 300. contracts/last 100. markets-by-event/counts 50. Over cap = 404 "Nothing matches the given URI". Count IDs.

Fix order: batch first (1500 markets at 200 = 8 calls/sweep). One timer fanning out. Cache static lists. Never poll login/cancel-all.

Increase line (verbatim, only if asked): "We are unable to review quote limit increases at this time, once you've built a larger sample size of activity we can review and request this for you." No dates. No thresholds. No aggregates. No full limit recital. No api@smarkets.com reroute. Internal bar (never in customer text): market maker level.

Streaming/websocket/push: not offered. REST polling only. Scope denial to API. Never name sio-live/archived SDK.

Ask: timer cadence? IDs per call? Other tools on account?
Escalate: limits at low single-client volume. Post-429 suspension. Approved account stuck on 20. Short-429 no recovery.

## 7. 403 Split

Get body first. `{` = JSON (account permission). `<` = HTML (network block).

JSON: approval / 60-day review / revoked / scope / RG_ACK / KYC / NO_DEPOSITS / ACTION_BLOCKED / SOURCE_BLOCKED / IP_NOT_TRUSTED / JURISDICTION_MISMATCH. RG_ACK: website popup, instant, no re-apply. KYC: verify on website.

HTML: datacentre/VPS IP, reputation, or server country. Home test proves host vs setup. No self-serve unblock. Internal allowlisting: supported jurisdictions only, api.smarkets.com only.

Ask: raw body starts `{` or `<`? If JSON, error_type + data words only, redact token. Home or cloud? ID checks + deposit done?
Escalate: all HTML. SOURCE/IP/JURISDICTION codes. 451 from supported country. Suspension/compliance disputes.

## 8. Server Side

500 INTERNAL_ERROR. 503 subsystem codes (KYC/AUTH/ORDER/EVENTS/CHARTS/MDS/FOREX/RECKONATOR/PROMOTION/ZEUS + TIMEOUT variants). 504 ZEUS_TIMEOUT/RECKONATOR_UNAVAILABLE. Wait minutes. Retry once. Escalate with UTC time + endpoint + code if persistent.

Ask: recurrence? Exact code + time + endpoint?
Escalate: always if persistent.

## 9. Commission / Payments / RG

Commission: Standard 2% net per market, win-only. No API discount. No 0%/affiliate for API users. Pro 1%: opt-in at 1500 bets or £1M/month (ask at 80%, via support, never automatic, per-matched-bet on wins AND losses, forfeits promos, 3-month minimum). Select 3%: auto at £25k/12mo net (+7d email, forfeits promos, discretionary review). Decode commission_type: 0.02/0.01/0.03. Never promise Pro/Select changes.

Payments: free, mostly instant, £10 min (£25 PayPal), own-name, account currency. Closed loop: same method out. Net deposits per method = deposits - withdrawals; zero each positive before skimming elsewhere. Timings: Instant Bank ~12h, Trustly/e-wallets 1-2d, cards 1-6d, Bank Transfer 5-10d (£20 min, last resort). E-wallet 4th+ in 7d takes 24h. Stuck: minimum? deposit method? overuse in 12h? address/country change? removed method?

RG: same on API. RG_ACK: website popup, instant. Timeout 1/7/31/42d: locks all, auto-reopens, never early. Self-exclusion 6mo/1y/5y/permanent: balance 48h, never early, fixed terms need support contact to reopen, permanent never reopens. SoF/wealth/affordability possible anytime. Never contact employer. Non-provision restricts: deposit block -> bet block -> suspension.

## 10. Betting Rules (Automation-Relevant)

Settlement ASAP on official result that day. Later amendments excluded. May delay/void/resettle.

Voids (stake back): cancelled, not concluded within 36h, postponed >36h past start, opponent/venue change, modified length. Surface change alone stands. Dead heats split.

Football: 90 min + stoppage. No extra time/pens unless stated ("To Advance" includes). Own goals excluded from goalscorer. Cards Y1/R2/YY+R3, max 3/player, subs excluded. Abandoned voids unless decided. No resumption news in 3h voids undecided.

Tennis: first set incomplete voids all (except decided). Post-set-one retirement: retiree loses Match Winner, Set Betting void. Venue/surface change stands. Final-set tie break = 1 game.

Racing: first past post then weighed-in. Later appeals excluded. Non-runner voids bets on it. Places >= runners voids all. Ante-post stands. Places: 5-7 = 2, 8-15 = 3, 16+ non-handicap 3, 16+ handicap 4. RF: New = Old x ((100-RF)/100). Win <2.5% stands; >=2.5% adjusts matched, cancels unmatched, reopens. Place: any RF adjusts, cancels unmatched. May apply post-race.

In-play/KIP/trade-out: delays per section 4. KIP set per bet (Rule 10). Non-KIP unmatched dies at halt. Trade out per contract, never guaranteed. Erroneous: report 60 min to support@smarkets.com with time/contract/market/price/reason, pre-result. Outliers ±20% reviewable later. Counterparty traded out can leave placer liable.

Void walk: 36h? RF? Same-event builder leg voided (whole bet voids, stake back) vs cross-event (odds reduce)? Erroneous? Resettled in error?

## 11. Policy (Denials)

Allowed: view prices + place bets on approved markets. Automate own trading. Report big setup changes.

Banned (T&Cs s2/s5/s6/s7): scraping, concealed calls, impersonation, reverse engineering, data without trading, share/sell/distribute without written approval, benchmarking, extra accounts for fees (fraud), latency arbitrage, court-siding, exchange-harmful strategies.

Penalties: warning -> suspension -> permanent removal + voided bets + possible legal. Serious skips to removal. Access withdrawable anytime without notice.

Secrets: customer responsibility. Leaked: change password, DELETE sessions, support@smarkets.com. One person per account.

Pattern B: one acknowledging line. Direct answer + one T&C quote max. <=2 sentences constraint. Optional alternative. Close. Test-mode line: "The public API specification does not document a test or sandbox environment."

## 12. Workflow

First action: 2-4 diagnostic questions. Not the fix. One soft hypothesis + ONE confirming evidence (full 429 body, or response text). Recurrence question ("has this happened since?"). Facts separate from policy. Quote T&Cs exactly.

Handoff (one message): platform. Approval state. Symptom in customer's words. Full error (status + error_type + data + expiry + JSON/HTML). Exact call (method + URL + field names, redacted). Expected vs actual. Start time. Poll rate + batch + tool count. Home vs cloud. Section already given.

Routing: API bugs/codes/limits/auth/batching -> api@smarkets.com path via tech. Account/money/ID/RG/closed loop/fee/compliance -> support@smarkets.com path. SBK -> support@getsbk.com / chat 09:00-23:00 GMT / +44 207 617 7413. Outages: status.smarkets.com / @SmarketsTech.

## 13. Reply Rules

4 jobs per sentence: fact, decision, reason, next step. Delete the rest.
Short info/denial 120-200 words. Complaints: Acknowledge (1 line) -> Review -> Reason (rule + THESE facts) -> Action (ONE decision sentence last).
Banned: Unfortunately, I'm sorry to say, I understand, the upside is, furthermore, additionally, Please be advised, I can confirm that.
Plain text. Straight quotes. No em dashes. No hyphenated compounds (except `in-play`). Negatives <= 3. UK English. No spec/schema/OpenAPI wording. No api@smarkets.com reroute. No colleague names. IBAS/eCOGRA only if requested, instructed, or final position.
Sign-off: "Kind regards, / [name] / Smarkets Support".

Copy-adapt bases (tune before sending):

Login: "Thanks for your message. Log in with POST https://api.smarkets.com/v3/sessions/ using `username` (your email as the value) and `password`. A working login returns 201 with a `token`. Set that step to accept 200 or 201 and save `token`. Add the header `Authorization: Session-Token <token>` to every later call and test with GET https://api.smarkets.com/v3/accounts/. Login allows 5 tries per 5 minutes, so pause before retrying after a 429. Kind regards, [name] Smarkets Support"

Rotation: "Thanks for your message. Sessions rotate about every 20 minutes, so long runs need a re-login branch. On a 401 run Login once, replace the stored token and retry that step once, then stop and alert if it fails again. For runs under 15 minutes the simplest fix is a fresh login each run with a logout at the end. Kind regards, [name] Smarkets Support"

Quantity: "Thanks for your message. The API counts stake in 1/10,000ths of your currency, so [their number] is [£x]. To stake [£y] send quantity [N] (pounds x 10000, minimum 500). Kind regards, [name] Smarkets Support"

Price: "Thanks for your message. The API counts odds as 10000 divided by decimal odds, so [their number] means [odds]. To bet at [odds] send price [N]. If a price is rejected, copy one straight from the quotes reply. Kind regards, [name] Smarkets Support"

Limits: "Thanks for your message. The quotes allowance is 50 requests per 60 seconds per account, shared across every tool on the account. Quotes takes up to 200 market IDs in one call, so [their volume] needs [N] calls per sweep. Wait until [expiry / about a minute] then re-run at that batch size with one timer. We are unable to review quote limit increases at this time, once you've built a larger sample size of activity we can review and request this for you. Kind regards, [name] Smarkets Support"

Batch 404: "Thanks for your message. That 404 means the batch held more IDs than the endpoint takes, not that the route is dead. Quotes takes up to 200 IDs per call [volumes/states/competitors 300, contracts/last prices 100, markets by event 50]. Split to those sizes and re-run. Kind regards, [name] Smarkets Support"

RG_ACK: "Thanks for your message. Your account is approved, place no new application. Log in at smarkets.com and complete the Responsible Gambling acknowledgement popup (try a market page if it does not show), then retry the same API call with no other change. Kind regards, [name] Smarkets Support"

Streaming: "Thanks for your message. Prices come from polling the documented REST endpoints. There is no streaming or push feed for API users and the old streaming service is deprecated. Poll quotes (up to 200 market IDs per call, 50 requests per 60 seconds) on a timer instead. Kind regards, [name] Smarkets Support"

## 14. Links

Docs https://docs.smarkets.com/. Live spec https://api.smarkets.com/v0/control/openapi/?tags=trading_api (truth; local copy can be stale). Form https://support.smarkets.com/p/6MLL-PL7/api-request-form. T&Cs https://help.smarkets.com/hc/en-gb/articles/34697834941085-Smarkets-API-Access-Integration-T-Cs. Commission https://help.smarkets.com/hc/en-gb/articles/212654665-Smarkets-commission-FAQ. Help https://help.smarkets.com/hc/en-gb. Base https://api.smarkets.com.

*Sources: live spec, API T&Cs, Commission FAQ, Help Centre rules/payments/RG, precedents (30 Sep increase wording, 12 Oct batching briefs, 1 Oct rotation + boundary probes). Docs beat this page on conflict. Flag for update.*
