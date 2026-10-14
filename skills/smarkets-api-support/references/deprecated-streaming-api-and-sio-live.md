# Deprecated Streaming API and sio-live.smarkets.com

## Context

Research conducted July 2026 when a customer requested IP allowlisting for two hostnames: `api.smarkets.com` and `sio-live.smarkets.com`. Investigation revealed three distinct Smarkets infrastructure tiers and confirmed that `sio-live.smarkets.com` is NOT from the deprecated GitHub SDK.

## Three-Tier Infrastructure

| Tier | Hostname | Protocol | Status | Source |
|------|----------|----------|--------|--------|
| Old streaming API | `stream.smarkets.com:3801` | TCP + SSL + protobuf framing | Deprecated | `github.com/smarkets/smk_python_sdk` (copyright 2011) |
| Current REST API (v3) | `api.smarkets.com` | HTTPS / JSON | Active | OpenAPI spec at docs.smarkets.com |
| Website frontend | `sio-live.smarkets.com` | WebSocket (raw, NOT Socket.IO despite "sio" prefix) | Internal, undocumented | Hardcoded in smarkets.com public JS (chunk 7491) |

## Deprecated smk_python_sdk

**Repo:** `github.com/smarkets/smk_python_sdk` — **archived** (GitHub API: `archived: true`, last push 2019-01-08). Still publicly visible but read-only.

## Verification Evidence (July 2026)

All claims below verified against primary sources, not inferred from prior notes:

- **GitHub API** (`api.github.com/repos/smarkets/smk_python_sdk`): `archived: true`, `pushed_at: 2019-01-08T10:44:07Z`, `stargazers_count: 18`
- **Source code** (`session.py` line 24): `host='stream.smarkets.com', port=3801, ssl=True` — confirms endpoint origin
- **DNS** (`dig +short stream.smarkets.com A`): empty response — NXDOMAIN confirmed
- **Repo contents**: `smarkets/streaming_api/session.py` contains `SessionSettings` class with the hardcoded default

**Distinction:** NXDOMAIN is a verified fact (DNS returns no records). "Decommissioned" is an inference (could also be DNS misconfiguration or never deployed). State the former as fact, the latter as likely.

**Description:** "Smarkets Streaming API Python client" — compatible with Python 2.7, 3.5 and PyPy 1.9+.

**Default host:** `stream.smarkets.com` (port 3801, SSL=True)

**Protocol:** Raw TCP socket with SSL, using Google Protocol Buffers for message framing. NOT Socket.IO, NOT WebSocket, NOT HTTP.

**Key code** (`session.py`):
```python
class SessionSettings(object):
    def __init__(self, username=None, password=None, token=None,
                 host='stream.smarkets.com', port=3801, ssl=True, ...):
```

**Order types in SDK:** `IMMEDIATE_OR_CANCEL`, `GOOD_TIL_CANCELLED` (note: uppercase naming, different from v3 API's `immediate_or_cancel`, `good_til_cancelled`)

**Documentation:** Was hosted at `smarkets-python-sdk.readthedocs.io` (still accessible)

**Related repo:** `github.com/smarkets/smk_api_docs` — "Smarkets API documentation generator" (also still public)

**Deprecated `smk_python_sdk` GitHub repos:**
- `github.com/smarkets/smk_python_sdk` — Python SDK with streaming client
- `github.com/smarkets/smk_api_docs` — API documentation generator
- `github.com/smarkets/smarkets` — 404 (deleted or made private)
- `github.com/smarkets/smarkets-api` — 404
- `github.com/smarkets/api` — 404

## sio-live.smarkets.com

**What it is:** Raw WebSocket endpoint (NOT Socket.IO despite the "sio" prefix, confirmed by JS analysis showing ``new WebSocket(this._url)``) used by the Smarkets website frontend for real-time market data push to browsers.

**NOT from the deprecated SDK:** The SDK uses `stream.smarkets.com:3801` (protobuf/TCP). `sio-live` uses Socket.IO (WebSocket). Completely different protocol, hostname, and purpose.

**Wayback Machine evidence:** First archived Feb 6, 2023. CDX API shows:
```
com,smarkets,sio-live)/ 20230206232746 https://sio-live.smarkets.com/ application/json 200
com,smarkets,sio-live)/ 20230213224621 https://sio-live.smarkets.com/ warc/revisit
```

**Public search results:** DuckDuckGo search for `"sio-live.smarkets.com"` returns only an IPQS domain reputation check page. No documentation, no GitHub references, no third-party articles. The hostname exists but is completely undocumented publicly.

**How customers discover it:** Browser DevTools network tab on smarkets.com shows the frontend connecting to `sio-live.smarkets.com` via Socket.IO for live price updates. Customers inspecting network traffic assume it's part of the API infrastructure.

## Research Methodology

1. Searched local workspace (`~/smarkets-api-support/`) for `sio-live`, `socket.io`, `streaming`, `websocket` — no matches in API docs or OpenAPI spec
2. Checked `github.com/smarkets/smarkets` — 404 (deleted/private)
3. Checked `github.com/smarkets/smarkets-api` and `github.com/smarkets/api` — both 404
4. DuckDuckGo search for `"sio-live.smarkets.com"` — only IPQS domain reputation result
5. DuckDuckGo search for `smarkets sio socket.io streaming api site:github.com` — found `smk_python_sdk` and `smk_api_docs` repos
6. Examined `smk_python_sdk` README — default host is `stream.smarkets.com:3801`, NOT `sio-live`
7. Examined `smk_python_sdk/session.py` raw source — confirmed `host='stream.smarkets.com'`, `port=3801`, `ssl=True`
8. Wayback Machine CDX API (`web.archive.org/cdx/search/cdx?url=sio-live.smarkets.com*`) — confirmed archived since Feb 2023, content type `application/json`

## Customer Response Guidance

Customer-facing wording rule (added after council review, 2026-09-16): scope the denial to the API. "We don't offer websockets or a streaming feed. The API is REST only, so there is no websocket interface to connect to." Never state absolutely that no websocket exists anywhere at Smarkets - `wss://sio-live.smarkets.com` is live for the website frontend and a customer with DevTools open can refute the claim. Do not use "nothing you've done wrong" (banned reassurance register); state the mechanism, then ask what instructions they were following and what the attempt returned rather than guessing at an archived SDK.

When a customer references `sio-live.smarkets.com`:

1. It is NOT part of the documented Smarkets API (current v3 REST or deprecated streaming)
2. It is the website frontend's Socket.IO endpoint, not an API endpoint
3. The documented API is REST-only via `api.smarkets.com`
4. If they need streaming/real-time data, take ownership and ask them to reply here with the use case. We ARE the API support team, so never reroute the customer to `api@smarkets.com` in customer-facing text.
5. Do NOT whitelist `sio-live.smarkets.com` as API infrastructure without internal review
6. The deprecated `smk_python_sdk` (with `stream.smarkets.com:3801`) is also not supported — it is a legacy SDK from 2011

## Key Distinction for Agents

Customers may confuse three things:
- **"I found a streaming endpoint on GitHub"** → They found `smk_python_sdk` which uses `stream.smarkets.com:3801` (deprecated protobuf/TCP from 2011)
- **"I found sio-live.smarkets.com serves my IP"** → They found the website's Socket.IO endpoint via DevTools (never was an API)
- **"I need real-time data"** → Take ownership and ask them to reply here with the use case; current API is REST-only with polling endpoints (quotes at 50 req/60s)

All three lead to the same answer: the documented API is REST-only via `api.smarkets.com`. Take ownership and ask the customer to reply here with the use case rather than rerouting to `api@smarkets.com`, since we ARE the API support team.

## Cross-Reference

For the full streaming topology (including CFTC-specific endpoints), the CFTC product ("Smarkets Predictions") findings, and the comprehensive infrastructure intelligence map (25 hostnames, Firebase config, regulatory identifiers), see ``references/streaming-infrastructure-and-cftc-product.md``. Full audit reports at ``~/smarkets-audit/cftc-infrastructure-leak-july-2026.md`` and ``~/smarkets-audit/infrastructure-intelligence-map-july-2026.md``.
