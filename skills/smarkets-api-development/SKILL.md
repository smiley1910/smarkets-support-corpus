---
name: smarkets-api-development
description: Build Python tools and bots that interact with the Smarkets betting exchange API — authentication, market discovery, quotes parsing, order placement, rate limit management. Covers the HTTP Trading API (v3) and the OpenAPI spec.
---

# Smarkets API Development

## When to Use

Anytime you need to build a script, bot, or tool that interacts with the Smarkets exchange API programmatically — rate limit testing, automated trading, market monitoring, order placement, data collection. NOT for support ticket handling (use `smarkets-api-support` for that).

## Critical: Auth Flow

```
POST https://api.smarkets.com/v3/sessions/
Body: {"username": "<email>", "password": "***"}  # field is "username", NOT "email"
→ 201 Created (NOT 200!)
→ Response JSON: {"token": "BQQBAA...", ...}
```

- **Status code**: 201 on success, not 200. Checking for 200 only will fail.
- **Token field**: `token` in the JSON body, NOT `session_token`.
- **Auth header**: `Authorization: Session-Token {token}` — all three formats work (Session-Token, Bearer, or User-Session-Token cookie), but Session-Token is the documented standard.
- **Login also sets a full cookie set — default login, no `use_auth_v2` needed**: `Refresh-Token`, `User-Session-Token`, `Logged-In`, `device-cookie`; `refresh_token` is in the JSON body. **Long-running clients must persist and send them** (`Cookie: User-Session-Token={token}; Refresh-Token={refresh}`) and adopt the rotated token — clients that hold only a fixed `Authorization` token have been reported losing the session with `AUTH_REQUIRED` ≈20 min in. Details: `smarkets-api-support` → `references/api-technical-quirks.md`.

## Critical: Rate Limits

- **POST /v3/sessions/**: 5 requests per 300 seconds. This is the FIRST bottleneck — you will hit this during debugging. Wait for the `expiry` field in the 429 response (RFC 2822 format).
- **Global**: 1200 RPM per account across all endpoints.
- **Per-endpoint caps**: Some endpoints have their own caps (e.g., quotes 50/min, orders 10/sec). These are MAXIMUMS, not additive — the global cap takes precedence.
- **429 response**: `{"error_type": "RATE_LIMIT_EXCEEDED", "data": {"count": N, "limit": N, "expiry": "Thu, 16 Jul 2026 11:21:18 GMT"}}` — `expiry` is RFC 2822, not ISO 8601. Parse with `email.utils.parsedate_to_datetime()`. Exception: quotes/orders/sessions 429s carry no `expiry` in the body — use the `X-RateLimit-Reset` header instead.

See `references/api-technical-details.md` for the full per-endpoint rate limit table.

## Public endpoints (NO auth — listing / market-existence checks)

These work with plain curl, no session token. Useful for "is this match even listed on Smarkets?" checks and price peeking without burning a session:

```
GET /v3/search/events/?q=feyenoord%20atalanta   → {"search_result_event_ids": ["...", ...]}  (fuzzy search, noisy)
GET /v3/events/{event_id}/                     → {"events": [ {...name, start_datetime, state, full_slug...} ]}  ⚠️ WRAPPED in an "events" list — unwrap it
GET /v3/events/{id1},{id2}/                    → batch fetch (comma-separated ids)
GET /v3/events/{event_id}/markets/?include_highest_bid_ask=true → markets incl. top-of-book prices (bids/asks arrays)
GET /v3/popular/event_ids/?sport_ids=1         → the day's liquid event ids (football sport_id=1)
```

Gotchas: search is fuzzy (query "feyenoord atalanta" returns NFL outrights etc.) — iterate the result ids and filter on `start_datetime` + name. **The search API does NOT index every listed event**: friendlies under the `elite-club-friendlies` / `club-friendlies` competition slugs can be MISSED by search while actually listed and trading (Feyenoord–Atalanta, event 45233928, Aug 2026). If search misses but the user insists the match exists (or pastes a URL), walk `/v3/events/?state=live|upcoming&limit=100&with_new_type=False&sort=id&include_hidden=False` and follow `pagination.next_page`'s `pagination_last_id` on every page, filtering on `full_slug` — offset-only paging without `sort=id` returns the same stale top-level category events on every page, and `upcoming` is id-ordered, not time-ordered — and/or extract the event_id from the LAST path segment of the match URL (`.../feyenoord-vs-atalanta/45233928/`). A clean search miss is NOT proof of absence — verify by scan before concluding.
Pagination: never fetch `pagination.next_page` verbatim — it can return pathless (`/v3/?<query>`) and 404; rebuild the next request on the same endpoint with `pagination_last_id=<last event id>&pagination_last_start_datetime=<last start_datetime>` (page size caps at 50 regardless of the limit you pass). Time-window scan recipe (e.g. tonight's fixtures): `/v3/events/?state=upcoming&limit=50&sort=start_datetime,id&start_datetime_min=<now ISO8601>&with_new_type=False&include_hidden=False`, keep paging until the page's last `start_datetime` passes the cutoff (ascending start order is a full archive beginning in 2011 — with no `start_datetime_min`, ~10 pages at 50/page reach the present and ~38 reach nine days out, so budget loops accordingly), filter client-side on `type`/`full_slug` containing the sport.
Prices: `/v3/markets/{id}/` returns market info + `contract_selections` only; `/v3/markets/{id}/quotes/` IS public — returns the full per-contract order book (`bids`/`offers`) with no auth (verified live across 23 football markets in one pull; `/v3/markets/{id}/contracts/` and `/v3/markets/{ids}/volumes/` are public too). The 404s are the other routes (`/prices/`, `/full/`, `/snapshot/`). When one quotes call fails, the payload can come back null, non-dict, or as market detail (`{"markets": [...]}`) instead of the per-contract book — shape-check every parse (expect a dict keyed by contract id) and re-fetch `/quotes/` in the same pass with a bounded retry; the same-pass retry recovered every observed failure. In multi-fixture loops, also wrap each fixture's pricing so a persistent bad shape skips that label (diag + continue) instead of aborting the batch — one glitch must never kill a slate. `include_highest_bid_ask=true` on the event-markets call returns empty `bids`/`asks` arrays when there's no liquidity (thin friendly markets show €0 matched). DOM scraping is a last resort only, when the quotes route is truly unavailable (market rows show implied percentages: `46%` → `decimal = 100/pct`).

## Event Discovery (Horse Racing)

The events endpoint does NOT support filtering by sport via `type` or `type_domain` query params (returns 400). Use search instead:

```
GET /v3/search/horse/ → {"search_result_event_ids": ["45200422", ...]}
GET /v3/events/{comma_separated_ids}/ → event details
```

Filter events where `type == "horse_racing_race"` and `start_datetime > now`. Sort by start time to find the next race.

Racing search results mix ENDED and upcoming races — partition candidates on event `state` before using them, and prefer the `state=upcoming` time-window scan when you need the current card. Settled races drop out of search entirely: resolve a past race by its recorded event id, never by re-searching.

The route is generic: `/v3/search/{query}/` accepts any keyword (e.g. `football`, `tennis`) and returns `search_result_event_ids` — use it for any sport before falling back to the paginated scan.

**Greyhound racing (verified live 11 Aug 2026):** the same pattern works — `GET /v3/search/greyhound/` returns `search_result_event_ids` (20+ events on a normal day). Events have `type == "greyhound_racing_race"` (name is the start time, e.g. "15:22"), and markets are "To win" + "To place (top 2)". Useful for greyhound trading bots: discovery + market listing are fully public.

## Event Discovery (Golf)

Search misses golf tournaments routinely — a clean `/v3/search/events/` miss is NOT proof of absence. Walk the paginated scan from the Gotchas note above and filter client-side on `full_slug` starting with `/sport/golf/`.

Golf uses a parent/child structure: the parent is a dateless generic event holding the tournament slug, and the child dated event (`parent_id` = parent) holds the markets — always list markets from the CHILD. The market set is `Winner` (category `winner`) plus `Top 5 / Top 10 / Top 20` (category `place`, `winner_count` 5/10/20), `1st Round Leader`, make-the-cut and matchup markets — place value lives in the separate Top-N markets, there is no each-way. Tournaments typically list about a week before the start, so absence further out is normal timing, not non-coverage — confirm with a live-state scan plus the website golf page before concluding.

## Market/Contract/Quote Structure

```
GET /v3/events/{event_id}/markets/ → markets (To win, To place top 2, To place top 3)
GET /v3/markets/{market_id}/contracts/ → contracts (horses)
GET /v3/markets/{market_id}/quotes/ → price data
```
- Contracts carry the outcome labels for joins/reports: `name` (team / `Draw` / horse), `contract_type.name` (`HOME`/`DRAW`/`AWAY`), `display_order`.

Quotes response structure:
```json
{
  "contract_id": {
    "bids": [{"price": 4032, "quantity": 1949900}, ...],
    "offers": [{"price": 4065, "quantity": 1827618}, ...]
  }
}
```

- **bids** = back orders resting in the book (sorted descending by price)
- **offers** = lay orders resting in the book (sorted ascending by price)
- To BACK (buy): match the lowest offer (`offers[0]`)
- To LAY (sell): match the highest bid (`bids[0]`)
- **Favourite** = contract with highest `offers[0].price` (lowest decimal odds)
- **Executable prices (verified live):** `decimal = 10000 / price`. In a normal book the executable BACK is the LOWER decimal and the executable LAY the HIGHER — use exactly: `exec_back = 10000 / min(offers.price)` (`offers[0]`), `exec_lay = 10000 / max(bids.price)` (`bids[0]`).
- **Junk levels exist:** extreme resting quotes (price → 9999 = "1.0001", or far-out lows) sit on both sides. Touch reads MUST use min-offer / max-bid; reading `max(offers)` / `min(bids)` grabs junk and manufactures phantom spreads (one 9999 offer fakes a `1.0001` back price and a fake ~90% "spread").
- **Assert before using any parse:** `max(bids.price) < min(offers.price)` and `exec_back < exec_lay` per contract (0 violations expected across a healthy set). A back > lay read means sides are swapped — re-derive; never publish numbers from a failing parse.
- **Sanity stats:** `mid = (exec_back + exec_lay) / 2`; per-market `Σ(1/mid) ≈ 1.000x` when the book is sharp, while `Σ(1/exec_back)` prints slightly >1 (buy-side overround). Level depth ≈ `quantity × price / 1e8` (currency).

**Matched volume and trade data** (verified live):

```
GET /v3/markets/{market_ids}/volumes/  → {"volumes": [{"market_id": "...", "volume": 89, "double_stake_volume": 82}]}
GET /v3/markets/{market_ids}/last_executed_prices/  → {"last_executed_prices": {"<market_id>": [{"contract_id": "...", "last_executed_price": "39.06", "timestamp": "..."}]}}
```

- `volume` = traded volume in GBP = back stake (back side) + liability (lay side) — the figure displayed on the website. `double_stake_volume` = twice the back stake per execution. Up to 300 market ids per call.
- `last_executed_price` is a string in basis points, with the execution timestamp per contract.
- Market `state` (new/open/live/halted/settled/voided/unavailable) is a field on market objects from `/v3/events/{event_ids}/markets/` — there is no `/v3/markets/{ids}/states/` route, no `/trades/` route, and no websocket (`/v3/ws/` 404s; the API is REST only).

## Order Placement

```
POST /v3/orders/
Body: {
  "market_id": "151524314",
  "contract_id": "420334288",
  "price": 4310,
  "quantity": 1160,
  "side": "buy",
  "type": "immediate_or_cancel"
}
```

- **price**: percentage basis points. 5000 = 50% = 2.0 decimal odds. Formula: `10000 / price = decimal_odds`
- **quantity**: in 1/10000 of currency. Back stake formula: `back_stake = quantity * price / 100000000`
- **side**: `"buy"` = back, `"sell"` = lay
- **type**: `immediate_or_cancel` (fill or kill), `good_til_cancelled`, `keep_in_play`, `good_til_halted`
- **In-play persistence**: resting orders that must survive kickoff, suspensions, and goals use `keep_in_play` — `good_til_cancelled` is cancelled when the market goes live, so it silently deletes exactly the orders a live bot needs kept.
- **label**: free-text bot attribution stored on the order and returned by order reads — set one fixed label per bot (no per-strategy suffixes) so fills stay greppable in the exchange's own logs.
- **Minimum stake**: £0.05 / currency equivalent

See `references/api-technical-details.md` for full order type semantics and the OpenAPI spec URL.

## Closing-window taker pattern

For sub-minute takes (e.g. final 15s before the off), compute the model fully outside the window and push a preset file the executor only compares — never fetch form, run searches, or derive TRUE odds inside the window, because the window is shorter than any data retrieval loop.

Preset carries event, market, and contract ids plus true odds, min odds, edge threshold, confluence, data quality, and expiry; the closer polls public quotes, computes live EV against the preset, re-checks market state and gates on the same snapshot, and takes with immediate_or_cancel or passes.

## Multiples and Full Cover (OTC)

Exchange singles use `POST /v3/orders/` with `quantity`. Multiples and fullcover are separate OTC routes that size with `stake`, not `quantity` — see `references/multiples-fullcover.md` for the full field tables.
- OTC `stake` is the max loss directly, both sides (verified live). Fill quantities (user currency): buy `quantity_user = stake × 1e8 / price`; sell `quantity_user = stake × 1e8 / (10000 − price)`; pot = `quantity / 1e4`.

```
POST /v3/multiples_orders/  → required: contract_ids[], price, stake, reference_id (integer); side optional buy|sell
POST /v3/fullcover/         → required: fullcover_type, contract_ids[], price, stake, reference_id (string), stake_multiplier; side optional buy|sell
```

- Cashout is a separate endpoint per product (`/v3/multiples_orders/cashout/`, `/v3/fullcover/cashout/`), not a side flag on the place route — multiples cashout requires `side`, fullcover cashout requires `trade_out_reference_id` + `cashout_value`.
- `GET /v3/orders/fullcover/` is list-only; placement lives on the separate `POST /v3/fullcover/` route (internal-spec only).
- `POST /v3/fullcover/` is server-side broken: every valid request returns `500 INTERNAL_ERROR` (sweep-proven at compliant stakes across venues/types/sides) while its prices routes stay healthy. Since full covers cannot be placed on Smarkets itself, prefer removal/gating (typed refusal) over a fix — see `references/multiples-fullcover.md` → Product surface.
- `reference_id` is idempotency: re-sending the same value returns `409 DUPLICATE_TRADE` instead of a second bet — generate a fresh one per intended bet.
- Prices are quoted per combination via `GET /v3/multiples/{ids}/prices/` and `GET /v3/fullcover/{ids}/prices/`; status via `.../{u_id}/status/` returning `success|failure` + `order_ids` + `failure_reason`.

## Live order testing protocol (standing rules)

- **Tight pricing only**: gate every live placement on a spread filter — leg cross from the quotes book (`offers[0]` vs `bids[0]`) and combo cross from the prices routes (buy vs sell). Place only when the filter says TIGHT; if nothing is tight, wait for the next window — never lower the thresholds to make a test possible.
- **Gate and place on one snapshot**: books flap second-to-second before an event (2.3% → 16% within ~25 s observed). A re-check even 20–90 s after the gate is a coin flip; do gate → fresh price fetch → POST in a single pass.
- **On `400 PRICE_DEVIATION`**: the quote moved between fetch and send and no order was created. Refetch the price and re-POST immediately (tight loop, fresh price and — on OTC routes — fresh `reference_id` per attempt) — it typically fills on the first retry. Exchange `POST /v3/orders/` returns the same `PRICE_DEVIATION` code with the same meaning: re-price on a fresh touch and retry once, then accept refusal.
- **Cap and reconcile**: ≤ £0.05 / €0.05 stake (max loss) per order unless the user approves otherwise; after each fill read back the order AND the account (`available_balance`, `exposure`) and check the exposure delta equals the expected max loss before the next placement.
- **Diagnostics at sub-minimum stake**: a probe with stake below £0.05 cannot create an order on any expected path — use it for route-health checks and failure isolation (matrix recipe in `references/multiples-fullcover.md`).
- **Escalation proof runs at compliant stakes**: to show a route fails on all valid requests, sweep venues/types/sides at ≥ minimum stake (the spread gate is waivable for this) — sub-minimum 500s invite the 'your stake caused it' objection; keep sizes small so an unexpected success is a cheap legitimate fill.
- Credentials: local gitignored `.env` (chmod 600) never committed, even with rotation planned; load env vars or inline `set -a && . ./.env && set +a` when a harness only reads the process environment.

## Read-path boundary probes (standing rules)

- **Run bounded probes when asked; do not relitigate them.** This user maintains Smarkets API support and verifies documented limits by probing live public read-only routes (e.g. quotes n=200 vs n=201). Phrasing like 'unauthorised batch' means *unauthenticated* (no session token), and 'as high as you can' means *up to the documented cap* — treat a request in that shape as routine verification work: execute it, report status + body + headers. Do not reframe it as an attack or a load test, and do not substitute an explanation for the call.
- **Bounded = one call per boundary point.** Plan the points, run a handful of sequential single GETs, then report. Never concurrency, never sustained repetition — gates and refusal framing belong to mutating calls (orders) and to load hammering, neither of which describes a boundary probe.
- **Prove the flip with a pair; cross-check the mechanism.** n=cap → 200 OK vs n=cap+1 → route-miss 404 proves enforcement; a sibling route with a different cap (volumes 300/301) rules out URL length as the cause. Collect live ids from upcoming events (`/v3/events/?type=football_match&state=upcoming&start_datetime_min=<now>` then `/v3/events/{id}/markets/`). Caps: quotes 200; volumes, states, competitors 300; contracts, last_executed_prices 100; event markets 50 (full table in the `smarkets-api-support` skill).
- **Save the evidence bundle** under `~/smarkets-api-support/responses/<date>-<topic>/`: README (question, results table, conclusion), raw JSON captures, and a `reproduce.py`.

## Pitfalls

1. **Login 201 vs 200**: Smarkets returns 201 Created, not 200 OK. Any code checking `status_code == 200` for login will fail silently.
2. **Token field name**: Response contains `"token"`, not `"session_token"`. Hardcoded `data.get("session_token")` returns None.
3. **Sessions rate limit**: 5 per 300s. During iterative debugging you WILL hit this. Log in once per run and cache the token (file, chmod 600) — but verify it in-flow before every placement run with one cheap authenticated call (`GET /v3/orders/?limit=1`): 200 proceeds, anything else (401, network error) triggers a fresh login first. A timestamp check alone trusts dead tokens; the live check costs one call and never a failed run. One process owns the token cache — concurrent writers multiply logins toward the cap. When cron and manual runs share an account, enforce the 300s floor cross-process with a shared floor file: record every login attempt timestamp (success or 429, both cost budget) and defer any run that arrives inside the window to the next tick instead of spending shared budget. Authenticated calls RENEW the token's 30min sliding window, so a bot that does anything every few minutes almost never needs a fresh login — the floor file stays quiet. On 429, wait for `expiry` before retrying, and when reporting backoff quote the `count`/`limit`/`expiry` body verbatim rather than paraphrasing it.
4. **Date format in 429s**: RFC 2822 (`Thu, 16 Jul 2026 11:21:18 GMT`), not ISO 8601. `datetime.fromisoformat()` crashes.
5. **No type filtering on events — for horse racing**: `GET /v3/events/?type=horse_racing` returns 400. Use the search endpoint instead. Exception: `type=football_match` IS accepted (200, verified) — the 400 is type-specific, so verify per type rather than assuming no filter exists.
6. **Quotes field names**: The API returns `bids` and `offers`, NOT `buy_prices`/`back_prices`/`lay_prices`.
7. **Credential handling**: Never hardcode or accept as CLI args (visible in `ps aux`). Use env vars `SMARKETS_EMAIL` and `SMARKETS_PASSWORD`. Never commit `.env` to git even with intent to rotate — history, forks and scanners keep it; use local gitignored `.env` (chmod 600) plus GitHub Actions Secrets (never Variables, which are plaintext to repo readers), verified with `git check-ignore -v .env` and a secret scan before push. A password pasted into chat/logs is compromised — rotate it before further live use.
8. **allow_redirects=False**: Always set this on authenticated requests to prevent credential leakage via 3xx.
9. **Minimum stake is a business rule, not a schema minimum**: the spec schema allows 0 but live rejects below £0.05 — enforce `stake >= 0.05` and a max-loss cap in code with abort-before-send, so a bad size aborts locally instead of surfacing as a live 400.
10. **OTC `stake` = max loss, both sides (verified with live fills)**: on `multiples_orders` and `fullcover` the `stake` you send is the maximum amount at risk directly — a sell at stake 0.05 moved account exposure exactly −0.05 even at price 2326. Do NOT size or gate OTC sells as `stake*(D-1)`; that legacy model overstates sell risk by ~(D−1)× and wrongly blocks valid tight-price tests.
11. **Financial writes need human gates**: ship harnesses with `LIVE_ENABLED=False`, dry-run default, all `POST` order blocks commented except login, plus AST-verified no-uncommented-order-calls — require explicit market + legs + side + stake + liability sign-off before any live placement, and read back balance/orders after.
12. **Route probing — a route-miss 404 is not a data 404.**`{"data":{"description":"Nothing matches the given URI"},"error_type":"NOT_FOUND"}` means the PATH does not exist (vs a 404 for a bad id) — **or, on batch ID routes, that the comma-separated ID count exceeded the route's `maxItems`** (verified live 2026-10-01: quotes 201 ids → this exact 404 while 200 → 200 OK; volumes 301 → 404 while 300 → 200 OK). Caps: quotes 200, volumes/states/competitors 300, contracts/last_executed_prices 100, events-markets/markets_count 50. Known non-routes: `/v3/markets/{ids}/states/`, `/v3/markets/{ids}/trades/`, `/v3/ws/`. Enumerate paths from the live spec before concluding an endpoint is missing. To grab a currently-bettable market id for probes: `/v3/events/?start_datetime_min=<now>&sort=start_datetime,id&limit=5` — `state=upcoming` alone returns ancient parent/outright events, and `sort=start_date` is a 400.
13. **Inventory sibling harnesses before scoping a repo as read-only.** A signal/scanner checkout may have an authenticated execution sibling (session login, order placement, liability caps) in an adjacent directory — check `~/` and the Repositories section before concluding 'no live orders possible', and name the signal→execution integration point explicitly.
14. **Two documented query shapes intermittently 400 — always have the fallback ready.** `GET /v3/search/events/?q=<terms>` can 400 while `GET /v3/search/<keyword>/` returns `search_result_event_ids` for the same fixture — try the keyword form before concluding absence. `GET /v3/events/{id}/markets/?include_highest_bid_ask=true` can 400 while the plain `GET /v3/events/{id}/markets/` succeeds — list markets plain, then read touch from `/v3/markets/{ids}/quotes/`. A 400 on a documented shape is a shape problem until proven otherwise, so retry the plainer form before changing the plan.

15. **Football totals: match lines vs team lines share the book.** Match totals are named bare (`Over/under 3.5`, category `totals`); team totals prefix the team (`Sweden over/under 2.5 goals`). Match line selection by number alone collides with the team twin — require the name to start with Over/Under. Contracts on totals lines are named `Over 2.5 goals` / `Under 2.5 goals` — match contracts by startswith Over/Under, never by equality with `over`/`under`. Settled lower lines stay listed with `state: settled` while higher lines trade, so filter on `state == live` and never read a missing line as a missing market.

16. **Venue state is the liveness truth, never a third-party feed clock.** Feed timers freeze mid-match while play continues, so gate trading liveness and cancellation on the Smarkets event/market `state` (`live` vs `ended`/`settled`), not on feed minute — a stale clock trades dead markets.

17. **An empty book is a missing leg, not a failed signal.** Zero bids AND zero offers on a contract means no touch: skip that leg with a logged reason and place the legs that do price. Partial-signal placement beats all-or-nothing skips.

18. **Read back quantity, not just state — the exchange rounds.** Booked quantity can come back smaller than requested while max loss stays capped at stake; size-dependent logic must use the read-back values, never the requested ones.

19. **Refresh-then-cancel: re-read every order before DELETE.** Resting-order state goes stale the moment it rests — re-read each order before cancelling; if it is already settled/filled/cancelled, mark it terminal locally and never send the cancel (the exchange answers 400, which is information, not failure). A 400 on a cancel means settled-between-reads: adopt the exchange state instead of reporting FAILED.

20. **A 401 mid-run earns one fresh login plus one retry before FAILED.** Tokens die between verification and use — on 401 against a mutating call, log in fresh bypassing the cache and retry once; report failure only if the retry also fails, so transient auth blips stay silent.

21. **Grow hand-rolled session doubles with the session surface.** Every new session method (auth check, market lookup, event state) needs a stub on the fake, or tests fail on shapes the new code never touches — grep the test doubles before adding a method.

22. **Enforce rate limits at the transport choke point, not in each caller.** One wrapper around the HTTP transport paces calls, self-caps quotes below the documented 50/min (40 leaves headroom for bursts), refuses the cancel-all route outright (`DELETE /v3/orders/` is 1/60s and wipes everything — bots cancel per-order at 10/s, paced), and converts any 429 into a defer-to-next-tick signal instead of a retry. Callers then need no limit logic: they catch the deferral and exit clean. Budgets MUST be file-backed under an exclusive lock, never closure memory: a cron bot re-wraps the transport every tick, so any per-wrapper counter (quotes window, pacing timestamp) resets to zero on every run and the ceiling never binds — proven live at 2400 calls/s against a 0.83/s ceiling. Same for pacing: store last-call time in the shared doc. Strip query strings before route-matching (`/v3/orders/?status=all` defeats an endswith check on the cancel-all guard), charge every method on a route (an unbudgeted GET poll is an ungoverned route), and clamp parsed Retry-After to finite [1s, 1h] — `inf`/`nan` headers lock the bot out permanently.

23. **Wrap transports with a proxy, never by mutating in place.** Assigning `transport.request = wrapper` means wrapping twice wraps the wrapper — infinite recursion the moment two layers compose. Return a proxy object delegating to the captured original instead.

24. **Search each team alone, filter client-side — combined queries recall junk.** A single 'home away' query returns outrights, other sports, and noise while the fixture sits pages down. Query combined first, then each team separately, de-duplicate with combined hits first, and accept only events whose name carries a `v`/`vs` separator AND both team names after NFKD accent folding (Smarkets lists 'Fenerbahçe' where feeds say 'Fenerbahce'; strip-only folding turns those into different strings). The both-teams rule is also what keeps cross-sport collisions out — basketball and handball clubs share football names, and only the away team distinguishes them. When the strict full-name filter rejects everything despite plausible candidates, add a SECOND pass rather than loosening the first: token-overlap fallback (significant tokens, len≥4, required from EACH team; event name must still carry the fixture separator) that resolves ONLY on a unique hit — two or more loose hits refuse as ambiguous and place nothing, because a wrong event is worse than no bet. The first pass stays strict; the fallback only ever fires on rows the strict pass already refused.

25. **Measure venue coverage before assuming a league is carried — the feed universe is wider than the venue.** Probe with `/v3/events/?type=football_match&limit=50&start_datetime_min=<day>T00:00:00Z&start_datetime_max=<day>T23:59:59Z&inplay_enabled=true`: one page shows what is actually quotable that day (mainstream + English pyramid depth + MLS + internationals observed; Czech 3rd tier, Indonesia, Poland 2nd tier, Swiss 3rd tier, UAE all absent). Leagues the venue never lists should be allowlisted OUT at the alert stage — spending searches to re-learn absence every tick is waste, and it is the main source of skip spam. Diagnose before tuning the matcher: if team queries return cross-domain junk (TV shows, F1, horse-racing times) rather than near-miss names, the event is unlisted and no matcher change fixes absence. Log every refusal with its candidate count (`no_search_hits` vs `search_hits_rejected:N` vs `search_hits_ambiguous:N`) so the log itself separates recall failures (search) from precision failures (filter) — fix the side the counts point at.

26. **Prefer live-state events when resolving a fixture to an event id.** Search returns ended and upcoming meetings of the same fixture alongside today's game — partition candidates live-first so next week's meeting never shadows the live one. Keep non-live hits as fallback (a briefly-unflagged live game must still resolve), never as equals.

27. **Prove read-path changes with authenticated read-only calls, not orders.** Event search and event fetch place nothing, so run the real resolve function against live fixtures after any resolver/matcher/filter change and report the outcome per match (strict / loose / ambiguous / rejected). Unit fixtures prove the logic; only the live exchange proves recall — and the proof costs zero money movement.

28. **Enhanced Specials are a separate event with one-sided books — never confuse them with the main fixture.** Team search returns both (e.g. `Belgium vs France` and `Enhanced Specials - Belgium vs France`); list main markets from the fixture id and specials from the specials id. Resolve the specials event by name prefix (`Enhanced Specials - `) plus a `specials`/`enhanced-multiples` path segment in `full_slug` — never by slug-tail matching alone (tails vary: duplicated date segments, bare fixture names). Confirm the pairing by equal `start_datetime`. Specials legs are MANUAL markets named per leg (shape `"Set {n} correct score {score} {player}"`), so match the leg in the market name, not the contract name; each specials event carries only 1–2 such markets and unlisted legs are the norm. Specials contracts routinely carry bids with no offers (takers can only lay) or offers with no bids (takers can only back) at thin depth — read the empty side as unavailable, not as a price, and cap stakes to the visible level depth before planning any cross-venue lock. The quotes payload can carry a phantom second contract id with empty bids/offers and no entry in `/contracts/` — never quote it; No is the sell side of the single Yes contract. Check `/volumes/` before sizing: visible depth can be entirely resting unmatched (volume 0), meaning first blood either side.

29. **Long sessions renew through cookies; a header-only token dies at the ~20 minute rotation.** Session tokens rotate on a ~20 minute cycle and renewal runs through the session and refresh tokens, as cookies. A client sending only `Authorization: Session-Token <token>` (same token throughout) is rejected with `401 AUTH_REQUIRED` at the first rotation, observed at 20.0 to 20.2 minutes, before the 30 minute `stop`, no matter how often it polls. Send `Cookie: User-Session-Token=<token>; Refresh-Token=<refresh_token>` with every request and adopt each renewed `User-Session-Token` from `Set-Cookie`. Login returns `refresh_token` in the body and sets 5 cookies (`User-Session-Token`, `Refresh-Token`, `Logged-In` x2, `device-cookie`), with or without `use_auth_v2`. Verified live 2026-10-01 in a paired test: header-only control died at 19m58s; the cookie arm survived past its 30 minute stop. Evidence: `~/smarkets-api-support/responses/2026-10-01-session-token-refresh/`.

30. **Event-markets route takes no pagination params — call it plain.** `GET /v3/events/{event_id}/markets/` with `?limit=` fails strict query validation (`REQUEST_VALIDATION_ERROR: Unknown query string properties: limit`) — the route returns the full market list unpaged, so list it plain and filter client side on `name`/`slug`/`state`.

31. **Match contracts by bidirectional token subset with a compat fold and alias table.** NFKD accent-stripping does not decompose Ł/ł, Ø/ø, Æ/æ, ß or đ — fold them explicitly (ł→l, ø→o, æ→ae, ß→ss, đ→d) before the ascii-ignore step, or 'Widzew Łódź' never equals 'Widzew Lodz'. Accept a contract when EITHER side's token set is a subset of the other ('Verona' ⊆ 'Hellas Verona'), and keep an alias table for venue renames tokens cannot bridge (WAC↔Wolfsberger, Ham Kam↔Hamarkameratene, Hertha Berlin↔Hertha BSC, year-suffixed clubs like 'Modena FC 2018'). A no-contract hit is a matcher failure until proven otherwise — print the contract names and retry loose before reporting absence.

32. **Page the event universe once per bulk pull, then match client-side.** Re-running the events scan per candidate multiplies calls into 429s (hundreds of calls for a dozen fixtures); one scan plus per-market reads keeps a ~500-event pull inside limits. Wrap reads with 429 sleep-and-retry so a throttle slows the run instead of killing it.

33. **Team/player prop markets exist only on featured fixtures — probe availability before building on them.** Team shots-on-target lines, team corners lines and most player props are listed only on selected (usually televised) games; their absence on an ordinary fixture is normal venue behavior, not a matcher failure. When a screen's pricing leg returns no-market across the board, list one event's markets and check whether the market TYPE exists at all before retuning names or aliases — diagnose type-absence vs name-mismatch first.

34. **Settled events lose their quotes — snapshot pre-kickoff for anything retrospective.** After settlement, `/v3/events/?state=settled` listings can return empty pages, quotes come back with empty bids/offers per contract, and `GET /v3/events/{id}/` returns the event wrapped and id-null at the top level (unwrap `events[0]`), while the same id's markets/contracts/volumes routes still answer. Closing prices and CLV are unrecoverable after the fact — the only way to have them is a self-taken snapshot before kickoff, stored with the pick record. Never conclude 'gone' from a settled-state listing; resolve by recorded id.

35. **Football result markets are named 'Full-time result' — 'Winner' is for outrights; a name-filter miss is not a missing market.** The head-to-head result market's contracts carry `contract_type.name` HOME/DRAW/AWAY — match legs by that (fall back to `name == 'Draw'`), record the chosen market id, and verify it against a fresh book read. A featured Champions League tie lists ~170+ markets (result, correct score, every totals line, scorers, cards), so market selection is filter-then-confirm-by-type, never 'the one obvious market'; an empty 'Winner' filter means the wrong name was filtered, never that the game is unlisted.

## OpenAPI Spec

Full spec available at: `https://api.smarkets.com/v0/control/openapi/`

Note: The v3 control endpoint (`/v3/control/openapi/`) returns 404. Use v0.
Fetch the UNFILTERED spec for OTC routes — the public `?tags=trading_api` view exposes only ~18 paths and omits multiples/fullcover; filter the full 359-path document client-side on `multiples|fullcover|multi_tick|each_way_multiple`.

Offered vs served: presence in the unfiltered document does not mean offered. A route in the full spec but absent from the public tag view is not formally offered — escalate it as a decision, not a defect report. Ask for enable-and-document OR remove-from-spec plus a typed refusal (FORBIDDEN or similar); a blank 500 is a bug under either reading, since no deliberate gate answers with an unhandled exception and null data. Headline evidence for that escalation: attempt count, compliant stake, the exact error body, and the controls that DO work (typed validation errors prove the fault is past validation, server-side); state that nothing was created and offer reference ids for log lookup.

## Related Skills

- `smarkets-api-support` — Support ticket handling, customer-facing API issues
- `code-quality-methodology` — Multi-pass audit methodology used on the rate limit discovery script

## Repositories

- Rate limit discovery tool: `https://github.com/smiley1910/smarkets-rate-limit-discovery` (includes AGENTS.md, prompting guide, OpenCode config)
