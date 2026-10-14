# API Ticket Helper — Playbook & Technical Diagnostics

## 1. Diagnostic Triage Tree: HTTP Status Codes

### 401 Unauthorized
- **Symptom:** Client receives 401 on requests.
- **Triage:**
  - If 401 occurs on `POST /v3/sessions/`: Check credentials. Look for `INVALID_CREDENTIALS` or `PASSWORD_RESET_NEEDED`.
  - If 401 occurs ~20 minutes into an automated run: The token expired due to rotation. The client is sending only the static `Authorization: Session-Token` header. Smarkets rotates tokens every 20 minutes via cookies. Client must send `Cookie: User-Session-Token={token}; Refresh-Token={refresh}` and adopt the renewed token from `Set-Cookie`.
  - If 401 occurs after idle period: Session token TTL is 30 minutes. Log in again to get a fresh token.

### 403 Forbidden
- **Symptom:** Client receives 403.
- **Triage:** Request the raw response body.
  - **HTML Body:** Cloudflare edge block. The request did not reach Smarkets application servers. Causes: Server hosted in an unsupported country (outside UK, Sweden, Malta, Ireland), or datacenter IP flagged by Cloudflare threat intelligence. Solution: Move server to a supported region or contact api@smarkets.com for IP review.
  - **JSON Body:** API rejection. Inspect `error_type`:
    - `CLIENT_JURISDICTION_MISMATCH`: Account registered jurisdiction does not match IP jurisdiction.
    - `SOURCE_BLOCKED` or `IP_NOT_TRUSTED`: IP address flagged internally.

### 429 Rate Limit Exceeded
- **Symptom:** Client receives 429.
- **Triage:**
  - Check the endpoint:
    - If on `POST /v3/sessions/`: The account exceeded 5 logins per 300 seconds. Client must wait for `expiry` before retrying and cache the session token.
    - If on `GET /v3/markets/{id}/quotes/`: Endpoint limit is 50 requests per 60 seconds. Client should batch contract reads or throttle polling.
    - If global across endpoints: Total authenticated volume exceeded 1,200 requests per 60 seconds per account.
  - Handling Rate Limit Increases: Smarkets evaluates increases on a case-by-case basis. Inquiries must go to api@smarkets.com with trading strategy, target markets, and expected request volume.

---

## 2. Five-Question Scope Confirmation Pattern

When an applicant or developer asks about authorized trading scope, answer each question directly:

1. **Approved events and markets:** Under Section 5 of the API Terms and Conditions, API usage is restricted to pre-approved events and markets agreed during application. This scope is maintained per-account and is not published. Contact api@smarkets.com to review or adjust approved scope.
2. **In-play betting:** In-play trading is permitted for approved accounts within their agreed event scope. In-play delay applies (4s for horse racing, 8s for football/other sports per Rule 8.2.1).
3. **Hedging and automated risk management:** Automated execution for hedging and risk management is permitted under Section 1. Latency arbitrage and court-siding (exploiting transmission delays) are prohibited under Section 7.
4. **Suspensions and order persistence:** On market halt, resting orders of type `good_til_halted` and `good_til_cancelled` are cancelled by the exchange. Orders placed as `keep_in_play` remain active across market state transitions.
5. **Streaming vs REST:** Smarkets provides an HTTP REST API only. There is no supported public streaming or WebSocket feed for API trading.

---

## 3. Persistent 429 Escalation Replies

When a client reports a 429 that persists beyond published windows (or appears server-specific):
- Do not endorse the assumption that the limiter is IP-based (documented rate limits are account-scoped).
- Request a single compact diagnostic bundle:
  1. Exact UTC timestamp of the request.
  2. Complete request URL and HTTP method.
  3. Full response status code and raw response body.
  4. Complete response headers, specifically `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After`.
- State that clearing or resetting an account limit requires investigation by the API team without promising the outcome.

---

## 4. Onboarding Fee & Section 3 Refunds

- **Setup Fee:** GBP 150 (or account currency equivalent) is deducted from account balance upon registration for API access.
- **Refund Policy (Section 3):** If the customer chooses to permanently withdraw from API usage within the first 60 days, the setup fee is fully refunded to their balance upon request.
- After 60 days, Section 3 does not apply and the fee is non-refundable.
