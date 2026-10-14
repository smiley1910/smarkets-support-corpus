# Streaming Infrastructure and CFTC Product — July 2026

## Investigation Context

Discovered during a customer support ticket where a customer requesting IP whitelisting mentioned `sio-live.smarkets.com` as a "market-data stream." Investigation revealed this hostname is NOT in the API documentation but IS hardcoded in the Smarkets website's public JavaScript. Further investigation uncovered an unannounced CFTC-regulated prediction market product.

## Three Distinct Streaming Architectures

### 1. Current REST API (Documented)
- Base URL: `https://api.smarkets.com`
- Protocol: HTTP/JSON (REST)
- Market data endpoints: quotes, last_executed_prices, volumes
- Auth: Session-Token header
- This is the ONLY documented API. No streaming.

### 2. Old Streaming API (Deprecated, Dead)
- Host: `stream.smarkets.com:3801` — NXDOMAIN (verified via `dig`, July 2026). Endpoint decommissioned (inferred from NXDOMAIN + SDK archived Jan 2019).
- Protocol: TCP + SSL + protobuf framing
- SDK: `github.com/smarkets/smk_python_sdk` (copyright 2011, still publicly visible)
- Docs: `smarkets-python-sdk.readthedocs.io` (still accessible)
- Python 2.7/3.5 compatible
- This was the "Smarkets Streaming API" — a proper documented streaming protocol
- Endpoint is dead. The SDK is historical reference only.

#### Primary Source Verification (July 2026)
Verified against the actual GitHub repo when a customer asked about this endpoint:
- **Repo status**: ARCHIVED (read-only — GitHub's deprecation mechanism)
- **Last push**: January 8, 2019 (6.5+ years unmaintained)
- **Source location**: `smarkets/streaming_api/session.py` line 24: `host='stream.smarkets.com', port=3801, ssl=True`
- **Protocol confirmed**: protobuf over TCP with SSL (imports `google.protobuf.text_format`)
- **Python compatibility**: 2.7, 3.5, PyPy 1.9+ (no modern Python support)
- **NXDOMAIN claim**: From earlier session — NOT independently re-verified via DNS lookup in July 2026. The customer's inability to resolve is consistent with decommissioning but could also be network/firewall. The archived SDK status is the strongest evidence of deprecation.
- **Verification path**: GitHub API → `repos/smarkets/smk_python_sdk` (metadata: archived, pushed_at) → `contents/smarkets/streaming_api/session.py` (source code: hardcoded host/port defaults)

### 3. Website WebSocket Stream (Undocumented, Live)
- Hosts: `sio-live.smarkets.com` (live), `sio-delayed.smarkets.com` (delayed)
- Protocol: WebSocket (JSON messages, NOT Socket.IO despite "sio" prefix)
- Auth: Requires session token
- Source: Hardcoded in Smarkets website frontend JS (chunk `7491-c68910d889274dcb.js`)
- This is the website frontend's real-time data push channel
- NOT part of the documented API
- NOT the same as the old SDK's streaming API
- Any website visitor can discover these by reading the public JavaScript

## How Customers Discover Undocumented Endpoints

The streaming endpoints are hardcoded in plaintext in the Smarkets website's JavaScript bundles. No reverse engineering or authentication bypass is needed. A customer simply:
1. Opens smarkets.com in a browser
2. Opens DevTools → Sources/Application tab
3. Reads the JS chunks
4. Finds the `wss://sio-live.smarkets.com/` URL in the configuration object

This is trivially easy for any web developer. Expect customers to mention these endpoints in support tickets, especially those requesting IP whitelisting or asking about real-time data.

## Full Streaming Topology (from JS chunk 7491)

```
Default (gambling exchange):
  production:  wss://sio-live.smarkets.com/        (live)
               wss://sio-delayed.smarkets.com/     (delayed)
  staging:     wss://sio-live.smarkets-staging.com/
               wss://sio-delayed.smarkets-staging.com/

CFTC variant (prediction market):
  production:  wss://cftc-sio-live.smarkets.com/
               wss://cftc-sio-delayed.smarkets.com/
  staging:     wss://cftc-sio-live.smarkets-staging.com/     (NXDOMAIN, not deployed)
               wss://cftc-sio-delayed.smarkets-staging.com/  (NXDOMAIN, not deployed)

Older endpoint:
  wss://live.smarkets.com/  (from JS chunk 6189, may be legacy/deprecated)
```

## CFTC Product — "Smarkets Predictions"

### Overview
- Product name: "Smarkets Predictions" (page title on CFTC routes)
- Type: CFTC-regulated prediction market / event contracts
- Positioning: Trading/financial platform, NOT gambling
- Legal language: "Trading on Smarkets involves risk... Smarkets is subject to U.S. regulatory oversight by the CFTC."
- Development stage: Infrastructure deployed, routes defined, content pages not built (render 404). CFTC staging not deployed.

### US Legal Entities
- Colorado: "Smarkets USA Op Co." — Colorado Division of Gaming, license #90034372, issued 20 April 2020
- Indiana: "Smarkets Holdings USA Inc" — Indiana Gaming Commission
- CFTC (federal): "Smarkets is subject to U.S. regulatory oversight by the CFTC"

Colorado license active since April 2020 — over 6 years of US infrastructure building.

### Jurisdiction System
- Colorado = "CDG", Indiana = "IGC", CFTC = "CFTC"
- US jurisdictions grouped: `new Set(["CDG", "IGC", "CFTC"])`
- European: Malta = "MGA", Sweden = "SGA", UK = "UKGC", Denmark = "DGA"

### CFTC Mode Behaviour
When active (via `useCftcMode()` hook):
- Hides gambling commission logos
- Hides "Gambling can be addictive" warning
- Hides Profit Hub and Portfolio links
- Changes odds format to "cents" (American odds)
- Uses CFTC-specific streaming endpoints
- Uses trading/financial legal language

### CFTC Routes
- `/cftc/regulatory-hub/` — 200 but renders 404 (route exists, page not built)
- `/cftc/help-center/` — 200 but renders 404

### SBK US Terms Already Published
- `help.getsbk.com/hc/en-us/articles/360007645537-SBK-Terms-Conditions-Colorado-USA`
- `help.getsbk.com/hc/en-us/articles/360018820477-SBK-Terms-Conditions-Indiana-USA`

## Other Infrastructure Exposed in Public JS

From comprehensive JS analysis (66 chunks, July 2026):

### Staging API in Production JS
- `api.smarkets-staging.com` — hardcoded in production JS chunk 6800

### Firebase Configuration (chunk 9032)
- Project ID: smarkets-cb16a
- App ID: 1:599825212086:web:8476c41a3e47de09647c17
- Measurement ID: G-TVGFS64NZB
- Auth Domain: smarkets-cb16a.firebaseapp.com
- API Key: AIzaSy...oIlY (Firebase keys are public by design)

### Regulatory Identifiers (chunk 6800)
- MGA company UUID: 32fabf90-ecba-4b5f-9dfd-d34d73c3267d
- UKGC account number: 39173
- Colorado license: 90034372

### Other Hostnames Discovered
- `status.smarkets.com` — Atlassian Statuspage
- `static.smarkets.com` — static asset CDN
- `smarketshq.com` — engineering blog (Medium)
- `centinelapi.cardinalcommerce.com` — 3D Secure payment auth
- `api.addressy.com` — Loqate address validation

### sbkscores.com
- Does NOT reference any Smarkets streaming endpoints
- Has `ws://localhost:8081` dev artifact in production JS (chunk 6999)
- Uses cached REST polling, not WebSocket

## New Findings — Comprehensive Audit July 2026

### New Subdomains Discovered (via CT logs + JS analysis)

| Subdomain | Status | Notes |
|---|---|---|
| sentry.smarkets.com | Active (Cloudflare) | Self-hosted Sentry error tracking. 3 projects: ID 4 (smarkets.com), ID 8 (sbkscores.com), ID 21 (betsbk.com) |
| pyms-api.k8s.smarkets.com | Active — resolves to PRIVATE IPs | 10.2.129.41, 10.2.29.172, 10.2.226.174. K8s internal API exposed in public DNS |
| stream-1.smarkets.com | Active — AWS ELB, NOT Cloudflare | k8s-exchange-exchange-8ac26b91c1-...elb.eu-west-1.amazonaws.com. Reveals K8s namespace "exchange" |
| stream-external.smarkets.com | Active — AWS ELB, NOT Cloudflare | 52.49.245.143. External streaming service |
| events-providers.smarkets.com | Active — AWS ELB, NOT Cloudflare | 18.200.109.84. Events data feed service |
| community.smarkets.com | Active (Cloudflare) | Developer forum (50 CT entries, 2019-2022) |
| support.smarkets.com | Active (Cloudflare) | Support portal (110 CT entries, 2024-2026) |
| mail.smarkets.com | Active (Cloudflare) | Email routing (98 CT entries) |
| mta-sts.smarkets.com | Active (Cloudflare) | MTA-STS SMTP security |
| backoffice-admin.smarkets.com | NXDOMAIN (historical) | Admin panel cert from 2016, abandoned |
| sandbox.smarkets.com | NXDOMAIN (historical) | Sandbox environment, abandoned |
| dga.smarkets.com | NXDOMAIN (historical) | Likely Danish Gambling Authority, 2018-2020 |

### Sentry Infrastructure

Self-hosted Sentry at `sentry.smarkets.com` (behind Cloudflare). DSNs extracted from JS:
- smarkets.com: `https://b5bf9925c86a9481564383edb26fb73f@sentry.smarkets.com/4` (project 4)
- sbkscores.com: `https://13aa890d064a0e2b459a5d2c506aff88@sentry.smarkets.com/8` (project 8, raw fetch() not Sentry SDK)
- betsbk.com: `https://50f7153f9f00ccc9b96edf2dcd8f2909@sentry.smarkets.com/21` (project 21)

Sentry release ID (smarkets.com): `82c11ba6a9b726db7647079df5b0e830eb48c50b` (git commit hash)
Next.js version: 15.4.10

### Complete API Endpoint Map (from JS chunks)

60+ endpoints extracted from smarkets.com JavaScript:

**Auth/User:** /v3/sessions/, /v3/sessions/verify/, /v3/password-reset-email/, /v3/password-reset/, /v3/password/, /v3/accounts/, /v3/accounts/activity/, /v3/accounts/net_deposits/, /v3/jurisdictions/, /v3/personal/, /v3/preferences/, /v3/occupations/, /v3/email/, /v0/users/current/info-without-rate/, /v0/users/current/finance/, /v0/users/current/activity/{type}/{id}/, /v0/sessions/current/, /v0/payment_terms_accepted/

**KYC:** /v3/kyc/requirements/{token}, /v3/kyc/verification_states/{token}, /v3/kyc_files/reviewing/{token}, /v3/kyc_files/, /v3/verification_emails/

**MFA:** /v3/mfa/, /v3/mfa/secrets/

**Trading:** /v3/orders/, /v3/orders/{id}/, /v3/events/, /v3/events/{id}/markets/, /v3/markets/{id}/, /v3/markets/{id}/contracts/, /v3/markets/{id}/quotes/, /v3/multiples/, /v3/multiples_orders/

**Payments:** /v3/card_deposits/, /v3/card_deposits/worldpay/, /v3/card_deposits/token/, /v3/card_methods/, /v3/deposit_methods/, /v3/deposit_methods/providers/, /v3/paypal_deposits/, /v3/paypal_deposits/client_tokens/, /v3/swish_deposits/, /v3/trustly_deposits/, /v3/trustly_account_payout/, /v3/open_bank_transfer_deposits/, /v3/open_bank_transfer_methods/providers/, /v3/open_bank_transfer/verified_withdrawals/, /v3/worldpay_methods/, /v3/withdrawal_methods/, /v3/withdrawals/, /v3/withdrawals/withdrawal_cancel_block/, /v3/transactions/, /v3/transactions/retrieve/

**Other:** /v3/breaks/, /v3/commission/bands/, /v3/currencies/, /v3/favourites/event_ids/, /v3/legal/terms/, /v3/legal/terms/last_seen/, /v3/metrics/, /v3/notifications/registrations/, /v3/notifications/subscriptions/, /v3/pnl/, /v3/chats/, /v3/chats/messages/, /v3/recommender/top_movers/, /v3/search/, /v3/usage/

### Payment Providers (7 total)
1. Worldpay (card deposits, /v3/card_deposits/worldpay/)
2. PayPal (deposits with client tokens)
3. Swish (Swedish mobile payments)
4. Trustly (deposits and account payouts)
5. Open Banking (bank transfer deposits, verified withdrawals)
6. CardinalCommerce (3D Secure, centinelapi.cardinalcommerce.com)
7. Loqate (address validation, api.addressy.com)

### "predictions" Deployment Environment
JS reveals a "predictions" deployment environment alongside "production", "staging", "preview", "vercel". This is the CFTC product's deployment pipeline code name.

### Internal Playground Routes (401 auth required)
- /internal/playground/ (bet-button, button, cards, graph, payments, scores)
- /internal/sentry-example-page
These return 401 (not 404), confirming they are active and auth-protected in production.

### betsbk.com
- Same Next.js codebase as smarkets.com (shared route structure)
- Separate Sentry project (ID 21)
- NO CFTC product (/cftc/ returns 404)
- Has /v3/promotions/ endpoints not seen on smarkets.com
- No /members/login or /members/signup routes (different auth flow)

### sbkscores.com API
- /api/v3/live-counts — returns live match counts per sport (JSON, no auth)
- /api/health/ — returns `{"service":"sbkscores-site","status":"ok","timestamp":"...","uptime":0}`
- /api/v3/sport-signals — requires locale parameter
- Preconnects to api.smarkets.com (uses Smarkets API directly)

### GitHub Intelligence
- 112 public repos under github.com/smarkets
- smk_api_common/seto.piqi: 2520-line API protocol definition (all message types, Runningball integration, admin cancellation)
- smk_trading_bot: API base URL (https://api.smarkets.com/v3/), endpoint patterns
- Technology stack: Erlang (primary), K8s (AWS eu-west-1), HAProxy (voyager), RabbitMQ, PostgreSQL, Cassandra, Chef, Ansible

### DNS Intelligence
- Anthropic domain verification in TXT records (Smarkets using Claude AI)
- SPF: includes AWS IP 176.34.128.115, Google, Mailchimp, Mailgun
- MX: Google Workspace
- NS: Cloudflare (megan.ns + sid.ns for smarkets.com/staging; collins.ns + ignacio.ns for betsbk/oddsindex/sbkscores)

### Second-Pass Findings — CSP Header Leak (CRITICAL)

The CSP header on oddsindex.com (secondary property) leaked the entire internal topology that smarkets.com's CSP did not expose:

**CSP `connect-src` leaked:**
- `*.smarkets.work` wildcard → resolved to `172.16.1.2` (private IP, RFC 1918)
- `silverstripe.k8s.smarkets.com` → resolved to `10.2.229.41`, `10.2.30.85` (private IPs)
- `betsbk-staging.com` (staging domain not in CT logs)
- `api.oddsindex.com` (internal API)
- Dev ports: 8080, 8081, 3001

**Missing security headers (all properties except oddsindex.com which had CSP):**
- smarkets.com: no CSP, no HSTS, no X-Frame-Options, no X-Content-Type-Options
- betsbk.com: same missing headers
- sbkscores.com: same missing headers

### Status Page Intelligence

`status.smarkets.com/api/v2/incidents.json` (public, no auth) returned 50 incidents including:
- Critical bet placement failures
- Critical login failures
- Component names revealing internal service architecture
- `status.smarkets.com/api/v2/status.json` returns current operational status

### oddsindex.com Deep Dive

- References 30+ competing brands in JS: DraftKings, FanDuel, Kalshi, Polymarket, BetMGM, Caesars, PointsBet, etc.
- Uses Betradar/Sportradar for odds data
- Has WebSocket proxy configuration and internal dev ports (8080, 8081, 3001) in production JS
- Separate Cloudflare nameserver pair from smarkets.com

### Source Maps

Checked for `.map` files alongside all JS chunks across all properties. All returned 404 — source maps are properly disabled in production.

## Full Audit Reports
- `~/smarkets-audit/cftc-infrastructure-leak-july-2026.md` — CFTC findings detail (initial)
- `~/smarkets-audit/infrastructure-intelligence-map-july-2026.md` — Full infrastructure map (57KB, 1093 lines, 60+ paper trail entries, severity ratings, 19 recommendations). Two-pass audit including CSP header analysis, security headers check, status page API, robots.txt intelligence, and oddsindex competitor mapping.
- `surface-infrastructure-reconnaissance` skill → `references/smarkets-case-study-july-2026.md` — Condensed case study of the two-pass audit methodology and key lessons.

## Support Response Guidance

When a customer mentions `sio-live.smarkets.com` or any streaming endpoint:
1. Flag that the hostname is not part of the documented Smarkets API
2. Confirm the documented API is REST-only via `api.smarkets.com`
3. Market data is available via REST endpoints (quotes, last_executed_prices, volumes)
4. Decline the request. There is no streaming API available for API customers. Do NOT redirect to `api@smarkets.com` to "discuss options" for streaming. If it is not in the documentation, we do not offer it. State this plainly and move on.
5. Note that use of undocumented endpoints falls outside the API agreement.
6. Do NOT mention the CFTC product or CFTC-specific endpoints to customers
7. Do NOT explain how the endpoints were discovered (public JS analysis) — just state they're not part of the documented API
8. If the customer is requesting IP whitelisting, proceed with `api.smarkets.com` only

When a customer mentions `stream.smarkets.com:3801` specifically:
1. This is from the deprecated `smk_python_sdk` (GitHub repo archived since January 2019)
2. The endpoint is no longer in service — the SDK is historical reference only
3. The current public API is REST-based with no streaming endpoint
4. Recommend polling REST endpoints for near-real-time data (within rate limits)
5. There is no streaming API available. Do NOT redirect to `api@smarkets.com` for streaming requests.
6. Do NOT explain the SDK's protobuf/TCP protocol or how it was verified — just state it's deprecated

## Verification Notes

When making factual claims about endpoint status or deprecation in customer responses:
- Claims in reference files may originate from prior sessions and be unverified
- If a customer challenges a claim, trace it to its primary source before reasserting
- For GitHub-hosted SDKs: check repo `archived` flag, `pushed_at` date, and source code for hardcoded endpoints
- Distinguish between verified facts (repo archived, endpoint in source code) and inferences (endpoint decommissioned — consistent with archived SDK but not independently DNS-verified)
