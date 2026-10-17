# No-Code API Users — Internal CS Cover Page

**Status: DRAFT for Michael | Owner: API Support | Last updated: Oct 2026**
**Audience: CS agents covering API tickets. NOT customer facing. Do not paste this page to customers.**
**Companion docs: `training/confluence_draft_v2.md` (main triage KB — use that first for all error codes), VOICE_CORE_PINNED.md (every customer reply must pass it), `skills/smarkets-api-support/SKILL.md` (escalation workflow). This page only covers what is DIFFERENT about no-code builders (Zapier / Make / n8n / Bubble / Sheets).**

## How to use this page

1. Ticket mentions Zapier, Make, n8n, Bubble, Sheets, "no code", "webhook module", "HTTP module"? You are on the right page. Otherwise use confluence_draft_v2.md only.
2. Ctrl+F the customer's symptom below. Each block gives: what it means, what to ASK (one question max — they cannot run curl or read headers easily), what to TELL them (copy-adapt, then run through Voice Core before sending), when to FLAG to technical.
3. Default first action on every new ticket: 2-4 diagnostic questions. No-code variant in "What to ask" under each block. Do not dump all probes at once.
4. Step 0 before any order-type answer: ask "Are you using the API or the website/SBK app?" (Same feature, different answer per surface. Real past correction.)
5. Never rephrase their words into codes they did not use. They wrote "Forbidden for url..." -> you write that back, not "your 403".

## 30-second orientation (read once per shift)

- There is no Zapier app, Make app, SDK, sandbox, read-only key, webhook-out, websocket or streaming. REST polling only via generic HTTP modules. Anyone asking for those gets Pattern B decline (one T&C quote max).
- Auth is email + password -> `token` from `POST /v3/sessions/` (201, field `username` not `email`, field `token` not `session_token`) -> header `Authorization: Session-Token <token>` on everything after. MFA adds `POST /v3/sessions/verify/`.
- The three no-code killers: quantity units (800 = £0.08, 20000 = £2), price units (5000 = 2.0, formula 10000/price), 20-minute rotation (header-only setups 401 around 19-20 min even while active).
- Limits that matter: global 1200/60s per account; quotes 50/60s approved (~20 pre-approval); login 5/300s; cancel-all 1/60s; place 10/s; cancel-one 10/s. Batch caps: quotes 200, volumes/states/competitors 300, contracts/last-prices 100, markets-by-event 50. Over cap -> 404 "Nothing matches the given URI" (not a dead route).
- Increase requests: batch advice FIRST (200 IDs/call maths for their volume), then Michael's approved line verbatim: "We are unable to review quote limit increases at this time, once you've built a larger sample size of activity we can review and request this for you." No dates, no thresholds, no aggregate totals (no "10k/min" style claims), never recite all six limits, never reroute to api@smarkets.com in customer text (WE are API support). Internal truth (never in customer text): bar is market maker level.
- 403 JSON = account permission (approval / 60-day review / revoked / scope / RG_ACK / KYC / NO_DEPOSITS). 403 HTML (`<!DOCTYPE`) or SOURCE_BLOCKED/IP_NOT_TRUSTED = edge/network block (VPS/datacentre IP, jurisdiction). Never diagnose mechanism without the response body — ask for it.
- Voice Core gates on every reply: plain text only, straight quotes, no em dashes, no hyphenated compound modifiers (exception `in-play`), negative density <= 3, UK English, banned openers ("Unfortunately", "I understand", "I can confirm that", "Please be advised", "furthermore", "additionally"), exactly ONE decision sentence last for complaints, sign-off exactly "Kind regards, / [name] / Smarkets Support".
- Source hierarchy: live spec https://api.smarkets.com/v0/control/openapi/?tags=trading_api > local openapi/ snapshot (STALE in places) > workspace docs > customer message > inference (label it, never present as fact).

## Triage map: symptom -> section

- "cannot log in / wrong password / locked out" -> A. Login failures
- "keeps logging me out / worked then 401 / token expired" -> B. 401s incl 20-min rotation
- "not allowed / forbidden / blocked / can't bet" -> C. 403 routing (JSON vs HTML)
- "bet rejected / won't place / insufficient funds / wrong price" -> D. Order rejects
- "can't cancel" -> E. Cancel
- "too many requests / rate limited / 429" incl "need higher limit / follow X markets / streaming?" -> F. Rate limits + batching + streaming denial
- "stake shows wrong (£0.08 not £2)" -> G. Quantity
- "odds/price rejected or confusing" -> H. Price
- "empty prices but website shows them" -> I. Quotes empty book
- "statement/CSV fails" -> J. CSV + account reads
- "where is my bet / not on website / fill wrong" -> K. Order visibility
- "commission 2% / Pro 1% / Select 3% / 0% offer" -> L. Commission
- "need test mode / read-only feed / data only" -> M. Scope denials
- "VPS / server / cloud blocks" -> N. Infra/network
- "moved country / travelling" -> 451 in C
- "500/503/504" -> O. Server side
- "how do I start / get access / £150 / how long" -> P. Onboarding
- Anything unmatched, customer sent logs you cannot parse, account/compliance dispute, persistent 5xx -> Q. Escalate

## A. Login failures (POST /v3/sessions/)

**What it means:** 90% are three field mistakes: `email` used as key (must be `username`), expecting 200 (login returns 201), reading `session_token` (field is `token`). Rest: wrong password, MFA code stale, device trust, session limit, suspension/timeout/exclusion, jurisdiction, or 429 (5/300s burns fast while debugging).

**What to ask (pick max 2):** "What exact field names did you put in the login body — did the guide you followed say `email` or `username`?" / "What status did the login step report — check whether your tool treats anything other than 200 as failed?" / "Are you using an authenticator app on the account?"

**What to tell them:** Login is POST https://api.smarkets.com/v3/sessions/ with `{"username": "their email", "password": "..."}`. Success is 201 with a `token` field — set the step to accept 200 OR 201 and read `token`. Then test with GET /v3/accounts/ + header `Authorization: Session-Token <token>`. MFA accounts add POST /v3/sessions/verify/ with the current 6-digit code before bets will work. Login allows 5 tries per 5 minutes — on 429 wait for the window, do not retry in a loop.

**Do NOT:** tell them to re-apply or pay again; mention paper trading/sandbox (does not exist — say "the public API specification does not document a test or sandbox environment"); paste ReST/markdown tables/curly quotes.

**Flag to technical:** DEVICE_NOT_TRUSTED / IP_NOT_TRUSTED / SESSION_LIMIT_REACHED / SOURCE_BLOCKED / CLIENT_JURISDICTION_MISMATCH, any 403 on login, HTML body on login, repeated 401 from DELETE /v3/sessions/.

## B. 401s after working ("keeps logging me out")

**What it means:** Usual: 30-min idle expiry. No-code signature: 401 at ~19-20 min DESPITE polling every 20s — that is the session rotation, not idle. Header-only clients die at rotation; cookie clients (both cookies sent + renewed token adopted) survive past 30 min. Verified live Oct 2026 (control 401 at 19:58, treatment 105x200 zero 401s). Other causes: MFA never verified (login fine, all orders 401), mixed auth (GET via browser cookie works, POST via header fails), environment switch invalidating tokens.

**What to ask:** "How many minutes after login does it fail — roughly 20, or after sitting idle?" / "Is it one scenario or several sharing the account, and do you use an authenticator app?" (Do NOT ask for token values. Do NOT ask them to run curl.)

**What to tell them:** Short runs: log in fresh each run (every 15 min dodges rotation entirely) and logout at end. Long runs: add a branch — on 401 run Login once, replace stored token, retry that step once, then stop and alert; never loop login (5/300s). If they can set cookies (n8n/advanced): send `Cookie: User-Session-Token=<token>; Refresh-Token=<refresh_token>` every call and adopt each renewed session token from responses.

**Flag to technical:** customer mentions cookies/auth v2/refresh tokens; 401 on POST but GET fine; `data: None`; 401 persisting after fresh login + MFA verify.

## C. 403 routing (JSON vs HTML — get the body first)

**What it means:** Two different faults, same digits. JSON `error_type: FORBIDDEN` (plus RG_ACK_REQUIRED / KYC_PERMISSION_DENIED / ACCOUNT_UNVERIFIED / NO_DEPOSITS / ACTION_BLOCKED / SOURCE_BLOCKED / IP_NOT_TRUSTED / CLIENT_JURISDICTION_MISMATCH) = account permission. HTML starting `<!DOCTYPE` = Cloudflare edge block (datacentre/VPS IP, IP reputation, or server in unsupported jurisdiction — allowlisting only helps supported-jurisdiction datacentre IPs via internal request, never promise it; Finland/Hetzner-Helsinki class = must move server, no hostname workaround).

**What to ask:** "Can you open the raw response body of that failed step and tell me whether it starts with `{` (JSON) or `<` (a web page)? If JSON, paste the `error_type` and `data` words only — redact the token." / "Are you running from home wifi or a cloud server/VPS, and has the account finished ID checks + first deposit?"

**What to tell them (JSON):** Account-level block. Usual: not yet approved (£150 + form), in 60-day compliance review (normal, can trade), revoked/scope, or one-step website fixes — RG_ACK_REQUIRED: do the gambling popup on smarkets.com (try a market page), lifts instantly; KYC/ACCOUNT_UNVERIFIED: finish verification on website, API follows with no setup change; NO_DEPOSITS: fund first. Do NOT tell RG_ACK/KYC cases to re-apply or pay again.

**What to tell them (HTML):** Network-level block, not credentials. Prove by running same call from home. No self-serve unblock. Take ownership and ask them to reply with use case + host behaviour; raise internal allowlisting ONLY for supported-jurisdiction datacentre IPs on api.smarkets.com. Only ever confirm api.smarkets.com — never bless sio-live/stream hosts (website internals / deprecated, not API).

**Flag to technical:** any HTML 403; JSON 403 with SOURCE_BLOCKED/IP_NOT_TRUSTED/CLIENT_JURISDICTION_MISMATCH; 451 COUNTRY_BLOCKED from a normally supported country; suspension/compliance disputes (human judgement, no detailed internal reasoning to customer unless pre-approved).

## D. Order rejects (POST /v3/orders/)

**What it means:** Code names the reason — ask for the exact code, never guess. No-code top three: INSUFFICIENT_FUNDS (exposure locking available — check `available_balance` not total), INVALID_PRICE (not on tick — copy from quotes), INVALID_QUANTITY (under 500). Then HALTED/SUSPENDED (goal/VAR/withdrawal — wait, re-check states; next time keep_in_play to survive halts), THROTTLE (over 10/s), CROSSED_SELF, CAPACITY/LIMIT/STAKE caps, NOT_FOUND/SETTLED/NOT_OPEN (stale IDs or done market), SERVICE_TIMEOUT (server side).

**What to ask:** "What is the exact rejection code word in the reply (e.g. ORDER_REJECTED_...)?" / "What available balance did the accounts step return just before, and was the market in-play?" (One question if they already gave the code.)

**What to tell them:** 5 required fields: market_id, contract_id, price, quantity, side (buy=back WILL, sell=lay WON'T). INSUFFICIENT_FUNDS: cancel an open order or stake less. INVALID_PRICE: copy a price from quotes. INVALID_QUANTITY: minimum 500. HALTED/SUSPENDED: wait, re-check GET states, retry; use `type: keep_in_play` to survive halts (only KIP survives — never promise "orders stay in the book"). THROTTLE: slow under 10/s. STAKE/LIMIT/CAPACITY: contact support. SETTLED/NOT_FOUND: re-walk events->markets->contracts for fresh IDs.

**Flag to technical:** IOC with minimum_accepted_quantity == quantity still partial-filling (need exact quantity/min values + full reply incl total_executed_quantity + paper/live); SERVICE_TEMPORARILY_UNAVAILABLE persisting; any code not in Groups 1-8.

## E. Cancel problems

**What it means:** Usually already filled/cancelled/settled, wrong UUID, or not theirs. Cancel-one 10/s; cancel-ALL 1/60s kills everything — never on auto-retry. Re-cancel of dead order succeeds silently (safe to retry once). After settlement nothing cancels.

**What to ask:** "What does GET /v3/orders/ show for that order ID right now — state and quantity_filled?" / "Was that the cancel-one or cancel-everything step?"

**What to tell them:** Check state first via GET /v3/orders/. Cancel one with DELETE /v3/orders/{order_id}/. Keep cancel-all off triggers/loops. Settled = cannot cancel.

**Flag to technical:** THROTTLE/CAPACITY/LIMIT persisting at low volume; INSUFFICIENT_FUNDS on cancel (rare); SERVICE error persisting.

## F. Rate limits + batching + streaming asks

**What it means:** Global 1200/60s per account shared across every tool/server/token on that account. Per-endpoint caps fire first (quotes 50/60s approved, ~20 pre-approval; login 5/300s; logout 30/60s; place 10/s; cancel-one 10/s; cancel-all 1/60s). Structured 429 (most GETs) has count/limit/expiry (RFC 2822 date, NOT ISO — do not tell them to fromisoformat it); quotes/orders/sessions 429 is short with NO expiry. Header is ground truth for their tier (20 vs 50 = usually pre-approval). Over-batch 404 ("Nothing matches the given URI") = too many IDs, not dead route (quotes flips 200->404 at 201; volumes at 301).

**What to ask:** "How often does the timer run, how many IDs per call, and is any other scenario/server using the same account?" / For increase asks: "How many IDs per quotes call today — check the comma count in that URL?" (Batch size BEFORE any increase talk. Do not recite all limits. Do not ask for full logs when these three numbers diagnose it.)

**What to tell them:** Wait to `expiry` where present (else ~60s for quotes/orders/sessions), then halve poll rate. Fix is batching, not speed: quotes 200/call, volumes/states/competitors 300, contracts/last-prices 100, markets-by-event 50. Work THEIR numbers: 1500 markets at 200 = 8 calls/sweep (~every 10s within 50/min); at 100 = 15 calls (~every 18s); at 1 = blocked. One timer fanning out beats five timers. Cache event/contract lists; poll only quotes/balance fast. Never poll login or cancel-all. Then increase line ONLY if asked (verbatim, see orientation). Streaming/push/websocket: decline — REST polling only, streaming service deprecated (scope denial to API, never name sio-live/archived SDK, no api@smarkets.com reroute, Pattern B shape).

**Flag to technical:** hitting limits at genuinely low single-client volume (possible hidden second client); suspension after repeated 429s; approved account stuck on 20 header (server-side mismatch — escalate for correction, never "force 20->50" as agent override); persistent short-429 with no recovery.

## G. Quantity wrong ("I sent 800 expecting £2")

**What it means:** Units are 1/10,000ths of currency. 800 IS £0.08. £2 = 20000. Minimum 500 (£0.05). Back-stake formula quantity x price / 100000000.

**What to ask:** "What quantity number did the step send, and what pounds did you expect?" (That alone diagnoses it.)

**What to tell them:** Multiply pounds by 10000: £1 -> 10000, £2 -> 20000, £10 -> 100000. Give THEIR corrected number back. Point to label their orders for Sheets filtering.

**Flag to technical:** rarely — only if corrected quantity still rejects as INVALID_QUANTITY.

## H. Price wrong ("odds rejected / confusing")

**What it means:** Units are basis points: decimal = 10000/price. 5000 = 2.0, 2500 = 4.0, 1000 = 10.0, 7194 = 1.39. Range 1-9999 on valid ticks only. No `time_in_force` field exists (their layer or another exchange — use `type` + `minimum_accepted_quantity`).

**What to ask:** "What price number did you send and what decimal odds did you want?"

**What to tell them:** Divide 10000 by wanted odds (2.0 -> 5000). INVALID_PRICE: copy a price from quotes. FOK = immediate_or_cancel + minimum_accepted_quantity == quantity; partial-ok = minimum lower; always set it explicitly on IOC (omitted can zero-fill).

**Flag to technical:** valid-looking tick from quotes still INVALID_PRICE repeatedly.

## I. Quotes empty but website shows prices

**What it means:** By design (strong evidence, not Smarkets-confirmed): quotes = P2P book only; website can aggregate extra market-making sources not in API. Thin in-play = often empty via API. NOT a bug to fix in their setup.

**What to ask:** "Which market ID, and does last_executed_prices show recent trades on it?"

**What to tell them:** Empty book = no P2P resting orders at that moment. Cross-check last_executed_prices for what really traded. For data confirmation beyond that, take ownership and ask them to reply with use case.

**Flag to technical:** customer disputes the explanation or shows liquid-market persistent empties with evidence.

## J. CSV + account reads

**What it means:** CSV: both ISO 8601 on the hour, exactly 1h apart (14:00->15:00) or 400 INVALID_DATETIMES; no data that hour = 404 NO_CSV_AVAILABLE; too broad = RECKONATOR_REQUEST_TOO_LARGE; reply is gzipped CSV (Make/n8n need Gunzip step, Zapier needs Code/Sheets import, Bubble needs file plugin). Paginated activity uses timestamp_max/offset/limit. Account fields: balance / available_balance / exposure (available = balance - exposure) / commission_type ("0.02"/"0.01"/"0.03") / currency / bonus_balance.

**What to ask:** "What exact start/end strings did the CSV step send?" / "What did the accounts step return for available vs balance?"

**What to tell them:** Snap times to `:00:00Z`, end = start + 1h. INSUFFICIENT_FUNDS with healthy balance = exposure — cancel an open order. commission_type decodes tier (see L).

**Flag to technical:** valid hour-window still INVALID_DATETIMES; persistent RECKONATOR_TOO_LARGE on narrow windows.

## K. Order visibility ("placed but not on website / fill wrong")

**What it means:** POST accepted (has order_id) but: filled instantly (check last_executed_prices), cancelled by halt/close, or looking at wrong account/environment. POST reply has total_executed_quantity + executed_avg_price (null if unmatched) but NEVER quantity_filled/state — those are GET-only. IOC partials depend on minimum_accepted_quantity. GTC/GTH/KIP confirmations only mean accepted — matching needs the other side.

**What to ask:** "What order_id did the place step return, and what do total_executed_quantity / executed_avg_price say?" / "What does GET /v3/orders/ show for it now?"

**What to tell them:** Track by order_id via GET /v3/orders/ (created/partial/filled/settled + quantity_filled). IOC: total_executed_quantity is the instant fill. Non-IOC: acceptance only, fills when matched. In-play delay (4s racing/darts, 8s rest) = pending + invisible, normal. Instant Match = 8-14s confirmation; material event inside can void.

**Flag to technical:** IOC full-minimum partial fills with proof; acceptance never appearing anywhere with valid ID.

## L. Commission questions

**What it means:** Standard 2% net-per-market (win only). API gives NO discount. 0%/affiliate offers: API users ineligible (T&Cs s3). Pro 1%: opt-in only at 1500 bets or £1M/month (ask at 80%), charged per matched bet on wins AND losses, forfeits promos, 3-month minimum. Select 3%: auto at £25k/12mo net (+7d email), forfeits promos, review if P&L drops (discretionary). Check commission_type first.

**What to ask:** "What commission_type does GET /v3/accounts/ show — 0.02, 0.01 or 0.03?"

**What to tell them:** Decode their value. Standard: 2% net per market only. Pro: thresholds + must contact support to opt in (can stay on 2%). Select: automatic on profit, not a penalty. Never promise Pro approval or Select removal.

**Flag to technical:** tier looks wrong for verified volume/profit with evidence (needs human judgement).

## M. Scope denials (read-only / data-only / test mode / multiples / streaming)

**What it means:** All Pattern B: one acknowledging line, direct answer quoting the operative T&C line (one quote max), <=2 sentences constraint, optional alternative, close. No padding, no multiple theories.

**Lines (adapt, keep quote exact):** Read-only/data-only: no reduced tier exists — single product, £150 + full process; T&Cs s2: "All other uses are strictly prohibited, including but not limited to, odds scraping, concealing API calls, browser impersonation or reverse engineering." Alternative: public event/competitor/contract endpoints, or apply if research justifies fee (refundable 60d). Test mode: "The public API specification does not document a test or sandbox environment." Multiples/accas/Bet Builders/cash out via API: not API features (SBK/website only). Streaming/websocket/push: not offered, REST polling only, deprecated service (scope to API). Benchmarking: s5 prohibits competitive benchmarking. Data resale/sharing: s5 needs written approval. Second accounts for fees: fraud.

**Flag to technical:** customer pushes back with "but endpoint X responds without auth" (runtime vs spec contradiction — do not debate, escalate with their evidence).

## N. Infra / network (VPS, cloud, Make/Zapier Cloud HTML 403s)

**What it means:** Cloud/datacentre IPs challenged more. Home-works + cloud-HTML-403 = host IP, not setup. Never keep retrying through the block. Never promise whitelisting. Only confirm api.smarkets.com for allowlisting requests.

**What to ask:** "Does the identical call work from home wifi? What are the first characters of the failure body (`{` or `<`)?"

**What to tell them:** Home test proves host vs setup. Take ownership, ask them to reply with use case + both behaviours. Internal allowlisting raisable ONLY for supported-jurisdiction datacentre IPs (UK/Malta/Ireland/Sweden). Unsupported-jurisdiction server (e.g. Helsinki class) = must relocate, no workaround, no alt hostname.

**Flag to technical:** always (network investigation, not CS-fixable). Include IP class + jurisdiction + JSON-vs-HTML finding.

## O. Server side (500 / 503 / 504)

**What it means:** Ours, not theirs. 500 INTERNAL_ERROR, 503 subsystem codes (KYC/AUTH/ORDER/EVENTS/CHARTS/MDS/FOREX/RECKONATOR/PROMOTION/ZEUS + TIMEOUT variants), 504 ZEUS_TIMEOUT/RECKONATOR_UNAVAILABLE. Nothing they change fixes it.

**What to ask:** "Has this happened since the first time, and can you give the exact code + time (UTC) + endpoint?" (Recurrence question, not reconstruction.)

**What to tell them:** Wait minutes, retry once with backoff. Still failing: report to api@smarkets.com path via escalation with timestamp + endpoint + code (subsystem code tells engineering where to look).

**Flag to technical:** always if persistent; immediately if customer confirms recurrence.

## P. Onboarding ("how do I start / £150 / how long / test?")

**What it means:** Standard path: verified account (ID + address, no screenshots, no mobile bills, 72h doc target, SoF possible) -> fund (>= £150 + stakes, own-name method) -> skim docs.smarkets.com (prices+bets only) -> Request Form (3-5 plain sentences: tool, sports, cadence, bet volume; must update Smarkets on big setup changes) -> wait (case by case, nudge if stale) -> £150 deducted on approval (refundable on permanent quit within 60d via support@smarkets.com) -> login with normal email/password (no separate key) -> 60-day review (can trade). Not eligible: unverified, self-excluded/timeout, unsupported jurisdiction, employees.

**What to ask:** "Where are you stuck — verification, deposit, the form, or first login?" / "What tool and roughly how many markets/min and bets/day?"

**What to tell them:** Point to the stuck step only (verify on smarkets.com / fund / form link / login recipe in A). Build order: login -> GET accounts -> GET quotes (one batched call) -> one £0.05-£1 manual-triggered bet -> then automate. No sandbox/test-mode promise.

**Flag to technical:** approval-delay disputes, jurisdiction edge cases, fee-refund disputes.

## Q. Escalate — exact handoff

Flag when: HTML 403 / edge / jurisdiction doubt; suspension/compliance dispute; "code works in docs but not my tool" debugging; cookies/auth-v2/refresh; persistent 5xx; unparseable logs; any pattern miss; limit suspension; IOC partial-fill dispute; quotes-empty dispute; approved-but-20-header mismatch; anything needing human judgement.

Handoff must include: platform (API confirmed), account approval state if known, exact symptom in CUSTOMER'S words, full error (status + error_type + data + expiry if 429 + JSON-vs-HTML), exact call (method + URL + field names, secrets redacted), expected vs actual, start time, poll rate + batch size + tool count sharing account, home vs cloud IP, what confluence section was already given. One message, key points only, no re-explained reasoning.

Routing: API bugs/codes/limits/auth/batching -> api@smarkets.com path via tech. Account/money/ID/application/RG/closed loop/fee/compliance -> support@smarkets.com path. SBK app -> support@getsbk.com / live chat 09:00-23:00 GMT / +44 207 617 7413. Outages: status.smarkets.com / @SmarketsTech.

## Copy-adapt replies (run each through Voice Core before sending)

**Login fix (no-code):** "Thanks for your message. Log in with POST https://api.smarkets.com/v3/sessions/ using `username` (your email as the value) and `password`. A working login returns 201 with a `token` — set that step to accept 200 or 201 and save `token`. Then add the header `Authorization: Session-Token <token>` to every later call and test with GET https://api.smarkets.com/v3/accounts/. Login allows 5 tries per 5 minutes, so pause before retrying if you hit a 429. Kind regards, [name] Smarkets Support"

**Logged-out loop:** "Thanks for your message. Sessions rotate about every 20 minutes, so long runs need a re-login branch: on a 401 run Login once, replace the stored token and retry that step once, then stop and alert if it fails again. For runs under 15 minutes the simplest fix is a fresh login each run with a logout at the end. Kind regards, [name] Smarkets Support"

**Quantity:** "Thanks for your message. The API counts stake in 1/10,000ths of your currency, so [their number] is [£x]. To stake [£y] send quantity [N] (pounds x 10000, minimum 500). Kind regards, [name] Smarkets Support"

**Price:** "Thanks for your message. The API counts odds as 10000 divided by decimal odds, so [their number] means [odds]. To bet at [odds] send price [N]. If a price is rejected, copy one straight from the quotes reply. Kind regards, [name] Smarkets Support"

**Rate limit + batch:** "Thanks for your message. The quotes allowance is 50 requests per 60 seconds per account, shared across every tool on the account. The fix that changes most setups is batching: quotes takes up to 200 market IDs in one call, so [their volume] needs [N] calls per sweep. Wait until [expiry / about a minute] then re-run at that batch size with one timer. We are unable to review quote limit increases at this time, once you've built a larger sample size of activity we can review and request this for you. Kind regards, [name] Smarkets Support"

**Batch 404:** "Thanks for your message. That 404 means the batch held more IDs than the endpoint takes, not that the route is dead. Quotes takes up to 200 IDs per call [volumes/states/competitors 300, contracts/last prices 100, markets by event 50]. Split to those sizes and re-run. Kind regards, [name] Smarkets Support"

**RG_ACK:** "Thanks for your message. Your account is approved — place no new application. Log in at smarkets.com and complete the Responsible Gambling acknowledgement popup (try a market page if it does not show), then retry the same API call with no other change. Kind regards, [name] Smarkets Support"

**Streaming:** "Thanks for your message. Prices come from polling the documented REST endpoints — there is no streaming or push feed for API users and the old streaming service is deprecated. Poll quotes (up to 200 market IDs per call, 50 requests per 60 seconds) on a timer instead. Kind regards, [name] Smarkets Support"

*Tune every draft: negative density count, one decision sentence last for complaints, no spec/OpenAPI wording (say "API documentation"), no api@smarkets.com reroute (we ARE support), no dates/thresholds/aggregates on increases.*

## Pitfalls specific to no-code tickets

- Treating the visual builder as the fault ("Zapier is broken") — 90% is a field name/unit/header copied wrong. Ask for the exact field names and numbers they sent.
- Asking them to run curl / read headers / parse Set-Cookie — they cannot. Ask for: status shown, error words, field names used, numbers sent, minutes-until-fail, timer cadence, ID count, home vs cloud.
- Approving limit increases, promising approval/pro promos/Select removal, quoting undocumented caps ("10 req/s general"), reciting all limits, naming sio-live/stream SDK, translating their words into codes they never used.
- Forgetting Step 0 (API vs website/SBK) on order-type/cash-out/Bet Builder questions — same words, different product answer.
- Missing exposure (available vs total), missing KIP-only survival (never "orders stay in the book"), missing CSV hour rule, missing cancel-all 1/60s danger on triggers.
- Timer-stack blindness: five 5s scenarios + balance checks + two tools = shared-pool 429 that looks like "low usage". Always ask tool count + cadence + batch size.

*Owner: API Support Team | Sources: live OpenAPI spec, docs.smarkets.com, API T&Cs, Commission FAQ, Help Centre rules/payments/RG, ticket precedents (30 Sep increase wording, 12 Oct batching briefs, 1 Oct rotation + batch-boundary probes) | If docs conflict with this page, docs win — flag the page for update.*
