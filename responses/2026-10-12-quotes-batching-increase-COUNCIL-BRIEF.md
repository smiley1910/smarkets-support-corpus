# 2026-10-12 — Quotes batching + limit increase ticket: council brief

Three independent reviewers verify ONE customer-facing Smarkets API support draft
before it is presented to Michael. The brief is a map, not gospel: re-verify its
claims against primary sources and report disagreement explicitly. Do not rewrite
the draft wholesale; list minimal, specific fixes with exact wording.

Draft under review:
`/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-quotes-batching-increase-draft-v1.txt`

## Customer message (verbatim)

"I've been trading through the API since September, automated pre-match trading
across football and basketball. Over the last 30 days that's around 590 bets
and £8,000 staked, and I'm scaling stakes and markets up over the coming
weeks.
Ideally I'd like access to a streaming or push price feed, if one exists for
API clients. Polling is the real limit on what I can do: with the quotes
endpoint at 50 calls a minute I can follow about 600 markets at a useful
refresh rate, and at busy times I'd like to follow around 1,500. A streaming
feed would let me follow all of them and put a lot more volume through your
book.
If streaming isn't available, could the quotes rate limit on my account be
raised instead, ideally to 200 calls a minute?
Happy to share more detail on volumes or usage if it helps."

## Michael's instruction (verbatim)

"next one / very similar / lets suggest batching if it doesnt look like hes doing it"

Reading: this is the second ticket today in the same class (streaming ask plus
limits). The previous ticket's approved position applies (no streaming, a
deprecated service, polling only). On this one Michael adds: suggest batching
(200 market ids per quotes call) because the customer's numbers suggest he is not
batched up to the endpoint limit. The increase request is answered with the
standing position used in the 30 Sep precedent below.

## Draft under review (also in the draft file)

```
Hi [name],

There isn't a streaming or push price feed for API clients. The streaming service is deprecated, and prices come from polling the REST endpoints.

The quotes endpoint accepts up to 200 market ids per call. At that batch size, all 1,500 of your markets come back in eight calls, so a full refresh about every ten seconds fits within the 50 requests per 60 seconds.

We are unable to review quote limit increases at this time. Once you've built a larger sample size of activity, we can review and request this for you.

Kind regards,
[name]
Smarkets Support
```

## Precedent A — today's earlier ticket (same class; council + delta approved)

File `2026-10-12-streaming-api-deprecated-FINAL.txt`. Opening paragraph:

"There isn't a streaming API for market prices. We don't offer streaming, as
it's a deprecated service, and the streaming references you've found online are
out of date. The API is REST only, so it has no websocket interface to connect
to, and the polling endpoints in our documentation are the current way to get
prices."

## Precedent B — 30 Sep same-scenario ticket (Peter; Michael edited by hand)

Final approved wording he kept:

"Doubling your quotes batch from 100 to 200 markets per call doubles what you
pull without extra requests. Quotes allow 50 requests per 60 seconds, and your
account allows 1200 requests per 60 seconds across all endpoints, shared across
any workers or tokens you run. That extra headroom should ease the refresh
pressure you've described during racing hours.
...
Quotes are served over REST, so polling remains the method and a push feed sits
outside what we offer to API customers. We are unable to review quote limit
increases at this time, once you've built a larger sample size of activity we
can review and request this for you."

Michael's standing edit rules from that session:

1. "ok but lets not make the 10k claim lets just give the batch advise without
   such huge numbers" — no showy aggregate throughput totals ("10,000 markets
   per minute" was cut). Small, directly actionable figures only.
2. "i just want to ensure we're not mirroring them and giving helpful advice" —
   the reply must add new value beyond what the customer said, not echo him.
3. No date promises: a polished variant that added "request this again in 90
   days" was rejected; the recovery path stays conditional on a larger sample
   size of activity, with no date.
4. Do not recite all six rate limits; lead with the batch advice that changes
   what the customer does.
5. The increase line's wording ("unable to review ... at this time, once you've
   built a larger sample size of activity we can review and request this for
   you") is Michael's own approved customer-facing wording. Do not add dates,
   thresholds, or stronger promises. INTERNAL (must never appear in customer
   text): increases need a market maker level participant internally, which no
   regular user realistically reaches; the recovery path is deliberately
   soft-spoken and must stay exactly this vague.

## Verified facts (re-verify; parent-verified 2026-10-12)

1. Live OpenAPI spec (fetched 2026-10-12; scratch copy
   `/Users/michaelsmyth1/.hermes/cache/scratch/live_spec_streaming_check.json`):
   quotes `GET /v3/markets/{market_ids}/quotes/` documents "Market IDs to filter
   by<br>maxItems:200" and "Maximum 50 requests per 60 seconds" for API users;
   global "default rate limit of 1200 requests per 60 seconds across all
   endpoints, applied per account". ZERO occurrences of websocket / wss /
   streaming / socket / push anywhere in the spec.
2. Batch size 200 live-verified by the parent workflow: 2026-09-30 unauth probe
   (200 ids -> HTTP 200; X-RateLimit-Limit 20) and authenticated probe on the
   test account (200 ids -> HTTP 200; Limit 50; logout clean). 2026-10-01 batch
   boundary: n=200 -> 200 OK, n=201 -> 404 NOT_FOUND. Captures in
   `responses/2026-10-01-batch-boundary/`.
3. Arithmetic (checked in the parent): ceil(1500/200) = 8 calls per full sweep;
   50/8 = 6.25 sweeps per minute; 60/6.25 = 9.6 s per sweep, i.e. "about every
   ten seconds". For reference: batch 100 -> 15 calls, one sweep per 18 s; batch
   50 -> 30 calls, one sweep per 36 s.
4. Streaming: internal reference
   `~/.hermes/skills/process/smarkets-api-support/references/deprecated-streaming-api-and-sio-live.md`
   (stream.smarkets.com:3801 deprecated, SDK archived; scope denials to the API;
   never name sio-live or the archived SDK in customer text).
5. Voice/core sources: pinned `~/.hermes/skills/process/smarkets-voice-core/SKILL.md`;
   `~/.hermes/skills/process/smarkets-ticket-writer/SKILL.md` and
   `references/api-tickets.md` (Streaming section). Docs root
   `~/smarkets-api-support/`.

## Hard gates (verbatim; pass/fail each)

- Plain text only; no markdown, no tables, no headers.
- Straight quotes only; no em/en dashes; no hyphenated compound modifiers.
- UK English; contractions expected.
- Banned: "Unfortunately", "I'm sorry to say", "I understand", "the upside is",
  "furthermore", "additionally", "Please be advised", "I can confirm that".
- No spec/schema/OpenAPI wording; no api@smarkets.com reroute.
- Streaming denial scoped to the API; never name sio-live or the archived SDK.
- Negative density: count not/no/never/isn't/don't/won't/can't etc.; flag if
  more than 3 in a short email.
- "documented" at most once per email.
- Sign-off exactly "Kind regards," / "[name]" / "Smarkets Support".
- No huge aggregate numbers (standing edit rule 1 above).
- No dates or thresholds on the increase recovery path (standing edit rule 3).
- Early decision acceptable for this info/denial class; every sentence must
  state a material fact, give the decision, explain a reason, or give a next
  step.

## Reviewer roles and deliverable

- Reviewer 1 — FACT/source: trace every factual claim (200 ids/call, 50/60s,
  8 calls, ten seconds, deprecated service, streaming absence) to sources;
  recompute the arithmetic yourself; check the customer echo is accurate; flag
  inference vs verified.
- Reviewer 2 — ADVERSARIAL/recipient + PROCESS: read as the customer; build an
  answer-coverage map (streaming ask, increase ask, "happy to share detail");
  flag anything refutable or overreaching (esp. the ten-second refresh claim,
  "deprecated", the recovery-path line); check process (no over-probing, no
  mirroring, advice adds value, no internal leakage such as MM level).
- Reviewer 3 — VOICE/structure/compliance: check every hard gate; state the
  negative-density count as a number; flag any sentence failing the four-job
  test; confirm one author's voice and consistent register.

Output contract (structured): role; grade APPROVED or NEEDS REVISION; findings;
mandatory_fixes (minimal exact wording, or empty).
