# 2026-10-12 — Quotes batching + increase ticket: DELTA verification brief (post-council edits)

Context: draft v1 went through three council reviewers. Two returned NEEDS REVISION
with mandatory fixes; one approved. The main agent applied fixes into draft v2.
This delta round verifies the changes only, plus a full mechanical re-scan.
Verified status does not transfer to edited text until this delta round passes.

Files:
- v1 (original): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-quotes-batching-increase-draft-v1.txt`
- v2 (to verify): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-quotes-batching-increase-draft-v2.txt`
- Council brief (hard gates, sources, context): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-quotes-batching-increase-COUNCIL-BRIEF.md`

Full v2 text:

```
Hi [name],

There isn't a streaming or push price feed for API clients. The streaming service is deprecated, and prices come from polling the REST endpoints.

The quotes endpoint accepts up to 200 market ids per call, and the 50 requests per 60 seconds allowance is shared across any clients or tokens you run. At that batch size, the 1,500 or so markets you want to follow at busy times take eight calls, so a full refresh about every ten seconds fits within the cap when those calls use the full quotes allowance.

We are unable to review quote limit increases at this time. Once you've built a larger sample size of activity, we can review and request this for you.

Kind regards,
[name]
Smarkets Support
```

## The changes applied (v1 -> v2), with the reviewer mandates

1. Customer-figure echo scoped.
   v1: "At that batch size, all 1,500 of your markets come back in eight calls"
   v2: "At that batch size, the 1,500 or so markets you want to follow at busy
   times take eight calls"
   - Reviewer 1 mandate: "Change 'all 1,500 of your markets' to 'the around 1,500
     markets you mention for busy times' to match the customer's hedged
     aspirational wording."
   - Judge whether the replaced wording meets the intent (hedged, aspirational,
     tied to busy times).

2. Refresh figure made conditional.
   v1: "so a full refresh about every ten seconds fits within the 50 requests
   per 60 seconds."
   v2: "so a full refresh about every ten seconds fits within the cap when those
   calls use the full quotes allowance."
   - Reviewer 1 mandate: "...if those calls use the full quotes allowance."
   - Reviewer 2 mandate: "...so in principle a full refresh about every ten
     seconds fits within the 50 requests per 60 seconds, when those requests are
     reserved for quotes."
   - The main agent adopted the conditional clause ("when those calls use the
     full quotes allowance"); "in principle" was not added literally. Judge
     whether the conditional intent of both mandates is met. "the cap" refers
     to the 50 requests per 60 seconds allowance named in the same paragraph.

3. New sentence added to address reviewer 2's shared-quota finding.
   v2 sentence: "The quotes endpoint accepts up to 200 market ids per call, and
   the 50 requests per 60 seconds allowance is shared across any clients or
   tokens you run."
   - Basis: reviewer 2 finding: "Omission of shared quota caveat increases
     refutability... Precedent B carried a shared use caveat and this draft
     drops it." Reviewer 2 did not mandate this change; the main agent added one
     sentence. Verify it is accurate (per-account sharing of the allowance) and
     does not damage voice, rhythm, or the no-huge-numbers gate.

## Your verification requirements

- Read v1 and v2 in full; diff them; confirm ONLY the three items above changed.
- For each change: judge whether it resolves the flagged issue; verify any
  new factual content against sources (council brief links: live spec, rate
  limit references, batch captures); flag any new problem introduced.
- Re-scan v2 in full against the hard gates in the council brief: plain text;
  straight quotes; no em/en dashes; no hyphenated compound modifiers; UK
  English; contractions; banned phrases; no spec/schema/OpenAPI wording; no
  reroute; streaming denial scoped to the API; negative density reported as a
  number; "documented" at most once; sign-off exactly "Kind regards," /
  "[name]" / "Smarkets Support"; no huge aggregate numbers; no dates or
  thresholds on the increase recovery path; four-job test per sentence.
- Answer explicitly: does v2 read as one author's voice with no committee seams
  (the added sentence must not read stitched in)?
- Minimal exact fixes only. Your final answer must be the structured report only.
