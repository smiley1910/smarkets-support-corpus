# Smarkets OpenAPI / API Docs — Change Log

Dated scrape + diff record. Live source: `https://api.smarkets.com/v0/control/openapi/?tags=trading_api`
(structurally identical to `/v0/control/openapi/` full, which exposes 360 paths incl. web/app endpoints).
Baseline refreshed copies: `smarkets_openapi.json` (workspace root) and `openapi/smarkets_openapi.json`.

Build revision (control/version): `ac919ea7a59fe6c0b3abead3188ac749485feffc` (scraped 2026-08-18).

## 2026-08-18 — vs May-19 and Jun-24 baselines
**Surface: NO structural change.** Trading API still 18 paths, 3 schemas, server `api.smarkets.com`.
All 18 endpoints and their methods unchanged. Per-endpoint rate limits unchanged:
  - GET /v3/markets/{ids}/quotes/ — max 50 / 60s
  - POST /v3/orders/ — max 10 / sec
  - DELETE /v3/orders/{id}/ — max 10 / sec
  - DELETE /v3/sessions/ — max 30 / 60s
  - POST /v3/sessions/ — max 5 / 300s
  - Global default: 1200 / 60s; X-RateLimit-Limit/Remaining/Reset headers (now stated inline in spec info block).

**Genuine new enum values (present live, absent in both baselines; nothing removed):**
1. `contract.unvoid` — new account-activity / event `source` value (alongside `contract.void`, `contract.unreduce`).
   Relevant to unvoid / void-reversal credit-request tickets. /v3/accounts/activity/.
2. `IRGC` — new value in the `jurisdiction` query-param enums on events / markets / contracts endpoints.
   (Alongside IGC, MGA, etc.) Flag: confirm what regulator/country it maps to if a customer references it.
3. `SBK_PRICER_UNAVAILABLE` — new error_type on the `/v3/markets/{ids}/quotes/` 503 response.
4. `LOGIN_VERIFICATION_REQUIRED` — new error_type (403) on `POST /v3/sessions/`, `DELETE /v3/sessions/`, `POST /v3/sessions/verify/`.
   → Added to `references/login-error-ticket-patterns.md` 403 table + error-code list.

**Notes:** enum ordering differs between snapshots (EVENTS_* error list reorder, BAD_REQUEST vs
REQUEST_VALIDATION_ERROR, `IRGC` position) — these are cosmetic reordering, not semantic, except the genuinely
new values above. Timestamp `example` fields are generated at serve time (rotating `now`) — ignore in diffs.

No endpoints added/removed, no rate-limit changes, no request/response schema shape changes on the 18 trading paths.

## 2026-08-18 — Customer-facing (help-centre) API policy — NO CHANGE
Re-fetched both API articles via Jina reader and diffed against the July capture (`references/api-tcs-full-text.md`).

1. **Smarkets API: Access, Integration & T&Cs** (article 34697834941085) — identical. All 8 sections, £150 admin fee,
   60-day refund, pre-approved events/markets restriction, benchmarking ban, §7 grounds (Data Harvesting / Fee
   Avoidance / Unfair Trading incl. latency arbitrage & court-siding), affiliate + 0%-commission ineligibility
   note, deposit-deduction activation, support@smarkets.com. No changes to rate-limit wording (policy does not
   state the 1200/min figure — that's spec-only).
2. **Smarkets API Documentation & Resources** (article 34720906181021) — identical: onboarding link, request form,
   docs.smarkets.com reference, Market Data / Order Management / Account Management sections.

**Artifacts to ignore:** Jina's reader occasionally injects a stray hidden link `smarkets.com.by` after the
`[smarkets.com](https://smarkets.com/)` link in §6.1 — that's a Jina HTML-parsing artifact, NOT real policy
content. Do not cite it.

Conclusion: customers see the same API policy wording as of Aug 2026. The only API-facing additions are the 4 new
OpenAPI enum values (recorded above) — none of which appear on the customer-facing policy articles.

## 2026-09-27 — lightweight spec refresh
Snapshot: `openapi/smarkets_openapi_2026-09-27.json` (195878 bytes, md5 1955158236070a8ef34cc56ceeb53280). Older copies left in place.
Surface: still 18 trading paths. Session TTL text, login cap, order caps, and throttle/auth enums unchanged.
Changes vs the 2026-09-16 copy (`openapi/smarkets_spec.json`):
1. GET /v3/events/ rate cap: Maximum 1200 requests per 60 seconds → Maximum 600 requests per 60 seconds. Matches the 2026-09-23 live check already in `references/rate-limits.md`. The Aug 18 copy has no events cap at all, so both older JSONs are stale on this one line.
2. POST /v3/orders/ description gained one internal sentence (Do not call _check_bet_permissions() here as it will be checked in Exchange). Not customer relevant.
Help centre rescrape skipped: no signal of policy change and nothing in the open ticket quotes those articles.