# Batch boundary test — quotes 400 IDs + cross-check (2026-10-01)

## Question
Does a 400-market quote batch go through? (Scale test on behalf of API users.)

## Answer
No. `GET /v3/markets/{ids}/quotes/` enforces `maxItems: 200` as a hard boundary.
Over-cap requests return a **route-miss style 404** — not a 400 validation error:

```
status 404  {"data":{"description":"Nothing matches the given URI"},"error_type":"NOT_FOUND"}
```

## Verified results (unauthenticated GETs, live market ids, public routes)

| Call | Status | Bytes | Note |
|---|---|---|---|
| quotes n=200 | 200 OK | 99,938 | full books returned |
| quotes n=400 | 404 | 82 | route-miss body |
| quotes n=201 | 404 | 82 | bisect |
| quotes n=210 | 404 | 82 | bisect |
| quotes n=250 | 404 | 82 | bisect |
| quotes n=300 | 404 | 82 | bisect |
| quotes n=350 | 404 | 82 | bisect |
| volumes n=300 | 200 OK | 20,133 | URL 3,044 chars — works |
| volumes n=301 | 404 | 82 | route-miss body |
| volumes n=310 | 404 | 82 | route-miss body |

## Conclusions
1. Each batch route flips exactly at its documented `maxItems` (quotes 200/201, volumes 300/301).
2. URL length is NOT the constraint (volumes succeeds at 3,044-char URLs while quotes fails at ~2,000) — it is per-route `maxItems` enforcement.
3. The over-cap response is the same 404 shape as a nonexistent path, so support must check ID count before concluding "route does not exist".
4. No `X-RateLimit-*` headers appear on these unauthenticated responses (consistent with limits being account-bound).

## Batch caps (live spec)
quotes 200 · volumes 300 · states 300 · competitors 300 · contracts 100 · last_executed_prices 100 · events-markets 50 · markets_count 50

## Files
- `boundary-quotes-probe.json` — control 200 vs test 400 full captures
- `boundary-bisect.json` — 200/201/210/250/300/350 bisect
- `reproduce.py` — re-runs the boundary checks
