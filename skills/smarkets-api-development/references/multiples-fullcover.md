# Multiples and Full Cover — OTC Endpoint Reference

Source: unfiltered OpenAPI `https://api.smarkets.com/v0/control/openapi/` (359 paths). Auth: `Authorization: Session-Token` header on all routes below except `GET /v3/multiples/popular_multiples/`. Public `trading_api` tag view exposes 18 paths and references full cover exactly once (`GET /v3/orders/fullcover/`); placement routes below are internal-spec only. Live findings and harness: private repo `smarkets-multiples-tester` (`docs/multiples-fullcover-testing.md` = running findings log, `scripts/test_multiples_fullcover.py` = live test harness) — check the log for current route status before re-deriving semantics.

## Place routes

### POST /v3/multiples_orders/ (operationId place_multiple_order)
Required: `contract_ids` (string[], each `^[0-9]+$`), `price` (int 1..9999 basis points, `10000/price` = decimal), `stake` (number, e.g. 24.08), `reference_id` (integer). Optional: `side` (enum buy|sell), `granular_errors`, `promotion_id`, `bet_token_id`. No `market_id`, no `type`, no `quantity`. Response: `order_id` (id string, or temp uuid during bet delay) + `bet_delay`, `bet_id`, `contract_id`, `market_id`.

### POST /v3/fullcover/ (operationId place_fullcover_order)
Required: `fullcover_type` (e.g. doubles), `contract_ids` (string[]), `price` (int 1..9999), `stake` (number), `reference_id` (STRING), `stake_multiplier` (integer — unconfirmed; best inference = `number_of_bets` from the prices call). Optional: `side` (buy|sell), `cover_depth` (default 0), `ew_contract_ids`, `ew_price`, `bet_token_id`, `promotion_id`. Response: `reference_id` + `bet_delay`, `bet_id`, `estimate`, `failure_reason`, `win_bet_id`, `place_bet_id`. Poll `GET /v3/fullcover/{u_id}/status/`.

### Adjacent singles
- `POST /v3/multi_tick_orders/` — singular `contract_id`, required `contract_id, price, stake, reference_id`, no side.
- `POST /v3/each_way/` — atomic each-way, required `win_contract_id, place_contract_id, win_price, place_price, stake` (+ integer `reference_id`); prices via `GET /v3/each_way/{win}/{place}/prices/`.
- `POST /v3/each_way_multiple/` — required `win_contract_ids, place_contract_ids, win_price, place_price, stake, reference_id`, no side.

## Cashout routes (separate endpoints)

- `POST /v3/multiples_orders/cashout/` — required `contract_ids, price, quantity, side, reference_id` (side REQUIRED here).
- `POST /v3/fullcover/cashout/` — required `reference_id, trade_out_reference_id, cashout_value`.
- `POST /v3/multi_tick_orders/cashout/` — required `contract_id, price, quantity, reference_id`, no side.
- Quotes: `GET /v3/multiples/cashout/{ids}/prices/` and `GET /v3/fullcover/cashout/prices/?trade_out_reference_id=`.

## Prices and status

- `GET /v3/multiples/{contract_ids}/prices/` (ids maxItems 300) and `GET /v3/fullcover/{contract_ids}/prices/` (ids maxItems 10); both accept optional `side=buy|sell`.
- Status: `GET /v3/multiples/{ids}/{u_id}/status/`, `GET /v3/fullcover/{u_id}/status/` → `{status: success|failure, order_ids[], failure_reason}`.
- `GET /v3/orders/fullcover/` is a GET-only account list (params `states, limit, pagination_last_id`); there is no POST at that path.

## Errors and idempotency

- Reusing `reference_id` returns `409 DUPLICATE_TRADE` — this is the retry guard, so mint a fresh id per intended bet.
- Live minimum legs: 2 legs on `GET /v3/fullcover/{ids}/prices/` returns `400 NOT_ENOUGH_FULLCOVER_CONTRACTS` — plan 3+ legs for any fullcover price or place call, and confirm leg count before sizing stake against the liability cap.
- Exotic types need their exact leg count — it is full cover THEN the exotic type, not a 3-leg shape with a different label: 3 legs → singles 3, doubles 3, trixie 4, patent 7; 4 legs → singles 4, doubles 6, trebles 4, yankee 11, lucky_15 15; 5 legs → singles 5, doubles 10, trebles 10, four_fold 5, super_yankee 26, lucky_31 31 (type → bets; the prices response lists exactly which types exist for the leg set given — probe the rows it returns, don't guess names). Fetch prices for the real leg set, take that row's own `number_of_bets` as `stake_multiplier`, and only then conclude the route is broken — a 500 on a 3-leg yankee proves nothing, a 500 on a server-priced 4-leg yankee with matched multiplier does.
- Below-minimum stake surfaces as HTTP 400 — `STAKE_TOO_LOW` confirmed live (multi_tick at stake 0.004); fullcover adds `INVALID_FULL_COVER_TYPE`, `STAKE_MULTIPLIER_NOT_MATCH`, `TOO_MANY_FULLCOVER_CONTRACTS`.
- Spec inconsistency to code around: multiples prices `contract_ids` description says minItems 300 but schema says minItems 2 — trust the schema and validate live.

## Verified live semantics (OTC orders)

- **`stake` = max loss directly, both sides.** A live sell at price 2326 with stake 0.05 moved account exposure exactly −0.05 (available €9.95 → €9.90). The legacy `stake*(D-1)` model overstates sell risk — do not size or gate OTC sells with it.
- Fill quantities (user currency, 1/10000 units): buy `quantity_user = stake × 1e8 / price`; sell `quantity_user = stake × 1e8 / (10000 − price)`. Back stake = `quantity × price / 1e8`; pot = `quantity / 1e4`. Raw `quantity` fields are GBP-denominated on a EUR account — apply the FX ratio (~1.16) before comparing with `*_user_currency` fields.
- Fullcover prices carry `contract_group_prices` — every combination's price. The `doubles` price equals the harmonic mean of the three pair prices (`3 / Σ(1/p_i)`); fullcover buy and sell quote the same number.
- `reference_id` types: multiples_orders → integer; fullcover → string; each_way → integer (string rejected: `data.reference_id must be integer`); multi_tick_orders → integer.
- Sibling price routes: `GET /v3/multi_tick_orders/{ids}/bulk_prices/` → `{contracts: [{contract_id, prices[], max_stakes[]}]}`; `GET /v3/each_way/{win}/{place}/prices/` → `{win_price, place_price, max_stake, price_error}`.
- `reduction_factor` lives on the `contract` schema (spec example `"0.45451"`) and surfaces via `GET /v3/contracts/{ids}/` — absent/`None` means no reduction applied to that contract. After a withdrawal/non-runner, re-read the same leg contracts (plus any combined multiple contract) to catch it.

## Probing a failing OTC order route (safe sub-min matrix)

Isolate the layer with a bounded probe matrix — every probe at stake below the minimum (e.g. 0.004), so no order can be created on any expected path:

1. Prove the validator works: send a deliberately wrong type (e.g. `contract_ids` as ints) and expect a clean `400 REQUEST_VALIDATION_ERROR` with a JSON-path message.
2. Vary ONE dimension per probe: contract set, `side`, `fullcover_type`, `stake_multiplier`, `cover_depth`, side omitted, leg count. Two or three probes per dimension exhausts it.
3. Compare with the read-only routes: if prices return 200 and validation returns 400 while every valid shape 500s, the fault is server-side — stop reshaping the request, document the matrix, set a recovery watcher (repeat one sub-min probe on a timer, exit on first non-500) and escalate. Rule out account/ban/backoff first with one sub-min POST on a known-good sibling route (expect its typed 400, e.g. `STAKE_TOO_LOW`) — fresh login plus healthy reads plus a typed sibling 400 proves the account is fine, and a lone 401 anywhere is an expired token until re-login proves otherwise. Before escalating, run the proof sweep at a compliant stake (see 'Proof sweeps' below) and cite only compliant sizes in the ticket headline; sub-min probes go in the appendix, never the headline. Refresh the session token on every watcher probe (or re-login on 401 before declaring change) — a stale cache returns `401 AUTH_REQUIRED`, which mimics a route change but is only an expired token. This pattern identified a server-side break of `POST /v3/fullcover/` placement while its prices routes stayed healthy — if it recurs, re-run the matrix rather than assuming the request shape is wrong.
4. After every wave, verify no order was created: route-specific orders list + general orders + account exposure unchanged — and say so explicitly in the write-up. Save a per-run JSON artifact (payloads, statuses, readbacks) and re-read it before the next wave — do not work from truncated terminal scrollback.

Notes: on a healthy route a sub-min probe returns `STAKE_TOO_LOW` (clean 400) — that is the pass signal, not a failure. A 500 on a probe does not create an order, but verify account state anyway.

**Proof sweeps (escalation evidence).** To show a route fails on ALL valid requests, not just one shape, sweep at a COMPLIANT stake (minimum or slightly above) with the spread gate waived when the user asks for it: vary venue/sport (horses, football, basketball, mixed-sport), probe every `fullcover_type` the prices rows return, and both sides. Compliant sizes close the 'maybe the sub-min stake caused it' objection; keep each attempt small-compliant so an unexpected success is a cheap legitimate fill, and stop the sweep on any non-500 to read back. Once a route has been swept to all-500 across venues/types/sides, that conclusion stands — renewed doubt is answered from the sweep's dimensions, and recovery is confirmed with ONE compliant attempt rather than rebuilding the sweep.

## Product surface (full cover)
- Full cover bet types are documented in SBK help; the SBK bet slip carries full cover support behind a feature flag (`Fullcovers disabled by feature flag`). The Smarkets web app has only error mappings (`LIVE_FULLCOVER_UNSUPPORTED` = in-play selections not supported), no placement UI.
- Since full covers cannot be placed on Smarkets itself, a failing placement route should be removed/gated (or return a typed refusal such as FORBIDDEN), not fixed — escalate with account ID + `reference_id`s + time window, citing only compliant sizes in the headline.
