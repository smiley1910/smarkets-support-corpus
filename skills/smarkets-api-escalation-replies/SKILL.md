---
name: smarkets-api-escalation-replies
description: Use for Smarkets API persistent throttling replies.
category: process
---

# Smarkets API Escalation Replies

Use this class skill for persistent or apparently IP-specific API throttling, requests to clear a block, and questions about session lifetime or longer-lived credentials.

## Workflow
1. Separate customer observations from verified platform facts.
2. Answer documented questions directly.
3. Treat unexplained persistence, count mismatches, and server-specific behaviour as investigation items, not proof of an IP block or abuse mechanism.
4. Never claim an IP/account reset, engineering review, or successful unblock unless completed and verified.
5. Ask for one compact diagnostic bundle when needed: timestamp, status, complete response body, and all response headers, especially `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After`.
6. Treat the customer's remediation as context, not blame.

## Verified answer set
- `POST /v3/sessions/`: maximum 5 requests per 300 seconds, applied per account.
- Global authenticated API limit: 1,200 requests per 60 seconds across endpoints, applied per account.
- Session tokens: valid for 30 minutes and renewed by authenticated requests. The `stop` value gives expiry.
- No longer-lived API key or static credential is documented publicly for approved API users. Do not imply one can be provisioned without API-team confirmation.

## IP-specific reports
Documented rate limits are account-scoped, so do not endorse the assumption that a session limiter is definitely IP-based. Do not dismiss a report that succeeds from home but fails from a server. State that the mechanism is unconfirmed and requires raw response data. A 429 persisting beyond the published 300-second window is an anomaly requiring review.

## Reply shape
Acknowledge the persistent 429 and remediation, give the documented limit/token/credential answers, say the clear/reset request needs API-team investigation without promising the outcome, identify the count/persistence discrepancy as requiring verification, and finish with the single diagnostic bundle request.

Avoid unnecessary apology, blame, claims that the IP was cleared, claims that `count`/`limit`/`expiry` must always exist on this endpoint, and unsupported explanations involving edge protection or abuse systems.

See `references/persistent-session-429.md` for the evidence map and wording decisions from the August/September 2026 case.
