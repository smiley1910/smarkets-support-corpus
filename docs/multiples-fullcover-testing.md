# Multiples & Full Cover — Test Plan and Known Facts

> **Status: LIVE FINDINGS 2026-09-24 appended (§13).** Multiples buy+sell placed and filled;
> fullcover placement swept to proof as server-side broken (46/46 HTTP 500). The risk models in
> §2–§3 are SUPERSEDED by §13 where they conflict.

---

## 1. Purpose and Scope

This document plans four live order tests on Smarkets — buy multiple, sell multiple, buy full cover, sell full cover — each capped at **£0.05 worst-case liability**. It records only what is verified from the live API spec; anything unverified is explicitly marked as an open question for the spec worker.

## 2. The Four Test Cases

The test set is exactly four placements: `buy_multiple`, `sell_multiple`, `buy_fullcover`, `sell_fullcover`, each at stake £0.05 and (for sells) price conditions that keep risk ≤ £0.05. Cashout endpoints are included in scope as read-only first (prices/offers), with placement forms documented but not exercised initially.

| # | Case | side | Endpoint (candidate) | Worst-case risk target |
|---|------|------|----------------------|------------------------|
| 1 | buy multiple | buy | `POST /v3/multiples_orders/` | £0.05 (stake) |
| 2 | sell multiple | sell | `POST /v3/multiples_orders/` | £0.05 (stake × (D−1)) |
| 3 | buy fullcover | buy | `POST /v3/fullcover/` | £0.05 (stake × lines) |
| 4 | sell fullcover | sell | `POST /v3/fullcover/` | £0.05 (per-line model) |

## 3. Price, Quantity and Liability Math

All order economics use integer `price` (basis points of 1, `D = 10000 / price`) and integer `quantity` (units of 1/10000 GBP), with `back_stake = quantity × price / 100000000`. Risk is the back stake for a buy and `stake × (D − 1)` for a sell, so a sell at £0.05 stake only fits the £0.05 cap when price ≥ 5000. **SUPERSEDED by live testing (2026-09-24): for OTC orders the `stake` field is the max loss directly, both sides — the `stake × (D − 1)` sell model overstates risk and must not be used for sizing or gating (see §13.1).**

| stake | price | D = 10000/price | quantity | pot | back stake | buy risk | sell risk |
|-------|-------|-----------------|----------|-----|------------|----------|-----------|
| £0.05 | 2000 | 5.0 | **2500** | £0.25 | £0.05 | £0.05 | £0.20 |
| £0.05 | 5000 | 2.0 | **1000** | £0.10 | £0.05 | £0.05 | £0.05 |
| £0.0005 | 5000 | 2.0 | 10 | £0.001 | £0.0005 | — | — |

Verified against the spec's own worked example: quantity 100000 @ price 5000 → £5.00 back stake, pot £10.00.

## 4. Minimum Stake and the "0.05c" Size Error

The minimum stake is **£0.05** ("The minimum stake is £0.05 or currency equivalent" — live `quantity` field description); the schema floor is `minimum: 0`, so this is a business rule enforced at validation. A request for "0.05c" (= £0.0005) is 100× below the minimum in every reading and will be rejected (candidate error `ORDER_INVALID_INVALID_QUANTITY`).

## 5. Authentication and Session Handling

Login is `POST /v3/sessions/` with `{"username", "password"}`, expecting HTTP **201** with a `token` field (rate limit 5 requests / 300 s). The token goes in the `Authorization: Session-Token <token>` header, is valid for 30 minutes with sliding renewal, and must never be logged or written to disk.

## 6. Read-Only Pre-Flight

Before any payload validation, the harness runs only read-only calls: credentials from `SMARKETS_EMAIL` / `SMARKETS_PASSWORD` env vars, login, `GET /v3/balance/` (`{"balance": "..."}`) plus `GET /v3/accounts/` for `available_balance`/`exposure`, then market discovery. Discovery walks events → markets → volumes → quotes to propose liquid markets, and for sell cases it must pick legs whose combined price is ≥ 5000.

## 7. Candidate Placement Endpoints (multiples / fullcover)

Both placement routes were found in the unfiltered live OpenAPI document (359 paths) but are absent from the public `trading_api` tag view, so availability and required fields are **UNCONFIRMED** for this account. The payload shapes below are candidates only — the spec worker must confirm each field's semantics before any live call.

| Route | Required fields (live schema) | Notes |
|-------|-------------------------------|-------|
| `POST /v3/multiples_orders/` | `contract_ids`, `price`, `stake`, `reference_id` | `side` (buy/sell), `granular_errors` optional; `reference_id` typed **integer** |
| `POST /v3/fullcover/` | `fullcover_type`, `contract_ids`, `price`, `stake`, `reference_id`, `stake_multiplier` | `reference_id` typed **string**; `stake_multiplier` semantics unknown (example=3) |

## 8. Candidate Cashout Endpoints

Cashout is available in several shapes (fullcover, multiples, multi-tick, per-market) and all are candidates pending confirmation; read-only price/offer routes should be used first. The market cashout amount is an integer in *decimals* (400 = £4.00), which is a different unit convention from `quantity`.

| Route | Method | Required fields |
|-------|--------|-----------------|
| `/v3/fullcover/cashout/` | POST | `reference_id`, `trade_out_reference_id`, `cashout_value` |
| `/v3/multiples_orders/cashout/` | POST | `contract_ids`, `price`, `quantity`, `side`, `reference_id` |
| `/v3/multi_tick_orders/cashout/` | POST | `contract_id`, `price`, `quantity`, `reference_id` |
| `/v3/markets/{market_id}/cash_outs/` | POST | `amount` (int, decimals) |
| `/v3/fullcover/cashout/prices/` | GET | `trade_out_reference_id` (query) |
| `/v3/multiples/cashout/{contract_ids}/prices/` | GET | `side`, `traded_out_order_id` (query) |

## 9. Safety Model: Dry-Run Gates and the Human Gate

The harness (`scripts/test_multiples_fullcover.py`) never places an order by default: live POST blocks are commented out and `Client.post_order()` is hard-blocked by `LIVE_ENABLED = False`. Every candidate payload must pass three dry-run gates — schema check, minimum-stake check, and liability-cap abort if worst-case risk > £0.05 — and a guard self-test must prove each abort actually fires.

Four explicit confirmations are required before any live placement:

1. **MARKET** — market_id + every leg contract_id verified by a human against the live market page.
2. **SIDE** — buy/sell matches the intended test case.
3. **STAKE** — stake value confirmed, including whether a fullcover stake is total or per line.
4. **LIABILITY** — worst-case liability confirmed ≤ £0.05 under the spec-worker-confirmed risk model.

## 10. Open Questions for the Spec Worker

Ten blocking questions are tracked in the harness (section `[6c]`) covering route availability, `stake`/`stake_multiplier` semantics, sell-side risk model, fullcover line exposure, minimum-stake interpretation, error code for below-minimum stakes, and valid price ticks. Placement endpoints stay commented out until every question that affects a given case is answered.

## 11. Runbook

Run `python3 scripts/test_multiples_fullcover.py --math` for the deterministic liability tables and `--dry-run` for the full offline validation report (add `--read-only-live` to include login/balance/discovery once credentials are set). Live placement is a separate, deliberate uncommenting step and requires the human gate above; the file is never edited to enable live orders as part of a dry-run.

## 12. Evidence and Provenance

Primary evidence is the live OpenAPI document at `https://api.smarkets.com/v0/control/openapi/` (unfiltered: 359 paths; fetched 2026-09-24) plus the field descriptions quoted verbatim above. A machine-readable extract of the candidate routes is kept at `openapi/multiples_fullcover_endpoint_candidates_2026-09-24.txt` for the spec worker.

---

## 13. Live findings 2026-09-24 (verified, test account, EUR)

Full probe artifacts (payloads, statuses, readbacks) live in the private `smarkets-multiples-tester` repo log (`docs/multiples-fullcover-testing.md`, "part 2" + "dynamic sweep" sections). No probe below ever created an unintended order; account finished at 8 orders, 0 fullcover orders, €9.90 available / −€0.10 exposure.

### 13.1 Multiples: buy and sell both placed and filled

- Buy multiple filled: order 203610581549277193 (Thunder Goddess 459046108 + King Sharja 459046903).
- Sell multiple filled: order 203610591347208201, side sell, price 2326, stake 0.05.
- **`stake` = max loss directly, both sides.** The sell fill moved account exposure exactly −0.05. This SUPERSEDES the §2–§3 model (`stake × (D−1)`, "price ≥ 5000 to fit £0.05") — that model overstates OTC sell risk and must not be used for sizing or gating.
- First sell attempt died with `400 PRICE_DEVIATION` (quote moved between fetch and send; nothing created). Fix: tight fetch→place loop with a fresh price per attempt.
- `reference_id` is integer on `POST /v3/multiples_orders/`. Status polling takes the `bet_id` as `u_id` (`GET /v3/multiples/{ids}/{bet_id}/status/` → `{status: success}`).

### 13.2 Fullcover placement: server-side broken, swept to proof

- 46 `POST /v3/fullcover/` attempts → **46 × HTTP 500 `{"data": null, "error_type": "INTERNAL_ERROR"}`** (~0.1 s each). Stakes 0.05 and 0.10 (both compliant: at/above the £/€0.05 minimum, inside max stake). Refs 202609242001–202609242046 plus earlier 202609241401 (0.05) and 202609241801 (0.10).
- Coverage: horses (two trios, 4-leg, 5-leg), football (six matches, 3/4/5-leg), basketball, mixed-sport trio; all ten types the pricing route offers (singles, doubles, trebles, four_fold, trixie, patent, yankee, lucky_15, lucky_31, super_yankee) with leg counts and `stake_multiplier` taken from each prices row; buy and sell.
- Working alongside: `GET /v3/fullcover/{ids}/prices/` 200 buy+sell (with `contract_group_prices`; doubles price = harmonic mean of pair prices); schema validation proven live (integer ids → `400 REQUEST_VALIDATION_ERROR "data.contract_ids[0] must be string"`; 2 legs → `400 NOT_ENOUGH_FULLCOVER_CONTRACTS`). Only *valid* requests die at 500.
- Conclusion: unconditional for valid order requests — not spread, venue, sport, type, side, stake size, or leg count. Escalation filed with account ID + refs + time window.
- Docs position: the public `trading_api` tag view (18 paths, verified live 2026-09-24) references full cover exactly once — `GET /v3/orders/fullcover/` ("Get all fullcover orders for an account"). Placement routes exist only in the internal full spec.
- Product position: full cover types are documented in SBK help and the SBK bet slip carries full cover support behind a feature flag ("Fullcovers disabled by feature flag"); the Smarkets web app has only error mappings, no placement UI. Since full covers cannot be placed on Smarkets itself, the recommendation is removal/gating of the placement route (or a typed refusal such as FORBIDDEN), not a fix.

### 13.3 Sibling OTC routes (all healthy — use for ban/backoff checks)

- `POST /v3/multi_tick_orders/` → clean `400 STAKE_TOO_LOW` below min. `GET /v3/multi_tick_orders/{ids}/bulk_prices/` → `{contracts: [{contract_id, prices[], max_stakes[]}]}`.
- `POST /v3/each_way/` (atomic each-way: `win_contract_id`, `place_contract_id`, `win_price`, `place_price`, `stake`) → reaches validation. `GET /v3/each_way/{win}/{place}/prices/` → `{win_price, place_price, max_stake, price_error}`.
- `reference_id` types: multiples_orders integer; fullcover string; each_way integer (`"data.reference_id must be integer"`); multi_tick_orders integer.
- `reduction_factor` lives on the `contract` schema (spec example `"0.45451"`) and surfaces via `GET /v3/contracts/{ids}/` — absent/`None` means no reduction applied. After a withdrawal/non-runner, re-read the same leg contracts to catch it.
- Account-health pattern (rules out ban/backoff before escalating any route): fresh login 201 + healthy reads + one sub-min POST on a known-good sibling route returning its typed 400. A lone 401 is a stale token until re-login proves otherwise.
