# Smarkets Product Ecosystem Security Audit — June 2026

> **Date:** 2026-06-26
> **Method:** Passive verification only — curl headers, DNS lookups, public API responses, JS bundle inspection
> **Scope:** sbkscores.com, api.smarkets.com, betsbk.com, betsbk-staging.com, oddsindex.com
> **Full report:** `~/smarkets-audit/red-team-report.md` (438 lines)
> **Test script:** `~/smarkets-api-support/scripts/noauth_live_football.py`

## Architecture Map (Verified)

### Public-Facing Domains (all behind Cloudflare)

| Domain | Cloudflare IPs | Tech | Purpose |
|---|---|---|---|
| sbkscores.com | 172.67.173.111, 104.21.55.216 | Next.js / OpenNext serverless | Sports scores |
| api.smarkets.com | 104.17.176.12, 104.17.97.49 | Exchange API | Betting exchange backend |
| betsbk.com | 104.18.17.8, 104.18.16.8 | Next.js | Betting product (prod) |
| betsbk-staging.com | 104.18.7.225, 104.18.6.225 | Next.js | Betting product (staging) |
| oddsindex.com | 172.67.180.154, 104.21.51.127 | Next.js | Odds comparison |

### Internal Services (leaked via DNS/CSP)

| Hostname | Resolves To | Purpose |
|---|---|---|
| oi-api.smarkets.work | **172.16.1.2** (RFC 1918) | OddsIndex API (HTTP!) |
| silverstripe.smarkets.tech | CNAME → silverstripe.k8s.smarkets.com → **10.2.24.240, 10.2.225.255** | Silverstripe CMS on K8s |
| sentry.smarkets.com | (referenced in CSP) | Self-hosted Sentry |
| api.oddsindex.com | (referenced in CSP) | OddsIndex API (public) |
| *.k8s.smarkets.com | 10.2.x.x (private) | Kubernetes internal DNS |

### Tech Stack

Next.js (all products) · OpenNext (serverless) · Cloudflare (edge) · AWS (origin, via x-amzn-trace-id) · Kubernetes (k8s.smarkets.com) · Silverstripe CMS · Sentry (self-hosted + cloud) · Google Analytics/TagManager · BetGenius (live sports data feed)

### Data Flow

```
sbkscores.com → proxies to api.smarkets.com (shared event IDs)
betsbk.com/staging → x-middleware-rewrite: /en_MGA_mt_/ (MGA locale)
oddsindex.com → oi-api.smarkets.work (HTTP, 172.16.1.2)
              → silverstripe.smarkets.tech (K8s, 10.2.x.x)
              → wss://betsbk.com + wss://betsbk-staging.com
api.smarkets.com → public, no auth (events, markets, contracts, quotes, states)
```

## Security Header Matrix

| Header | sbkscores (page) | sbkscores (API) | betsbk.com | betsbk-staging | oddsindex |
|---|---|---|---|---|---|
| CSP | ✅ | ❌ | ❌ | ❌ | ✅ |
| HSTS | ✅ | ❌ | ❌ | ❌ | ✅ |
| X-Frame-Options | ✅ DENY | ✅ DENY | ❌ | ❌ | ✅ DENY |
| X-Content-Type-Options | ✅ | ✅ | ❌ | ❌ | ✅ |
| Referrer-Policy | ✅ | ✅ | ❌ | ❌ | ✅ |
| Permissions-Policy | ✅ | ❌ | ❌ | ❌ | ✅ |

## Verified Findings

### Issue 1: Exchange metadata leaked via sbkscores.com API — Low-Medium

sbkscores.com `/api/v3/sports/*/matches` returns exchange-internal fields: `bet_allowed`, `bettable`, `inplay_enabled`, `parent_id`, `hasLiveStream`, `competition.priority`, `actual_start_datetime` (ms precision). `coverage_delay: 8` nested at `info.coverage_delay` for inplay matches only.

**Fix:** Field-level filtering in sbkscores API gateway — strip exchange-internal fields from scores API response.

### Issue 2: Shared event IDs — Informational (not a vulnerability)

sbkscores.com match IDs are identical to api.smarkets.com event IDs. Deliberate architecture for scores-to-betting deep-linking. Not a security finding.

### Issue 3: Inconsistent rate limiting — Low

sbkscores health endpoint has rate limiting (`x-ratelimit-limit: 10`), matches API does not surface rate limit headers but is cached (`s-maxage=10`). CORS restricts to sbkscores.com origin (standard). "No rate limiting" claim was partially overstated.

### Issue 4: betsbk-staging.com publicly accessible — Medium (AND production betsbk.com also lacks headers)

Staging returns HTTP 200 on root and `/login/`. Zero security headers. `x-middleware-rewrite: /en_MGA_mt_/` confirms MGA locale. Client-side React 404 is cosmetic — server serves full 341KB app bundle including JS chunks, CSS, Smarks branding, MGA compliance text.

**NEW:** betsbk.com (PRODUCTION) also lacks ALL security headers. Systemic, not staging-specific.

**Fix:** Cloudflare Access in front of staging domain. Add CSP/HSTS/X-Frame-Options to both staging and production.

### Issue 5: Internal infrastructure leaked via oddsindex.com CSP — Medium-High (most significant)

CSP `connect-src` leaks complete internal map:
- `http://oi-api.smarkets.work` → 172.16.1.2 (private, HTTP!)
- `https://silverstripe.smarkets.tech` → 10.2.x.x (private, K8s)
- `wss://betsbk-staging.com` (staging in production CSP!)
- `http://localhost:8080, 8081, 3001` (dev ports in prod)
- CSP also has `'unsafe-eval'` in script-src

**Fix:** Remove localhost, staging domains, and private-IP hostnames from production CSP. Remove `unsafe-eval`. Use production-specific API endpoints.

### Issue 6: DevSwrDebug in production JS — Informational (dead code)

Found at byte 53426 in `layout-5d9fd58bda2bbc0d.js`. Component is a **no-op stub** — empty `useEffect(() => {}, [e, t])`, returns `null`. Does NOT reveal API structure (original audit claim was false). Dead code, 5-minute fix.

### Issue 7: Stack/location disclosure — Low-Medium

Headers: `x-powered-by: Next.js`, `x-opennext: 1`, `x-user-country: MT`, `x-locale`, `x-user-language`, `x-user-region`, `x-user-has-preference`. Health endpoint leaks: `service: "sbkscores-site"`, `version: "1.0.0"`, `uptime: 0`, `external_api.responseTime: 71`. Also: `x-cache-key` and `x-fetch-time` headers on API responses.

**Fix:** Remove custom x-user-* headers. Restrict health endpoint to internal IPs. Strip x-cache-key and x-fetch-time.

## Methodology Lesson

When auditing from the public API only:
- State explicitly: "This was verified via public (no-auth) API access"
- Distinguish: what the field IS (verified) vs what it MEANS (inferred)
- If two interpretations are possible, state the one test that resolves it
- Never present either interpretation as confirmed fact without that test
- The `coverage_delay` field interpretation (public delay vs inherent feed latency) was contradictory across two assessments because both used the same unauthenticated access — an authenticated comparison was never performed
