# 2026-10-12 — Streaming API ticket: DELTA verification brief (post-council edits)

Context: draft v1 went through three council reviewers. Two returned NEEDS REVISION
with specific mandatory fixes; one approved. The main agent applied the fixes into
draft v2. This delta round verifies the changes only, plus a full mechanical
re-scan. Per the reconciliation rule, verified status does not transfer to edited
text until this delta round passes.

Files:
- v1 (original): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-streaming-api-deprecated-draft-v1.txt`
- v2 (to verify): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-streaming-api-deprecated-draft-v2.txt`
- Full council brief (hard gates, sources, context): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-12-streaming-api-deprecated-COUNCIL-BRIEF.md`
- Draft file under v2:

```
Hi [name],

There isn't a streaming API for market prices. We don't offer streaming, as it's a deprecated service, and the streaming references you've found online are out of date. The API is REST only, so it has no websocket interface to connect to, and the polling endpoints in our documentation are the current way to get prices.

Price updates come from polling. GET /v3/markets/{market_ids}/quotes/ returns the current prices for the markets you request, within a rate limit of 50 requests per 60 seconds for API users. If you tell me what you're building, I can point you to the endpoints that fit it.

Kind regards,
[name]
Smarkets Support
```

## The three changes applied (v1 -> v2), with the reviewer mandates

1. Paragraph 1, sentence 2.
   v1: "It's a deprecated service, so we don't offer it, and anything you've found
   online about one is out of date."
   v2: "We don't offer streaming, as it's a deprecated service, and the streaming
   references you've found online are out of date."
   - Reviewer 2 mandate: replace "It is a deprecated service, so we do not offer
     it," with "We do not offer it; it is a deprecated service," (rationale:
     decision should lead; do not order history before decision).
   - Reviewer 1 mandate: scope the online-material sentence; preferred minimal
     fix: "and the streaming references you've found online are out of date."
   - Note: reviewer 2 proposed "any streaming references you have found online";
     reviewer 1 proposed "the streaming references you've found online". The main
     agent adopted reviewer 1's preferred wording. Judge whether the intent
     (scope the claim to streaming references, not "anything") is met.

2. Paragraph 1, sentence 3 (websocket clause).
   v1: "The API is REST only, so there's no websocket interface to connect to,"
   v2: "The API is REST only, so it has no websocket interface to connect to,"
   - Reviewer 2 mandate: replace "so there is no websocket interface to connect
     to," with "so there is no websocket interface to connect to in the API,"
     (rationale: the bare clause could be read as a global no-websocket claim;
     it must be unmistakably API-scoped, because a website-frontend websocket
     exists and must not be refutable).
   - The main agent tightened scope to the API via subject plus pronoun ("it" =
     The API). Judge whether this resolves the mandate's intent; if a reader
     could still read the clause as global, say so.

3. Paragraph 2, rate limit.
   v1: "within a rate limit of 50 requests per 60 seconds."
   v2: "within a rate limit of 50 requests per 60 seconds for API users."
   - Reviewer 1 mandate: add the scope qualifier (live spec: these limits are
     "applicable to API users").

## Your verification requirements

- Read v1 and v2 in full; diff them; confirm ONLY the three items above changed.
- For each change: state whether it resolves the flagged issue, verify the new
  wording against the sources (live spec, streaming reference, voice-core, all
  linked from the council brief), and flag any new factual or voice problem it
  introduced.
- Re-scan v2 in full against the hard gates listed in the council brief: plain
  text; straight quotes; no em/en dashes; no hyphenated compound modifiers; UK
  English with contractions; banned phrases; no spec/schema/OpenAPI wording; no
  api@smarkets.com reroute; websocket denial scoped to the API; negative-density
  count reported as a number; "documented" at most once; sign-off exactly
  "Kind regards," / "[name]" / "Smarkets Support"; early decision acceptable for
  this simple API info ticket; four-job test.
- Answer explicitly: does v2 read as one author's voice with no committee seams?
- Do not rewrite wholesale; minimal exact fixes only. Your final answer must be
  the structured report only.
