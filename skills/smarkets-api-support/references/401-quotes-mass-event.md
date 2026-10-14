# Mass 401 on GET /v3/markets/{ids}/quotes/ — Diagnostic Flow

## Symptom Pattern
Customer reports 401 AUTH_REQUIRED on all /quotes/ requests while /events/ and /markets/ continue returning 200. Token believed valid (customer cites "24-hour TTL" — actually 30 min with sliding renewal).

## Diagnosis
Most likely: **token expired**. The /quotes/ endpoint requires auth; /events/ and /markets/ do not (public endpoints — do NOT reveal this to customer). The customer's "24-hour TTL" belief is a common misconception. Actual TTL is 30 minutes with sliding renewal.

## Distinguishing Questions
- **"Did the issue resolve on its own, or did your code re-authenticate?"**
  - Resolved after re-auth → confirms token expiry
  - Resolved on its own → possible transient auth validation issue on /quotes/ specifically (noted in api-technical-quirks.md)
- Ask for the full 401 response body to confirm error_type is AUTH_REQUIRED

## What 401 is NOT
- NOT a rate limit (rate limits return 429 with RATE_LIMIT_EXCEEDED)
- NOT a service disruption (service issues return 503 with MDS_SERVICE_UNAVAILABLE, SBK_PRICER_UNAVAILABLE, etc.)
- NOT a settled-market response (settled markets return 200 with empty books)

## Customer Response Approach
- Correct the 24-hour TTL misconception (it's 30 min sliding renewal)
- Point to the "stop" field in POST /v3/sessions/ response for actual expiry timestamp
- Do NOT explain why /events/ and /markets/ kept working (security exposure)
- Say: "The 401 on /quotes/ is the authoritative signal that the token wasn't being accepted"
- Frame service disruption question via error codes: "A service issue would return 503, not 401"
- Suggest: token refresh check on "stop" timestamp, auto re-auth on 401, authenticated request every 25 min (buffer under 30-min TTL)
- Quotes endpoint accepts up to 200 market IDs per request (maxItems: 200 in live spec) — customer can increase batch size from 50 to reduce request count

## Source References
- references/api-technical-quirks.md — token TTL (30 min sliding renewal), 24-hour misconception, quotes error responses
- references/rate-limits.md — 429 vs 401 distinction, quotes 50/60s limit
- references/quotes-endpoint-behaviour.md — settled markets return 200 with empty books
- Live spec: https://api.smarkets.com/v0/control/openapi/?tags=trading_api — quotes endpoint response codes
