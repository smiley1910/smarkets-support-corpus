# 2026-10-12 — Streaming API ticket (deprecated service): council brief

Three independent reviewers verify ONE customer-facing Smarkets API support draft
before it is presented to Michael. Each reviewer covers its own layer. The brief is
a map, not gospel: re-verify its claims against primary sources and report
disagreement explicitly. Do not rewrite the draft wholesale; list minimal,
specific fixes with exact suggested wording where useful.

Draft file under review:
`/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-streaming-api-deprecated-draft-v1.txt`

## Customer message (verbatim)

"Thank you for your email and for the approval.
I was just wondering if there is a streaming api for market prices? I'm seeing
conflicting things online, but can only see polling endpoints in the docs."

Context: the customer has just been approved for Smarkets API access. This is a
customer-facing reply, written as a Smarkets support agent for Michael to paste
into the ticketing system.

## Michael's internal instruction (verbatim; he typed "depracted")

"Advise we do not offer streaming, a depracted service"

Meaning: tell the customer we do not offer streaming, and that streaming is a
deprecated service.

## Draft under review (also in the draft file)

```
Hi [name],

There isn't a streaming API for market prices. It's a deprecated service, so we don't offer it, and anything you've found online about one is out of date. The API is REST only, so there's no websocket interface to connect to, and the polling endpoints in our documentation are the current way to get prices.

Price updates come from polling. GET /v3/markets/{market_ids}/quotes/ returns the current prices for the markets you request, within a rate limit of 50 requests per 60 seconds. If you tell me what you're building, I can point you to the endpoints that fit it.

Kind regards,
[name]
Smarkets Support
```

## Verified facts (re-verify; parent-verified on 2026-10-12)

1. Live OpenAPI spec fetched 2026-10-12 by the parent from
   https://api.smarkets.com/v0/control/openapi/?tags=trading_api : 18 paths total;
   ZERO occurrences of websocket / wss / streaming / socket anywhere in the
   document. Quotes endpoint `GET /v3/markets/{market_ids}/quotes/` documents
   "Maximum 50 requests per 60 seconds" applicable to API users (non-API users get
   lower limits). Global limit: 1200 requests per 60 seconds across all endpoints,
   applied per account. Local scratch copy of the fetched spec:
   `/Users/michaelsmyth1/.hermes/cache/scratch/live_spec_streaming_check.json`.
   The local repo spec `~/smarkets-api-support/openapi/smarkets_openapi.json` can
   lag the live one; limits claims must be checked live.
2. Historical streaming service, from
   `~/.hermes/skills/process/smarkets-api-support/references/deprecated-streaming-api-and-sio-live.md`:
   `stream.smarkets.com:3801` protobuf/TCP client (`smk_python_sdk`, archived Jan
   2019); host NXDOMAIN (verified July 2026). Council rule of 2026-09-16: scope
   any denial to the API; NEVER claim no websocket exists anywhere at Smarkets;
   never mention sio-live or the archived SDK in customer-facing text.
3. Precedent sent responses:
   - `~/smarkets-api-support/responses/2026-09-16-websocket-and-ratelimits-v4-FINAL.txt`
     opens: "The API doesn't offer websockets or a streaming feed: it is REST only,
     so there is no websocket interface to connect to, and price updates come from
     polling the documented endpoints."
   - `~/smarkets-api-support/responses/2026-09-24-websocket-volume-draft-v2-FINAL.txt`:
     "The API is REST only. We don't offer websockets or a streaming feed, so there
     is no websocket URL or authentication method for one."
4. Voice/core sources: pinned `~/.hermes/skills/process/smarkets-voice-core/SKILL.md`;
   `~/.hermes/skills/process/smarkets-ticket-writer/SKILL.md` and its
   `references/api-tickets.md` ("Streaming: The public API is REST only. WebSocket
   endpoints exist for the website frontend, not for API customers...").
   Docs root: `~/smarkets-api-support/`.

## Hard gates for the customer text (verbatim; pass/fail each)

- Plain text only; no markdown, no tables, no headers, no decorative formatting.
- Straight quotes only; no curly quotes.
- No em dashes; no hyphenated compound modifiers ("real time", not "real-time");
  exception "in-play".
- UK English; contractions expected (don't, isn't, it's, you've).
- Banned: "Unfortunately", "I'm sorry to say", "I understand", "the upside is",
  "furthermore", "additionally", "Please be advised", "I can confirm that",
  "Should you need further assistance, do not hesitate to reach out".
- Never say spec / schema / OpenAPI to a customer; say "API documentation".
- Do not reroute the customer to api@smarkets.com (we are the API support team).
- Scope any websocket denial to the API; never mention sio-live or the archived
  SDK; never state or imply any endpoint needs no auth / is public.
- Negative density: count of not / no / never / isn't / don't / won't / can't etc.
  Flag if more than 3 in a short email.
- The word "documented" at most once per email (draft uses "documentation" once).
- Sign-off exactly: "Kind regards," / "[name]" / "Smarkets Support".
- Simple API info ticket: early decision is acceptable; every sentence must state
  a material fact, give the decision, explain the reason, or give a next step.

## Accuracy note: the "deprecated service" claim

Michael requires advising that streaming is a deprecated service. The draft's
rendering must be accurate and scoped: current API is REST only; the historical
streaming service is deprecated; references found online are out of date. The
customer may have seen the archived SDK or frontend tooling; the draft must not
name either. "Deprecated" (not "retired"/"discontinued") is the intended word.

## Reviewer roles and deliverable

- Reviewer 1 — FACT/source: trace every factual claim in the draft to a source
  (workspace doc or live spec); flag inference/unverified items; check numbers,
  endpoint paths, and the customer-paraphrase accuracy. Output label per claim.
- Reviewer 2 — ADVERSARIAL/recipient + PROCESS: read as the recipient customer;
  build an answer-coverage map (each point of the customer message vs the exact
  draft line that answers it); list anything refutable, misleading, overreaching,
  or that could be escalated (websocket scope, "deprecated" scope, rate-limit
  applicability to them); attempt to falsify; check process (API platform clear,
  direct response permitted by Michael's instruction, no over-probing, echo of the
  customer's own words).
- Reviewer 3 — VOICE/structure/compliance: check the draft against voice-core
  sections 0-4 and 8 and the hard gates above; state the negative-density count as
  a number; flag any sentence failing the 4-job test; confirm one author's voice,
  no committee seams, sign-off format.

Output contract (structured): role; grade APPROVED or NEEDS REVISION; findings
(list); mandatory_fixes (list; minimal exact wording, or empty).
