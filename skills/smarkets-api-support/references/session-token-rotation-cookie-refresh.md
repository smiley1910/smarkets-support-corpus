# Session token rotation: the ~20 minute 401 and the cookie/refresh fix (verified 2026-10-01)

## Symptom
- Client authenticates with `Authorization: Session-Token <token>` only, same token throughout.
- Active polling (e.g. `GET /v3/orders/` every 20 s) returns 200s, then the first `401 AUTH_REQUIRED` (data null) lands at **20.0 to 20.2 minutes after login**, before the login response `stop` (login + 30 min), about 20 s after a success with the same header.
- Five runs observed at 20.0, 20.2, 20.1, 20.1 minutes and 20m09s. That rules out idle expiry, concurrent sessions, MFA/verify, header format and rate limits. Do not keep re-probing those.

## Cause
Session tokens rotate on a ~20 minute cycle. Renewal runs through the session and refresh tokens, as cookies. A header-only client keeps presenting the original token; at the rotation point it is no longer valid and the next request returns `401 AUTH_REQUIRED`. The "valid 30min, renewed by each authenticated request" wording does not cover this rotation and is what misleads diagnosis.

## Fix (customer guidance)
1. Capture both tokens at login. The login response returns `refresh_token` in the body and sets the cookies.
2. Send both with every request: `Cookie: User-Session-Token=<token>; Refresh-Token=<refresh_token>`
3. Adopt each renewed `User-Session-Token` (arrives via `Set-Cookie` mid session) and use it for subsequent requests.
4. Log response cookies. The rotation is only visible in `Set-Cookie`; request-only logging hides it.
5. Re-run the timed test; expect survival past the 20 minute mark and past the 30 minute stop.

## Login facts (probed live on the test account, 2026-10-01)
- 201 body keys: `created_social_member`, `factor`, `refresh_token` (len 100), `stop`, `token` (len 154), `verify`.
- 5 `Set-Cookie` headers: `Refresh-Token` (~6 months), `Logged-In` x2, `User-Session-Token` (~1 month), `device-cookie` (~1 year).
- Identical shape with and without `use_auth_v2: true`.

## Live verification (paired arms, 20 s polls, 36 minutes, completed 2026-10-01 17:15:54 UTC)
- CONTROL (header-only, mirrors the failing client): first 401 at **t+19:58** (58x 200 before, last 200 at t+19:38), then rejected for the rest of the run.
- TREATMENT (sends both cookies, adopts renewed token): **survived the full 36 minutes, 105x 200, zero 401s**; at **t+20:19 a rotated User-Session-Token arrived via Set-Cookie** and was adopted, carrying it past its 30 minute stop.
- Evidence: `~/smarkets-api-support/responses/2026-10-01-session-token-refresh/` (probe_login_modes.py, cookie_refresh_36min.py, run-cookie-refresh.log, run-cookie-refresh-results.json).
