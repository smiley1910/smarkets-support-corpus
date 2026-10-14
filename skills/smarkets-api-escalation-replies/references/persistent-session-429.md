# Persistent session 429: evidence map

## Case pattern
Customer reports `POST /v3/sessions/` returning 429 from one server while login succeeds from home, with a count above the published cap and persistence after many idle hours. They also describe prior repeated login attempts and subsequent remediation.

## Verified versus unverified
Verified: the session endpoint maximum is 5 requests per 300 seconds per account; the global authenticated limit is 1,200 per 60 seconds per account; tokens last 30 minutes with sliding renewal; `stop` gives expiry; no public static API key is documented.

Unverified: whether the limiter is actually IP-scoped, whether an abuse or edge control is involved, whether the count is from the session endpoint's documented counter, whether an internal hold exists, and whether support has cleared anything.

## Safe response decisions
- Do not promise an IP clear or say the API team has reviewed it unless verified.
- Do not dismiss 15+ hours of persistence as a normal five-minute window.
- Do not reconcile a reported count of roughly 25 to 38 with the documented maximum of 5. Flag it for investigation.
- Do not assert that every session 429 includes `count`, `limit`, or `expiry`; request the complete body and headers instead.
- Do not blame the customer for the earlier misconfiguration. Treat it as relevant context.

## Preferred diagnostic bundle
Request, in one ask: timestamp, status, complete response body, and all response headers, especially `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After`. This is enough to distinguish the documented response from an account, IP, or other control without stacking several speculative questions.
