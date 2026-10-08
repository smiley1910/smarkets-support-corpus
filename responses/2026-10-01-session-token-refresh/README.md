# Session token ~20-min death — cookie/refresh flow investigation (2026-10-01)

## Ticket
API customer sessions rejected with `401 AUTH_REQUIRED` ~20 minutes after login (all 5 recorded runs: 20.0–20.2 min), despite `GET /v3/orders/` polling every 20s and `stop` stating login + 30 min. Escalated to engineers. Engineers replied: client must send
`Cookie: User-Session-Token=<token>; Refresh-Token=<refresh_token>` — the refresh token mints a new User-Session-Token (rotation at ~20 min) which must be used for subsequent requests.

## Question asked (2026-10-01): has this already been tried?
**No on both counts.**
- Customer: has never mentioned cookies or refresh tokens. Their full log submission (~100 requests, 40KB) is `Authorization: Session-Token` header-only with one fixed token; zero occurrences of `cookie`/`refresh`/`set-cookie` in it, and their harness did not capture any `Set-Cookie` from responses.
- Support side: never tested the cookie flow and never suggested it to the customer. Ticket history (four runs → logs request → 30 Sep logs → escalation) stayed on the header/remember/verify path. Internal docs only: KB classifies "auth v2, refresh tokens, cookies" as "not covered here — escalate"; the Sep 23 Q5/Q6 brief flagged the `use_auth_v2`/refresh flow as an open question.

## Live probe (2026-10-01 16:38 UTC, test account, 0 funds)
Both a **default login** and a `use_auth_v2: true` login return identical shape:
- body: `token` (154 ch), `refresh_token` (100 ch), `factor: complete`, `stop`
- 5 `Set-Cookie` headers: `Refresh-Token`, `Logged-In` (x2), `User-Session-Token`, `device-cookie`
  - Refresh-Token expires ~2027-04-08; User-Session-Token expires ~2026-10-31; device-cookie ~2027-09-30

Conclusion: the engineers' fix is implementable on the standard login — no `use_auth_v2` flag needed; the cookies are issued already and the customer's client was simply not capturing or sending them.

## Paired test — COMPLETE (16:39:47 to 17:15:54 UTC, 20 s polls, 36 min)
- CONTROL (header-only): first 401 at t+19:58 (58x 200 before; last 200 t+19:38). Dead for the remainder.
- TREATMENT (cookies + adopt renewed token): SURVIVED full 36 min, 105x 200, zero 401s; rotated User-Session-Token received via Set-Cookie at t+20:19 (fp 3201aab8b7 -> 62b8d45375) and adopted; crossed its 30 minute stop with 200s.

**Verdict: mechanism and fix confirmed live. Header-only clients die at the ~20 minute rotation; sending both cookies and adopting the renewed token carries the session.**

## Files
- `probe_login_modes.py` — default vs use_auth_v2 login comparison (done)
- `cookie_refresh_36min.py` — paired arms test (done)
- `run-cookie-refresh.log` — full live log
- `run-cookie-refresh-results.json` — final results
- `draft-customer-reply-v1.md` + `draft-customer-reply-v2.md` — v2 is the council-cleared customer draft (v1 kept for history)

## Docs updated from this case
- skill refs (smarkets-api-support): `references/session-token-rotation-cookie-refresh.md` (new), `references/api-technical-quirks.md` (TTL correction), SKILL.md pointer; smarkets-api-development pitfall 29.
- workspace: docs/smarkets_api_knowledge_base.md, troubleshooting/common_api_issues.md, training/confluence_draft_v2.md, training/pattern_matching_guide.md.
