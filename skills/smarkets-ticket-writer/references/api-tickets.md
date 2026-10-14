# API Tickets (Access, Rate Limits, Auth, Order Types, Scope)

Application module of `process:smarkets-ticket-writer`. Universal voice,
structure, length and style gates live in `process:smarkets-voice-core` and
are not restated here. Load `process:smarkets-api-support` first for
diagnosis; this file governs the customer facing reply. If this file ever
seems to contradict voice-core, voice-core wins.

Absorbs (with gate corrections): `api-tcs-verification.md`,
`api-vs-website-liquidity.md`, `openapi-spec-verified-facts.md`, and the API
sections of `ticket-scenarios-and-examples.md`. Originals removed after
merge; verbatim history stays in the skill backup.

## Step zero: platform first

Ask whether they use the API or the website or SBK app before answering
order type, liquidity or limit questions. Do not use internal terms
("OpenAPI", "spec", "schema") in customer text; say "API documentation".

## Diagnose first, resolve second

If the customer gave logs, payloads, endpoints or request patterns, state
the likely diagnosis and ask for the one confirming evidence (full response
body, not just status). If they gave nothing, send two to four diagnostic
questions. Prefer a single soft hypothesis over multiple possibilities. Ask
about recurrence, not reconstruction. Mirror their stated facts once.

## Rate limits

The live spec at `https://api.smarkets.com/v0/control/openapi/?tags=trading_api`
is authoritative; the local copy is stale and must not be cited for limits.
Fetch it before citing figures and run `scripts/verify_live_spec.py` first.
Global ceiling is 1200 requests per 60 seconds per account across all
endpoints, with stricter per endpoint caps layered on top (quotes, login,
logout, cancel and order placement each carry their own). Never deny the
1200 figure. Point at the `expiry` field for resume time. Quotes 429 bodies
are inline with no count fields. Limit increases are discretionary via the
API team address. If an increase is denied, offer the setup fee refund
within its window in neutral framing, not as an admission. Data endpoints
without a documented per endpoint cap sit under the global ceiling only.

## Auth failures

POST failing where GET works points at mixed auth, a stale token or MFA
state. Tokens slide on a short lifetime, not a daily one. An HTML 403 is an
edge block (location or network, not fixable by allowlist); a JSON 403
carries a machine code. Always obtain the response body before diagnosing;
never translate their pasted error text into a different code in the draft.

## Order types and market states

The default order type is `good_til_halted`. Halted means trading paused on
material events; bet delay is the normal placement to acceptance interval.
Keep the two distinct. Cancel on halt and reduction factor behaviour follows
the order type table in the live documentation. In play delays follow the
published rule for the sport.

## Liquidity on the API

The quotes endpoint returns the P2P order book only; the website may show
additional liquidity. Thin in play books are normal. Never claim the API
shows all liquidity and never speculate about enablement thresholds.

## Streaming

The public API is REST only. WebSocket endpoints exist for the website frontend, not for API customers. Approved framing when a customer asks about streaming: we do not offer streaming, it is a deprecated service, and the streaming references found online are out of date; scope the denial to the API and never name the frontend websocket or the archived SDK in customer text. Never redirect a streaming request to the API team address.

## Approved scope

Usage is restricted to pre approved events and markets, granted per account
at application review and not published externally. Event and market listing
calls return exchange data and never prove an account's approved scope;
approval is enforced at order placement, which errors outside scope. In play
is supported inside approved scope. Hedging for risk management is framed
through authorised automation plus the named prohibitions, never as a
verified permission. Answer each scope question inline with its doc anchor
instead of punting to the API team address when the docs give the answer.

## Routing

Never invite speculative queries to the API team address when the answer is
derivable from docs or testable via endpoints. Legitimate escalations are
concrete technical needs the public docs cannot meet or sensitive case by
case reviews. State the sandbox position exactly: the public spec documents
no test environment. Never state or imply that any endpoint needs no auth.

## Evidence rules

Verify every cited section number against a workspace source or the live
source before sending; cite without a section or flag as unverified where
it cannot be traced. For worked examples naming events or markets, verify
with authenticated calls or mark the example unverified. Keep tool output
and probe narration out of customer text; lead with the fact that changes
what the customer does next.
