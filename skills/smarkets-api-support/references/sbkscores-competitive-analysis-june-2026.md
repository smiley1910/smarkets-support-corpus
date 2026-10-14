# SBK Scores — Competitive Product Analysis (June 2026)

## What SBK Scores Currently Has (verified by browsing live site)

- Live scores with status (live/FT/upcoming), match clock
- Match events timeline (goals, yellow/red cards, HT, FT with minute markers + scoreline changes)
- Match statistics: attacking (shots, on target, off target, corners, attacks, dangerous attacks), discipline (cards, substitutions), shooting efficiency (on-target vs total ratio)
- Recent form (W/D/L)
- Match info: competition, round, date, kickoff, venue, capacity, duration
- Team pages: form, season stats, next match, home/away record, fixtures, results
- Competition pages: standings/tables, groups, fixtures, results
- D3/SVG visualizations on match pages
- 15+ sports: football, basketball, tennis, cricket, horse racing, greyhound racing, table tennis, snooker, darts, baseball, hockey, volleyball, rugby, MMA, handball
- Dark/light theme toggle
- 11 locales (en-US, en-GB, es-ES, es-MX, pt-BR, de-DE, fr-FR, it-IT, zh-CN, hi-IN, ja-JP)
- Basic PWA (1 icon, standalone display — but NO service worker)
- Settings: theme, language, timezone, locale, odds format (decimal/fractional)
- Day navigation (yesterday/today/tomorrow)
- Filter tabs (All, Live, Finished, Upcoming)
- Team logos (SVG)
- Venue data: stadium name, city, country, capacity, GPS coordinates
- Betting integration with Smarkets exchange (unique differentiator — no competitor has this)

## Critical Gaps (every competitor has all 5, SBK has none)

| Gap | Flashscore | Fotmob | SofaScore | ESPN | 365Scores |
|---|---|---|---|---|---|
| Native mobile app (iOS/Android) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Push notifications | ✅ | ✅ | ✅ | ✅ | ✅ |
| WebSocket real-time updates (<5s) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Favorites/custom alerts | ✅ | ✅ | ✅ | ✅ | ✅ |
| Head-to-head (H2H) records | ✅ | ✅ | ✅ | ✅ | ✅ |

## Tier 1 Priorities (must ship to compete)

1. Native mobile apps (3-6 months) — scores are consumed on mobile, PWA is not enough
2. Push notifications (2-4 weeks) — requires service worker at minimum
3. WebSocket real-time updates (1-2 months) — replace HTTP polling (10s cache window)
4. Favorites system (3-4 weeks) — star teams/leagues, custom alerts
5. H2H records (1-2 weeks) — standard on every competitor

## Tier 2 Differentiators

6. xG (expected goals) — requires data licensing (Opta/StatsBomb)
7. Player ratings per match — SofaScore's signature feature
8. Match momentum graph — SBK already uses D3, 1-2 weeks
9. Match preview page — auto-generated form/H2H/stats before kickoff
10. Multi-bookmaker odds comparison — currently Smarkets only
11. UI redesign — match page layout needs to match Fotmob's standard
12. Live text commentary — play-by-play text feed

## Known Bugs (found during testing)

- Team page sidebar: "Failed to load competitions" error
- URL locale mismatch: US locale uses "soccer" in URLs but API uses "football" → 404s
- No service worker — PWA manifest exists but push notifications cannot work
- 10-second cache on live data — competitors use WebSocket

## What SBK Scores Does Well (don't lose these)

- Betting integration with Smarkets exchange (unique differentiator)
- Sport breadth (15 sports including niche)
- D3 visualizations already in stack
- Venue data (GPS coordinates, capacity)
- Shooting efficiency ratio (some competitors don't show this)

## Architecture (confirmed June 2026)

- Frontend: Next.js (App Router) with OpenNext (serverless) behind Cloudflare
- API: Next.js API route handlers proxying to api.smarkets.com
- No WebSocket, no Rust backend
- Cache: s-maxage=10, stale-while-revalidate=50
- Direct api.smarkets.com is faster than the sbkscores proxy (140ms vs 175ms cached, 340ms vs 832ms uncached)

Full detailed report at `~/smarkets-audit/sbkscores-competitive-analysis.md`
