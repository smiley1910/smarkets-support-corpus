# Rate Limit Requests — Verification and Response Guide

## Documented Rate Limits (from OpenAPI spec)

| Endpoint | Rate Limit | Scope |
|---|---|---|
| GET /v3/markets/{market_ids}/quotes/ | Maximum 50 requests per 60 seconds | Per account (inferred from orders endpoint) |
| POST /v3/orders/ | "Rate limits are applied on an per account basis" | Per account (explicit) |
| DELETE /v3/orders/ | Maximum 1 request per 60 seconds | Per account |
| DELETE /v3/orders/{order_id}/ | Maximum 10 requests per second | Per account |
| DELETE /v3/sessions/ | Maximum 30 requests per 60 seconds | Per account |
| POST /v3/sessions/ | Maximum 5 requests per 300 seconds | Per account |

## The "Defaults" Claim Pattern (corrected 2026-09-16 against the live spec)

Customers may claim the OpenAPI spec describes rate limits as "defaults," implying flexibility for higher tiers. Do NOT answer that the spec never uses the word "default" - it does, for the global limit:

- `info.description` (verbatim, live spec re-fetched 2026-09-16): "All API users are subject to a default rate limit of 1200 requests per 60 seconds across all endpoints, applied per account. Individual endpoints may have additional stricter limits as documented on each route below."
- Every rate-limited route instead reads "## Rate limits / Maximum X requests per ...".

The earlier version of this file claimed the spec uses "Maximum" consistently and that no occurrence of "default" relates to rate limits. That was wrong for the global limit. The support position is unchanged in practice: no higher tier is offered, declines follow the section below, and `X-RateLimit-Limit` is ground truth for an account's effective cap.

### How to Verify (parse the spec programmatically)

```python
import json, re

with open('openapi/smarkets_openapi.json') as f:
    spec = json.load(f)

# Get quotes endpoint description verbatim
quotes = spec['paths']['/v3/markets/{market_ids}/quotes/']['get']
print(quotes.get('description', 'N/A'))
# Output: "## Description\nIf session token is not sent, these prices will be delayed.<br><br>\nThe rate limits below are applicable to API users.\nThe rate limits for non-API users are lower.\n\n##  Rate limits\nMaximum 50 requests per 60 seconds"

# Get orders endpoint (explicitly mentions per-account scoping)
orders = spec['paths']['/v3/orders/']['post']
print(orders.get('description', 'N/A'))
# Contains: "Rate limits are applied on an per account basis"

# Confirm NO "default" appears near rate limit text
spec_str = json.dumps(spec)
for match in re.finditer(r'.{0,80}(?:rate.limit|RateLimit|rate_limit).{0,200}', spec_str, re.IGNORECASE):
    print(match.group())
```

## Rate Limit Scoping: Per Account vs Per Session Token

The only explicit scoping language in the OpenAPI spec is on the POST /v3/orders/ endpoint:
"Rate limits are applied on an per account basis"

The quotes endpoint does not separately specify scope, but per-account is the only documented model. When a customer asks whether the quotes allowance is per-account or per-session-token, the documented answer is: per account.

Practical implication for customers: if running multiple session tokens against the same account, they share a single rate limit allowance.

## No-Auth Rate Limit Behaviour (July 2026 Live Test)

Hammered `GET /v3/events/` with 20 concurrent threads, NO authentication:
- **18,141 requests in 90 seconds** (12,086 RPM) — zero 429s, all returned 200
- No `X-RateLimit-*` headers on any response

**The 1200 RPM limit is per-account (session token), NOT per-IP.** Public endpoints are effectively unlimited without auth. Cloudflare sits in front but does not apply API rate limits to unauthenticated traffic.

The one exception is `POST /v3/sessions/` — it returns rate limit headers (`limit=5 remaining=4 reset=299`) even with invalid credentials, as brute-force protection on the login endpoint.

**Support implication:** If a customer asks about rate limits for public data access (events, markets, contracts, currencies), the answer is: no rate limit applies to unauthenticated requests. However, authenticated requests (quotes, orders, accounts) always require a session token, so the 1200 RPM limit always applies to them. Customers should use a session token for real-time (non-delayed) quotes data.

**RESOLVED (July 2026):** The API requires `username` as the JSON key (the value IS the email address). OpenAPI spec: `"username": {"format": "email", "example": "john.doe@company.com"}`. User confirmed: "smarkets username IS email." All login scripts must use `{"username": "user@example.com", "password": "..."}`.

## Declining Rate Limit Increases

Check batch size BEFORE declining (see `rate-limits.md`, "Check Batch Size BEFORE Declining a Throughput Increase"): the quotes endpoint takes 200 market ids per call, so batch advice that changes what the customer does comes first. Worked example: 30 Sep 2026 — batch advice led, the decline followed, no six-limit recital.

Current approved customer line for the increase itself (Michael's own wording, 30 Sep 2026): "We are unable to review quote limit increases at this time; once you've built a larger sample size of activity we can review and request this for you." Keep it exactly that vague: no dates (a "request this again in 90 days" variant was rejected), no thresholds, no showy aggregate throughput totals. Internally an increase requires market maker level participation, which no regular user realistically reaches; that fact never appears in customer text.

Keep the old safeguards: state the documented limit where it does work; correct any "defaults" misreading (the global line says "default", the route lines say "Maximum"); do NOT redirect to `api@smarkets.com` to "discuss volume or commercials"; do NOT suggest workarounds or alternatives outside the documentation. Avoid the too-definitive blanket "these limits can't be increased".

## Fair Usage Policy Context

The API agreement (Section 6) states:
- Smarkets pre-approves call limits per period
- Circumventing rate limits is prohibited
- Using undocumented endpoints falls outside the API agreement

Using `sio-live.smarkets.com` to stream prices instead of polling the documented REST endpoints within rate limits could constitute circumvention. Note this factually if relevant, without being threatening.

## Session: July 2026

Customer requested: streaming whitelist for `sio-live.smarkets.com`, official streaming API, rate limit increase (50 to 400-600/min), and rate limit scoping clarification.

Response: declined streaming (not documented, not offered), corrected "defaults" claim (spec says Maximum), declined rate limit increase, confirmed per-account scoping. Michael's instruction: "lets not offer something outside of documentation, theyre asking for something we simply do not offer."
