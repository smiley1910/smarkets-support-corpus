# Login Error Ticket Patterns

Common customer ticket patterns for `POST /v3/sessions/` authentication failures, with pre-drafted response templates and misconception-busting guidance.

## DEVICE_NOT_TRUSTED (403) — "I need IP whitelisting"

### Customer phrasing
- "Could you whitelist my device or IP for API access?"
- "I logged in via the browser from the same computer but the API still fails"
- "I keep getting 403 DEVICE_NOT_TRUSTED on POST /v3/sessions/"
- "Could you help approve/whitelist my device or IP for API access"

### What's happening
The API client is being treated as an untrusted device. Browser login and API authentication are separate channels — logging in via smarkets.com does not transfer device trust to API requests. The browser session carries cookies and identifiers that the API client does not share.

### Critical customer misconceptions to address
1. **"Whitelist my IP"** — Smarkets does not offer IP whitelisting. Device trust is managed at the device level, not by IP address. This applies to all 403 login errors, not just Cloudflare blocks.
2. **"I logged in via the browser"** — Browser login and API authentication are separate channels. Completing a browser login does not mark the device as trusted for API use.
3. **"It's a network/IP issue"** — The response is JSON (`{'data': None, 'error_type': 'DEVICE_NOT_TRUSTED'}`), confirming this is an API-level 403, not a Cloudflare network block (which would return HTML starting with `<!DOCTYPE`).

### 403 diagnostic quick reference

**CRITICAL: Before diagnosing any 403, you must know whether the response body is HTML or JSON.** If the customer only shared the HTTP status code or a Python error message (e.g., "Forbidden for url: https://api.smarkets.com/v3/sessions/"), you do NOT have enough information to diagnose. Ask the customer for the full response body (e.g., print(response.text) or curl output) BEFORE claiming it is a Cloudflare block, a jurisdiction block, or an API-level rejection. Presenting a diagnosis without the response body is presenting an inference as fact — do not do this.

| Response body | Error type | Cause | Resolution |
|---|---|---|---|
| JSON | `DEVICE_NOT_TRUSTED` | Device not marked as trusted | Complete device trust verification on smarkets.com |
| JSON | `IP_NOT_TRUSTED` | IP address not recognised | Complete device trust verification on smarkets.com |
| JSON | `FORBIDDEN` | Account-level block (not approved, compliance review, suspended) | Check API access status, contact api@smarkets.com |
| JSON | `USER_SUSPENDED` | Account suspended by Smarkets | Contact support@smarkets.com |
| JSON | `SESSION_LIMIT_REACHED` | Too many active sessions | Log out from other sessions first |
| JSON | `CLIENT_JURISDICTION_MISMATCH` | Account country doesn't match IP | Contact support@smarkets.com |
| JSON | `LOGIN_VERIFICATION_REQUIRED` | Additional login verification (2FA/MFA or security check) outstanding | Complete the verification step (e.g. MFA code / security check) and retry. NEW in live spec, Aug 2026 — appears on `POST /v3/sessions/`, `DELETE /v3/sessions/`, and `POST /v3/sessions/verify/` 403s. |
| HTML (starts with `<!DOCTYPE`) | Cloudflare | Network-level block (datacenter IP, unsupported jurisdiction) | Flag for technical support. See `references/streaming-infrastructure-and-cftc-product.md` for IP allowlisting context. |

### Pitfall: Do not assume Cloudflare vs API-level 403 without the response body

Customers often share Python's requests library error message (e.g., "Forbidden for url: https://api.smarkets.com/v3/sessions/") which only gives the HTTP status code, not the response body. The 403 diagnostic table above requires knowing whether the body is HTML (Cloudflare) or JSON (API-level with error_type). When the customer has not shared the response body:

1. Do NOT claim it is specifically a Cloudflare edge block or a specific JSON error_type
2. Ask for the full response body (suggest `print(response.text)` or `curl -v` from the server)
3. Note any relevant contributing factors (e.g., VPS in unsupported jurisdiction) as a side note in the same response
4. Wait for the response body before giving a definitive diagnosis

This applies to all 403 scenarios where the customer shares a library error message rather than the raw HTTP response.

### Resolution
1. Complete device trust verification on smarkets.com (log in, complete any verification prompts — typically a verification link sent to registered email)
2. Retry the API authentication

### Escalation path
- If the customer is running from a VPS or data centre IP, the device trust flow may not complete from that environment. This may require internal allowlisting via api@smarkets.com.
- If the error persists after completing device trust steps, request: timestamp of last failed request, whether running from local machine or server, and full request headers (credentials redacted).
- Login is rate-limited to 5 attempts per 300 seconds. If the customer has been retrying frequently, they may also be hitting the rate limit (429).

### Response template

**Pitfall (July 2026):** Do NOT paste this template verbatim as the first response. The template assumes the customer is running from a local machine. If the customer has not told you WHERE their API client runs (local machine vs server/VPS), ask 1-2 focused probing questions FIRST before prescribing a resolution. Michael's explicit correction: jumping to a diagnosis without enough information is wrong, and listing 6 questions is too many. One or two focused questions (e.g., "Have you been able to authenticate from your local machine, or are you running from a server? If so, what's the IP?") is the right approach.

The template below is the resolution path AFTER you have confirmed the customer's environment matches the expected pattern.

.. code-block:: rst

    Hi [name],

    Thanks for getting in touch, and glad to hear your API access has been approved.

    The ``DEVICE_NOT_TRUSTED`` error is a device-level security check, not an IP
    block. Browser login and API authentication are treated as separate channels,
    so logging in via the website doesn't automatically mark the device as
    trusted for API use.

    To resolve this, please complete the device trust verification on smarkets.com:

    #. Log in at `smarkets.com <https://smarkets.com>`_
    #. If you see a device verification prompt, complete it. This typically
       involves clicking a verification link sent to your registered email address.
    #. Once verified, retry your ``POST /v3/sessions/`` request.

    A few things to note:

    * Smarkets does not offer IP whitelisting. Device trust is managed at the
      device level, not by IP address.
    * If you are running your API client from a VPS or data centre server rather
      than your local machine, the device trust flow may not complete successfully
      from that environment. Let me know if that's the case and we can look into
      it further.
    * The sessions endpoint is rate-limited to 5 requests per 300 seconds, so
      leave a gap between retries to avoid hitting the limit while testing.

    If the error persists after completing the steps above, please reply with the
    approximate timestamp of your last failed request and whether you're running
    from a local machine or a server, and I'll investigate further.

    Best regards,
    Michael

## IP_NOT_TRUSTED (403)

Same pattern as DEVICE_NOT_TRUSTED. Customer may say "my IP isn't recognised" or "IP_NOT_TRUSTED error." Resolution is identical: complete device trust verification on smarkets.com. Same misconceptions apply (no IP whitelisting, browser ≠ API).

## INVALID_DEVICE_COOKIE (400)

Different from the above. This means the request is missing the device identifier entirely (not that the device is untrusted). Resolution: ensure the request includes the device cookie. This is a request-formatting issue, not a trust issue.

## Related error codes (from training materials)

Full login error code table is in `~/smarkets-api-support/training/pattern_matching_guide.md` section "Login errors (POST /v3/sessions/)". The table covers: INVALID_CREDENTIALS (401), PASSWORD_RESET_NEEDED (401), INVALID_DEVICE_COOKIE (400), INVALID_TOKEN (400), DEVICE_NOT_TRUSTED (403), USER_SUSPENDED (403), USER_SELF_SUSPENDED (403), USER_ON_TIMEOUT (403), USER_EXCLUDED (403), SESSION_LIMIT_REACHED (403), IP_NOT_TRUSTED (403), SOURCE_BLOCKED (403), CLIENT_JURISDICTION_MISMATCH (403), LOGIN_VERIFICATION_REQUIRED (403, added to live spec Aug 2026), COUNTRY_BLOCKED (451).
