# Q2/Q3 Evidence Brief — Lay Multiples (cross-event) & Builder Markets via API

Scope: Q2 cross-event multiples via API; Q3 builder-related markets (correct score, winner+BTTS, winner+total goals), permissions, back-only position.
Excluded: policy, fees, rate limits, order safety.
Specs: `openapi/smarkets_openapi.json` = `scrape-aug18/live_trading.json` (18 paths, tag `trading_api`). `scrape-aug18/live_full.json` = `/v0/control/openapi/` full surface (360 paths, incl. web/app). Build revision `ac919ea7a59fe6c0b3abead3188ac749485feffc` (scraped 2026-08-18).

---

## Q2 — LAY MULTIPLES (CROSS-EVENT) VIA API

```
cross_event_multiples_via_API:
  Y (partial) — via pre-created accumulator MARKETS traded as ordinary single
                contracts on the documented trading API.
  N (for builder-style) — no multiples quote/submit/status endpoint exists in the
                18-path trading spec; those live only in the full spec (tag 'otc').

endpoints (documented trading spec — openapi/smarkets_openapi.json, live_trading.json):
  GET    /v3/events/                              Retrieve events that are available on Smarkets to bet on.
                                                  [type_scope enum incl. acca, acca_root, acca_category]
  GET    /v3/events/{event_ids}/markets/          Retrieve markets by event ids. Each market will have a set of contracts.
                                                  [markets[].contract_selections "only set for accumulator markets"; categories enum incl. bet_builder]
  GET    /v3/events/{event_ids}/markets_count/    Retrieve markets_count by event ids.
  GET    /v3/markets/{market_ids}/contracts/      Retrieve contracts by a set of market ids.
  GET    /v3/markets/{market_ids}/quotes/         Get the current prices from the exchange.
  GET    /v3/markets/{market_ids}/last_executed_prices/  Retrieve the last executed price and timestamp for each contract.
  GET    /v3/markets/{market_ids}/volumes/        Retrieve traded volumes by market ids.
  POST   /v3/orders/                              Place orders on the exchange. [side enum: buy|sell]
  GET    /v3/orders/                              Retrieve current orders... (open and recently settled orders).
  DELETE /v3/orders/{order_id}/                   Cancel specific order.
  DELETE /v3/orders/                              Cancel all orders.
  GET    /v3/orders/fullcover/                    Get all fullcover orders for an account. [READ-ONLY]

endpoints (full spec only — scrape-aug18/live_full.json, tag 'otc'; NOT in trading_api tag):
  GET    /v3/multiples/{contract_ids}/prices/     Create an entry for and get the price of a multiple based on the given contract ids.
  POST   /v3/multiples_orders/                    Place a multiple order for the given contract ids at the given price and stake.
  GET    /v3/multiples/{contract_ids}/{u_id}/status/  Get multiple order status by reference id.
  GET    /v3/multiples/popular_multiples/         (popular pre-built multiples)
  GET    /v3/multiples/random/{num_legs}/         (random multiple generator)
  GET    /v3/multiples/{contract_ids}/cached_prices/
  GET    /v3/multiples/cashout/{contract_ids}/prices/ ; POST /v3/multiples_orders/cashout/
  POST   /v3/fullcover/                           Place a fullcover order for the given contract ids at the given price and stake.
  GET    /v3/fullcover/{contract_ids}/prices/     Get the price averaged across all contracts for a fullcover bet.
  GET    /v3/fullcover/{u_id}/status/             Get the status of the full cover order with the given reference id.
  POST   /v3/fullcover/cashout/ ; GET /v3/fullcover/cashout/prices/

quote_endpoint:
  DOCUMENTED: GET /v3/markets/{market_ids}/quotes/  ("Get the current prices from the exchange.")
              — works for any market incl. an accumulator market's contracts.
  MULTIPLES-SPECIFIC: GET /v3/multiples/{contract_ids}/prices/  (full spec only; query side enum buy|sell;
              path contract_ids minItems 2, maxItems 300)

max_stake_endpoint_or_STATE_NOT_DOCUMENTED: STATE_NOT_DOCUMENTED
  - No max-stake endpoint or field in the trading spec.
  - POST /v3/orders/ quantity description documents ONLY "The minimum stake is £0.05 or currency equivalent";
    quantity maximum 4294967295 is a uint32 bound, not a business limit.
  - Undocumented limit signal: account-activity source enum contains "order.reject.stake_limit_exceeded"
    (live_trading.json, GET /v3/accounts/activity/ source enum).
  - Customer-facing (website, not API): help page 212727285 "The minimum stake is £/€ 0.05 and the maximum
    stake per bet is £/€ 99,999.99."

submit_endpoint:
  DOCUMENTED: POST /v3/orders/  ("Place orders on the exchange.") — single market_id + contract_id + price +
              quantity + side; returns order_id. Rate: "Maximum 10 requests per second".
  MULTIPLES: POST /v3/multiples_orders/ (full spec only; required contract_ids, price, stake, side, reference_id;
              request fields incl. bet_token_id, free_bet_token_id, bonus_bet, promotion_id, granular_errors).

status_endpoint:
  DOCUMENTED: GET /v3/orders/  ("Retrieve current orders... include open and recently settled orders.")
              filters: id, state (created|partial|filled|settled), market_id, contract_id, side, sort, pagination_last_id, limit (max 100).
              POST /v3/orders/ description: "For all other order types, the route will return when the order is
              accepted by the exchange. In the latter case, GET v3/orders should be used to check the status of
              the order, using the order id returned by this response."
  MULTIPLES: GET /v3/multiples/{contract_ids}/{u_id}/status/ (full spec only).

lay_side_supported: Y (cross-event multiples) / N (same-event bet builders)
  - Source (product): help-pages/smarkets/en-gb/360011216478_Multiples_on_Smarkets.md lines 42-44 —
    different-event multiples: "Buy/back and sell/lay multiples are allowed."; same-event (Bet builders):
    "Only buy/back multiples are allowed."
  - Source (API): POST /v3/orders/ side enum ["buy","sell"] with description "sell: laying a contract"
    (openapi/smarkets_openapi.json). GET /v3/multiples/{contract_ids}/prices/ and POST /v3/multiples_orders/
    also carry side enum ["buy","sell"] (live_full.json) — but full-spec only.
  - Source (rules): general_rules_1-11.md 9.5 (cross-event) vs 9.6 (same-event) — rule text does not restrict side.

supporting_spec_evidence_for_acca_as_tradeable_market:
  - GET /v3/events/ type_scope enum: ["root","round","category_root","category","single_event","acca_root",
    "acca_category","acca","outright_root","outright_category","outright","tour","antepost_root","antepost_category","antepost"]
  - markets[].contract_selections: "only set for accumulator markets and it refers to the contract IDs that the
    acca is made up of" (example: M3 acca market with M3-C1 Yes / M3-C2 No built from M1-C1 + M2-C1).
  - markets[].market_type.name free string (no enum in trading spec) — e.g. "OVER_UNDER".
```

---

## Q3 — BUILDER-RELATED MARKETS

```
correct_score:          AVAILABLE_VIA_EVENTS_MARKETS (subject to account pre-approved scope)
  - Market type name: CORRECT_SCORE (live_full.json market_types enum; also HALF_TIME_CORRECT_SCORE)
  - Settlement rule: betting-rules/smarkets/12_football.md 12.5.2 "Correct score: This market will be settled
    on the correct score after regular time has expired."
  - Retrieval: GET /v3/events/{event_ids}/markets/ (trading spec) with market_types filter (free string).

winner_BTTS:            AVAILABLE_VIA_EVENTS_MARKETS (subject to account pre-approved scope)
  - Market type name: WINNER_AND_BTTS (live_full.json market_types enum; also FIRST_HALF_WINNER_AND_BTTS)
  - Settlement rule: 12_football.md 12.5.9 "Winner and Both Team to Score: This market will be settled on the
    winner of the match combined with a prediction on whether both teams will score over the course of the
    90 minutes (including stoppage time)."

winner_total_goals:     AVAILABLE_VIA_EVENTS_MARKETS (subject to account pre-approved scope)
  - Market type name: WINNER_AND_OVER (live_full.json market_types enum; also WINNER_2_WAY_AND_OVER)
  - Settlement rule: 12_football.md 12.5.11 "Winner and over 2.5: This market will be settled on the winner of
    the match combined with a prediction on whether the total number of goals over the course of the 90 minutes
    (including stoppage time) will be above or below 2.5."

permission_basis:
  - The 18-path trading spec does NOT enumerate market-type names: 0 occurrences of CORRECT_SCORE,
    WINNER_AND_BTTS, WINNER_AND_OVER, ACCUMULATOR, BET_BUILDER in live_trading.json. market_types query param
    is a free string ("Filter markets by a list of market types separated with `,`").
  - The definitive market_type enum (713 values incl. ACCUMULATOR, BET_BUILDER, BET_BUILDER_PLUS,
    CORRECT_SCORE, BTTS, WINNER_AND_BTTS, WINNER_AND_OVER, BTTS_AND_OVER, EXACT_GOALS) appears only in
    live_full.json (full surface), not the trading spec.
  - Bet-builder eligibility IS exposed in the trading spec: markets[].categories / category enum includes
    "bet_builder" (openapi/smarkets_openapi.json, GET /v3/events/{event_ids}/markets/ 200 schema).
  - Per-account gate: API T&Cs §5 "Usage is restricted to pre-approved events and markets only"
    (scrape-aug18/help/api-tcs.md; api-scope-confirmation.txt §1: "The pre-approved scope is configured
    per-account during the application review... This list isn't published externally").
  - No per-market-type permission flag or endpoint is documented → market access is scope-based, not
    flag-based, and the scope list is not published.

same_event_back_only_position (verbatim rule 9.6.1, ≤30 words):
  "If one or more selections are voided or settled as a dead heat, the whole multiple will be voided with your
  stake returned."
  [24 words — betting-rules/smarkets/general_rules_1-11.md line 184; mirrored in rag-context/betting-rules.md §Rule 9]
  Back-only source: help-pages/smarkets/en-gb/360011216478_Multiples_on_Smarkets.md line 42 —
  same-event Bet builders: "Only buy/back multiples are allowed."
  Related: 9.6.2 horse-racing RF voids full bet; 9.6.3 cash out ceases after in-play.

api_vs_website_difference: NOT DOCUMENTED
  - No Smarkets doc states whether the API can build/place same-event bet builders or dynamic cross-event
    multiples; no API-vs-website equivalence statement for these markets.
  - Only API-side statements found: pre-approved events/markets scope (API T&Cs §5); no test/sandbox
    environment, read-only public endpoints need no auth (api-scope-confirmation.txt).
  - Website-only behaviours documented (help page 360011216478): "With all multiples... Smarkets is the
    counter-party matching the bet. The price of the multiple is formed from the original odds but not an exact
    accumulation. You cannot edit the price of a multiple."; no trade out for multiples; max 10 selections;
    same-event builders not available in-play; eligible sports = football, American football, basketball, tennis.
```

---

## DOC_POINTERS (customer should read)

- Spec (trading surface, 18 paths): https://api.smarkets.com/v0/control/openapi/?tags=trading_api
  → local: `openapi/smarkets_openapi.json`, `scrape-aug18/live_trading.json`
- Full surface incl. multiples/fullcover (tag `otc`): https://api.smarkets.com/v0/control/openapi/
  → local: `scrape-aug18/live_full.json`
- Docs portal: https://docs.smarkets.com/
- Rules: 1-11 General rules (212183509) §9.5 cross-event, §9.6 same-event Bet builders
  → local `betting-rules/smarkets/general_rules_1-11.md` lines 176-188
- Rules: 12 Football rules (210005425) §12.5.2 correct score, §12.5.9 winner+BTTS, §12.5.11 winner+over 2.5
  → local `betting-rules/smarkets/12_football.md` lines 31, 45, 49
- Product: Multiples on Smarkets (360011216478) — buy/sell, back-only builders, 10-selection cap, counterparty, fixed price
- Product: Minimum and maximum stakes (212727285) — £/€0.05 min, £/€99,999.99 max per bet
- API T&Cs (34697834941085) §5 pre-approved events/markets; API Docs & Resources (34720906181021)

## GAPS (→ api@smarkets.com)

1. Are `/v3/multiples*` and `/v3/fullcover*` (tag `otc`) licensed for customer API use? Absent from the trading spec.
2. Are accumulator markets (`type_scope=acca`, `contract_selections`) returned to API accounts and tradeable with `side=sell` (lay)?
3. Per-account pre-approved market list — specifically whether CORRECT_SCORE / WINNER_AND_BTTS / WINNER_AND_OVER are in scope.
4. Max stake per bet/market via API — no endpoint or field; `order.reject.stake_limit_exceeded` exists in the source enum.
5. Can same-event Bet builders (buy-only per help page) be placed via API at all?
6. Executability of acca market prices (website states price cannot be edited; Smarkets is counterparty) — is a resting sell order on an acca contract accepted?
7. Rate limits for multiples/fullcover endpoints (none published in the trading spec).
