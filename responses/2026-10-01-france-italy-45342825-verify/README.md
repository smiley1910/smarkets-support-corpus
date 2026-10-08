# Verification — France vs Italy (event 45342825) API support draft

Date: 2026-10-01 ~22:16 local. Read-only, unauthenticated GETs (structure and IDs
unaffected; spec notes prices are delayed without a session token — customer has auth).

Question: does every factual claim in the drafted reply hold — endpoint paths,
market existence, price/quantity formulas, REST v3 sufficiency, no hallucinated endpoints?

## Claim-by-claim results

| # | Draft claim | Live / spec evidence | Verdict |
|---|-------------|----------------------|---------|
| 1 | France vs Italy = event 45342825 | event name "France vs Italy", state upcoming, KO 2026-10-02T18:45:00Z | PASS |
| 2 | "currently shows 165 open markets" | GET /v3/events/45342825/markets/ → 165 markets, states = {open: 165} | PASS |
| 3 | France O/U 0.5–3.5 goals exist | 166809839, 840, 841, 842 = "France over/under 0.5–3.5 goals", all open | PASS |
| 4 | Italy O/U 0.5–3.5 goals exist | 166809849, 850, 851, 852 = "Italy over/under 0.5–3.5 goals", all open | PASS |
| 5 | Both-halves markets exist (score + win, both teams) | 166809916 France to score in both halves; 166809926 Italy to score in both halves; 166809918 France to win both halves; 166809928 Italy to win both halves — all open | PASS |
| 6 | GET /v3/events/{event_id}/markets/ | spec path /v3/events/{event_ids}/markets/; concrete call 45342825 → HTTP 200 | PASS (placeholder note) |
| 7 | GET /v3/markets/{market_id}/contracts/ | spec path /v3/markets/{market_ids}/contracts/; 166809918 → HTTP 200, Yes 460736180 / No 460736181 | PASS |
| 8 | GET /v3/markets/{market_id}/quotes/ | spec path /v3/markets/{market_ids}/quotes/; 166809918 → HTTP 200, populated book | PASS |
| 9 | Each market has id, name, state | live market objects carry id / name / state (plus slug, category, ...) | PASS |
| 10 | Quotes "grouped by contract id with bids and offers" | response = {"460736180": {"bids": [...], "offers": [...]}, "460736181": {...}} | PASS |
| 11 | Bids = back orders resting; offers = lay orders | workspace-verified mapping; sort order + uncrossed assert hold in all 4 contract books | PASS |
| 12 | Price basis points /10000; decimal = 10000/price | spec: "percentage basis points ... divide 10000 by it. 10000 / 5000 = 2.0" | PASS |
| 13 | Quantity 1/10000 currency; GBP = quantity/10000 | spec: "units are 1/100 of a UK penny ... Quantity 500 = 0.05 GBP" | PASS |
| 14 | "No separate feed; REST v3 covers both steps" | API is REST only (no streaming for API customers); both steps served by the verified endpoints | PASS |

## Sample live quotes (market 166809918, contract Yes 460736180)
bids: [{price: 2381, quantity: 4199916}, {price: 2273, quantity: 7919049}]
offers: [{price: 3175, quantity: 1465201}, {price: 3226, quantity: 2657218}]
max(bid price) 2381 < min(offer price) 3175 → uncrossed book, mapping consistent.

## Precision notes (non-blocking, not errors)
- Spec-exact templates use plural placeholders ({event_ids}, {market_ids}) — these routes
  accept comma-separated batch ids. The draft's singular placeholders are idiomatic for a
  single id; the concrete calls used are exact and live-verified.
- "You do not need a separate feed" is true and consistent with the verified fact (API is
  REST only, no streaming). Optionally sharper: state explicitly that there is no streaming feed.
- "the current book" — quotes return the exchange order book; per house style avoid implying
  all website liquidity is shown.

## Files
- reproduce.py — reruns all checks (expects same-day data).
- event_45342825.json, markets_45342825.json, contracts_166809918.json,
  quotes_166809918.json, quotes_166809839.json, openapi_trading_api.json — raw captures.
