# 2026-10-12 — Quotes batching + increase ticket: DELTA-2 brief (owner-requested edit)

Context: v2 passed the three-pass council and delta-1. The owner (Michael) then
reviewed and sent: "although correct, i feel its irresponsible to give this much
load/" — the second paragraph read as advising the customer to run the quotes
endpoint at essentially maximum load (full quotes allowance, refresh every ten
seconds). The max-usage framing must go while the batching value stays. Draft v3
applies that change.

Files:
- v2 (last verified): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-quotes-batching-increase-draft-v2.txt`
- v3 (to verify): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-quotes-batching-increase-draft-v3.txt`
- Council brief (hard gates, sources, context): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-quotes-batching-increase-COUNCIL-BRIEF.md`
- Delta-1 brief: `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-quotes-batching-increase-DELTA-BRIEF.md`

Full v3 text:

```
Hi [name],

There isn't a streaming or push price feed for API clients. The streaming service is deprecated, and prices come from polling the REST endpoints.

The quotes endpoint accepts up to 200 market ids per call, and the 50 requests per 60 seconds allowance is shared across any clients or tokens you run. At that batch size, the 1,500 or so markets you want to follow at busy times take eight calls, which should ease the refresh pressure you describe.

We are unable to review quote limit increases at this time. Once you've built a larger sample size of activity, we can review and request this for you.

Kind regards,
[name]
Smarkets Support
```

## The single change applied (v2 -> v3)

- v2: "At that batch size, the 1,500 or so markets you want to follow at busy
  times take eight calls, so a full refresh about every ten seconds fits within
  the cap when those calls use the full quotes allowance."
- v3: "At that batch size, the 1,500 or so markets you want to follow at busy
  times take eight calls, which should ease the refresh pressure you describe."

Notes for the verifier:

- The council had mandated conditioning the refresh claim; the owner has now
  removed the claim outright. Judge: (a) removal is complete — no dangling
  arithmetic, no load-maximisation implication, no orphaned "so/fits" clause;
  (b) the replacement keeps the batching point (200 ids per call; eight calls
  cover the 1,500) and stays within the standing edit rules (advice adds value;
  no huge aggregate numbers); (c) "should ease the refresh pressure you
  describe" does not promise a cadence, a load level, or anything about the
  increase review; (d) answer coverage still holds for all three asks
  (streaming, batching/throughput, limit increase).
- Confirm ONLY this sentence changed between v2 and v3 (diff them).
- Re-scan v3 in full against the hard gates in the council brief: plain text;
  straight quotes; no em/en dashes; no hyphenated compound modifiers; UK
  English; contractions; banned phrases; no spec/schema/OpenAPI wording; no
  reroute; streaming denial scoped to the API; negative density reported as a
  number; "documented" at most once; sign-off exactly "Kind regards," /
  "[name]" / "Smarkets Support"; no huge aggregate numbers; no dates or
  thresholds on the increase recovery path; four-job test per sentence.
- Answer explicitly: does v3 read as one author's voice with no committee seams?
- Minimal exact fixes only. Your final answer must be the structured report only.
