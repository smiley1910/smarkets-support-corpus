# 2026-10-13 — Pro tier / streaming / sandbox / market maker ticket: council brief

Three independent reviewers verify ONE customer-facing Smarkets API support draft
before it is presented to Michael. The brief is a map, not gospel: re-verify its
claims against primary sources and report disagreement explicitly. Do not rewrite
the draft wholesale; list minimal, specific fixes with exact wording.

Draft under review:
`/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-13-pro-tier-data-side-draft-v1.txt`

## Customer message (verbatim)

"Thanks for moving my account to the Pro tier. I trade on Smarkets through the
API, mainly UK horse and greyhound racing, with some football and tennis, and
I'd like to make the most of what Pro offers on the data side.
At present I read prices by polling the quotes endpoint, batching markets into
each request to stay within the 50 requests-a-minute limit. That gives me a
refresh roughly every two seconds, and in racing's final minutes a lot of
prices have moved on by the time I see them.
Could you tell me what API access comes with the Pro tier, in particular
whether a streaming price feed (WebSocket or similar) is included? If it is:
1. How do I enable it on my account, and is there any extra cost?
2. Which markets does it cover, specifically UK and Irish racing win and
place markets, and football and tennis match odds, both pre-match and in play?
3. Does it carry the full depth of the order book, or the best prices only?
4. What are the connection and subscription limits, for example how many
markets at once?
5. Is there any documentation or a sandbox I could test against first?
If streaming isn't part of Pro, could the quotes rate limit be raised for my
account? A higher limit would let me refresh active racing markets more often.
I'd also welcome any information on market-maker or liquidity-provider
arrangements for Pro customers, as I'm considering placing more resting orders
in the morning racing markets."

## Precedents (approved wording, do not contradict)

- A. `responses/2026-10-12-streaming-api-deprecated-FINAL.txt` (approved): "There
  isn't a streaming API for market prices. We don't offer streaming, as it's a
  deprecated service, and the streaming references you've found online are out of
  date. The API is REST only, so it has no websocket interface to connect to..."
- B. `responses/2026-10-12-quotes-batching-increase-FINAL.txt` (approved): batch
  advice (200 ids per call) leads; then "We are unable to review quote limit
  increases at this time. Once you've built a larger sample size of activity, we
  can review and request this for you."
- C. `responses/2026-09-24-websocket-volume-draft-v3.txt`: "There are no
  subscription levels or upgrades that unlock streaming."
- D. `responses/2026-09-23-presales-role2-adversarial-customer.md` fix 7: market
  maker decline must be the flat per-account line ("The Market Maker commission
  tier isn't available for your account"), must NOT mention Sweden or any
  percentage, and must pair with the Pro statement ("The Pro tier removes the
  1,500 bet and £1m staked monthly limits"). Fix 4: Pro must carry the
  loss-charging mechanic when described.
- E. Michael's standing edit rules (from the 30 Sep ticket, restated in the
  2026-10-12 council brief): no showy aggregate totals; advice must add value,
  not mirror the customer; no dates or thresholds on the increase recovery path;
  do not recite all six rate limits.

## Verified facts (re-verify against sources; parent-verified 2026-10-13)

1. Live OpenAPI spec (fetched TODAY, scratch copy
   `/Users/michaelsmyth1/.hermes/cache/scratch/live_spec_20261013.json`):
   quotes `GET /v3/markets/{market_ids}/quotes/` documents "Maximum 50 requests
   per 60 seconds" and "The rate limits below are applicable to API users. The
   rate limits for non-API users are lower."; path param "Market IDs to filter
   by<br>maxItems:200"; global info text "All API users are subject to a default
   rate limit of 1200 requests per 60 seconds across all endpoints, applied per
   account." ZERO occurrences of websocket / wss / streaming / socket / push /
   sandbox anywhere in the spec.
2. Batch size 200 live-verified earlier: 2026-09-30 unauth + authenticated probes
   (200 ids -> HTTP 200), 2026-10-01 batch boundary (n=200 OK, n=201 404 NOT_FOUND)
   in `responses/2026-10-01-batch-boundary/`.
3. Streaming: internal refs
   `~/.hermes/skills/process/smarkets-api-support/references/deprecated-streaming-api-and-sio-live.md`
   and `.../rate-limit-requests.md`. Denial must be scoped to the API: never name
   the website frontend websocket host or the archived 2011 SDK in customer text;
   never claim no websocket exists anywhere at Smarkets; never reroute a streaming
   request to api@smarkets.com.
4. Pro tier: `~/smarkets-api-support/help-pages/smarkets/en-gb/212654665_Smarkets_commission_FAQ.md`:
   Pro charges "1% ... per each individual matched bet that settles ... either on
   the profit if it wins or the losses if it loses"; opt-in once past 80% of
   "more than 1500 bets or stakes more than £1m in a calendar month"; Select 3%
   separate. Skill ref `commission-tiers-faq.md`: there is no API-specific Pro
   tier; the API T&Cs describe one API product. NOTE: that skill file's tier
   TABLE contradicts the help-centre FAQ on the Pro basis — the help-centre FAQ
   is canonical for customer-facing mechanics.
5. Sandbox/test: no test or sandbox environment is documented (Q5-Q6 evidence
   brief: "The public API specification does not document a test or sandbox
   environment."). Approved precedent line: "...so when you're ready to test
   order placement, you'll be using live funds." Do NOT reuse the old second
   half about public/no-auth endpoints (banned). Paper-trading claims in the
   training guide are stale; do not use.
6. Quotes depth: the response carries the raw peer-to-peer order book (bids and
   offers as price/quantity arrays) — `references/quotes-endpoint-behaviour.md`.
   First-party liquidity is excluded; the website may merge extra liquidity.
   This is internal analysis (field evidence), so customer text stays
   light-touch and must never claim the API shows all liquidity.
7. Docs portal: https://docs.smarkets.com/ (per API T&Cs "How to Apply").
8. In-play betting delay (Rule 8.2.1): not used in the draft; do not add unless
   flagged as a material omission with a concrete reason.

## Hard gates (verbatim; pass/fail each)

- Plain text only; no markdown, no tables, no headers.
- Straight quotes only; no em/en dashes; no hyphenated compound modifiers
  ("peer to peer", "pre match", "in play", "market maker" all unhyphenated).
- UK English; contractions expected.
- Banned: "Unfortunately", "I'm sorry to say", "I understand", "the upside is",
  "furthermore", "additionally", "Please be advised", "I can confirm that",
  "Thanks for the detailed overview", "do not hesitate".
- No spec/schema/OpenAPI wording; no api@smarkets.com reroute; no
  competitor comparisons.
- Streaming denial scoped to the API; never name the frontend websocket or the
  archived SDK; never claim no websocket exists anywhere at Smarkets.
- Never state or imply any endpoint needs no auth / is public.
- No account-state claims: we have not verified this customer's account. The
  draft must not assert facts about their tier, scope, or settings.
- Negative density: count not/no/never/isn't/don't/won't/can't etc.; flag if
  more than 3 in a short email and propose trims that keep material
  restrictions.
- "documented"/"documentation" wording: keep minimal; never "as documented".
- Sign-off exactly "Kind regards," / "[name]" / "Smarkets Support".
- No huge aggregate numbers; no dates or thresholds on the increase recovery
  path; do not recite all six rate limits.
- Every sentence must state a material fact, give the decision, explain a
  reason, or give a next step (four-job test). Early decision is acceptable
  for this info/denial class.

## Reviewer roles and deliverable

- Reviewer 1 — FACT/source: trace every factual claim (streaming absence,
  Pro mechanics and 1% loss-charging, API tiering, 200 ids/call, 50/60s,
  1200/60s shared per account, P2P book caveat, sandbox absence, docs URL,
  market maker line, increase line) to sources; flag inference vs verified;
  check the customer echo is accurate (they said "50 requests-a-minute").
- Reviewer 2 — ADVERSARIAL/recipient + PROCESS: read as the customer; build an
  answer-coverage map (streaming ask, enable/cost, coverage incl. UK/IR racing
  win and place + football/tennis pre match and in play, depth, connection/
  subscription limits, docs/sandbox, increase ask, market maker ask, and the
  "make the most of Pro" premise); flag anything refutable, overreaching, or
  internally leaky (MM internal fact, Sweden, spec wording, SDK/frontend
  names); check advice adds value rather than mirroring; check nothing needs
  account verification we lack.
- Reviewer 3 — VOICE/structure/compliance: check every hard gate; state the
  negative-density count as a number; flag any sentence failing the four-job
  test; confirm one author's voice, consistent register, prose not numbered,
  and that no decision is stacked (§1a: single decision sentences for the
  streaming and market maker positions).

Output contract (structured): role; grade APPROVED or NEEDS REVISION; findings;
mandatory_fixes (minimal exact wording, or empty).
