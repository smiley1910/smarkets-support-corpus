# Smarkets Product Ecosystem Security Audit — July 2026 (Re-audit)

> **Date:** 2026-07-11
> **Method:** 3-pass passive audit — (1) headers/API/DNS baseline, (2) JS bundle + endpoint deep-dive, (3) logic/edge-case testing
> **Scope:** sbkscores.com, api.smarkets.com, betsbk.com, betsbk-staging.com, oddsindex.com
> **Previous audit:** June 2026 (see `sbkscores-security-audit-june-2026.md`)
> **Full report:** `~/smarkets-audit/audit-july-2026.md`
> **Patches:** `~/smarkets-audit/patches/` (13 files + REMEDIATION_GUIDE.md)
> **Total requests:** ~80 across all targets

## What Changed Since June 2026

### Partially fixed:
- Health endpoint no longer leaks `version: "1.0.0"` and `external_api.responseTime` (partially cleaned up — still leaks `service: "sbkscores-site"` and `uptime: 0`)
- betsbk-staging.com now returns 503 instead of 200 (backend scaled down, but domain still publicly accessible — NOT access-controlled)

### Got WORSE:
- sbkscores.com API now leaks MORE exchange-internal fields: 32 fields per match (was ~20 in June). New fields: `clock`, `periods`, `periodScores`, `scores`, `quarters`, `round`, `stats`, `additional`, `hasLeagueTable`
- API response grew to 603KB (319 matches × 32 fields)

### Still NOT fixed (same as June):
- betsbk.com (production): zero security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy all missing)
- oddsindex.com CSP: still leaks localhost:8080/8081/3001, oi-api.smarkets.work (172.16.1.2), silverstripe.smarkets.tech (10.2.x.x), wss://betsbk-staging.com, 'unsafe-eval'
- Exchange metadata: still leaking via sbkscores API and api.smarkets.com states endpoint
- DevSwrDebug: still in production JS (chunk hash changed from `layout-5d9fd58bda2bbc0d.js` to `layout-338e59ebad278b87.js` but code is identical — byte 53846)
- Geo/stack headers: still leaking (x-user-country: MT, x-locale, etc.)
- Rate limiting: still inconsistent

## API Parameter Format Changes (IMPORTANT for support tickets)

The api.smarkets.com event type parameter format changed since June:

| Parameter | June 2026 (old) | July 2026 (current) |
|---|---|---|
| `type` | `football` | `football_match` |
| `state` | `inplay` | `live` |

Old values now return 400 `REQUEST_VALIDATION_ERROR`. The error message also leaks the complete enum of valid values (see Finding 9 below).

**Impact on support:** Customers referencing old parameter formats in tickets may be confused. The migration is silent — no deprecation notice, just a 400 error.

## New Findings (6 — not in June audit)

### Finding 9: api.smarkets.com error messages leak complete event type enum — Medium (NEW)

Sending an invalid `type` parameter returns a 400 error listing ALL 47 valid event types:
- All sports: football_match, baseball_match, basketball_match, cricket_match, darts_match, golf_match, greyhound_racing_race, horse_racing_race, ice_hockey_match, mma_match, snooker_match, table_tennis_match, tennis_match, volleyball_match, rugby_league_match, rugby_union_match, handball_match, american_football_match
- All esports: csgo_match, dota_2_match, league_of_legends_match, call_of_duty_match, football_esports_match, basketball_esports_match
- Special: politics, politics_outright, current_affairs, tv_entertainment, cycling, rowing, sailing_race, sailing_outright
- Structural: generic, top_level_event, all *_outright variants

Also, `state` validation leaks: `['new', 'upcoming', 'live', 'ended', 'settled', 'cancelled', 'suspended']`

This is a complete market coverage map handed to anyone who sends a bad request. Patch 09 sanitizes these to generic "Invalid value for parameter" messages.

**Verified:** `curl -s "https://api.smarkets.com/v3/events/?type=INVALID"` — returns full enum.

### Finding 10: date=9999-12-31 causes backend 503 — Low (NEW)

`date=9999-12-31` on sbkscores.com API returns 503 "Failed to fetch matches" instead of clean 400 rejection. Missing date range validation. Normal future dates (2027-01-01) return 200 with empty matches. Only extreme dates cause the error.

**Verified:** `curl -s "https://sbkscores.com/api/v3/sports/football/matches?date=9999-12-31"`

### Finding 11: sbkscores.com page CSP leaks self-hosted Sentry — Low (NEW)

Page CSP `connect-src` includes `https://sentry.smarkets.com`, revealing a self-hosted Sentry error tracking instance. Not in the June audit's CSP analysis.

### Finding 12: x-cache-key leaks build hash and git commit prefix — Low (NEW)

`x-cache-key: matches:20260708-091221-391f770b60e:football:2026-07-11:all:UTC` reveals:
- Build date: July 8, 2026 at 09:12:21
- Git commit prefix: 391f770b60e
- Cache key format and structure

Additional cache-internal headers now visible: `x-transform-dropped`, `x-cache-live`, `x-cache-swr-base`, `x-cache-ttl-base`.

### Finding 13: 603KB API response (excessive data) — Informational (NEW)

319 matches × 32 fields = 603KB per response. Stripping exchange-internal fields (Patch 04) would reduce to ~350KB (42% reduction). Performance and bandwidth issue as much as security.

### Finding 14: cachedAt timestamp leaked — Informational (NEW)

Top-level response includes `cachedAt: "2026-07-11T15:23:14.444Z"`, revealing exact cache timestamp. Combined with x-fetch-time, reveals the full cache lifecycle.

## Verified NOT Vulnerable (Good)

- No admin/debug/internal API endpoints exposed (all return 404)
- No path traversal vulnerability (returns 404)
- No SQL injection (rejected with 400)
- No CORS reflection (static origin: `https://sbkscores.com`, correct)
- No cache poisoning via X-Forwarded-Host/Proto (cache key is sport+date+timezone only)
- No IDOR on match endpoints (404)
- HTTP method tampering blocked (405 for POST/PUT/DELETE)
- No secrets/tokens in JS bundles
- No API keys in HTML
- Parameter pollution rejected (400 for duplicate date params)
- Cricket endpoint works (not an error — cricket is a valid sport)

## DevSwrDebug Persistence Note

The DevSwrDebug dead code has persisted across a rebuild. The chunk hash changed (`5d9fd58bda2bbc0d` → `338e59ebad278b87`) but the code is identical (same no-op stub at a similar byte offset). This means **rebuilding alone does not remove dead code — the source must be modified** to remove the DevSwrDebug import/component. See Patch 08 for the source-level fix.

## Patch Summary

All 13 patches in `~/smarkets-audit/patches/`:

| Patch | Finding | Applies To | Effort |
|---|---|---|---|
| 01 | betsbk.com missing headers | Cloudflare Transform Rules | 4h |
| 02 | oddsindex CSP leaks | Next.js config | 1h |
| 03 | Staging public access | Cloudflare Access | 1h |
| 04 | Exchange fields in scores API | API route handler | 4h |
| 05 | BetGenius metadata in states | API middleware | 2h |
| 06 | Geo/stack headers | Cloudflare Transform Rules | 1h |
| 07 | Rate limiting | Cloudflare WAF / Next.js | 1h |
| 08 | DevSwrDebug dead code | Build config / source | 30min |
| 09 | Event type enum leak | API error handler | 1h |
| 10 | Date validation | API route handler | 30min |
| 11 | Sentry in CSP | Next.js config | 30min |
| 12 | x-cache-key leak | Cloudflare Transform Rules | 30min |
| 14 | cachedAt leak | API route handler | 15min |

**P0 (this week): ~6h** | **P1 (this sprint): ~8h** | **P2 (this quarter): ~4h** | **Total: ~18h**
