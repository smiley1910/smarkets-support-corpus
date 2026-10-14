# 2026-10-13 — Pro tier / streaming / sandbox / market maker ticket: DELTA verification brief (post-council edits)

Context: draft v1 went through three council reviewers. Reviewer 1 returned NEEDS
REVISION (1 mandate); Reviewer 2 returned NEEDS REVISION (2 mandates plus
findings); Reviewer 3 APPROVED (negative density 6, all mapped to directly asked
material restrictions). The main agent applied the fixes into draft v2 and added
one closing sentence for Reviewer 2's connection/subscription finding. This delta
round verifies the changes only, plus a full mechanical re-scan. Verified status
does not transfer to edited text until this delta round passes.

Files:
- v1 (original): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-13-pro-tier-data-side-draft-v1.txt`
- v2 (to verify): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-13-pro-tier-data-side-draft-v2.txt`
- Council brief (hard gates, sources, context): `/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-13-pro-tier-data-side-COUNCIL-BRIEF.md`
- Live spec fetched 2026-10-13: `/Users/michaelsmyth1/.hermes/cache/scratch/live_spec_20261013.json`

Full v2 text:

```
Hi [name],

Thanks for laying out how you trade and what you want from the data side. Streaming isn't part of Pro: we don't offer streaming, as it's a deprecated service, and the API is REST only, so it has no websocket interface to connect to. There are no subscription levels or upgrades that unlock one.

The Pro tier and API access are separate: Pro is a commission tier that sets your commission at 1% per matched bet that settles, charged on the profit if the bet wins and on the losses if it loses. Your data and order access come from the API, through the same REST endpoints you use today.

Prices come from polling. The quotes endpoint returns the order book for any market within your approved scope, horse racing win and place, football and tennis, pre match and in play included. Each market comes back with bids and offers at price and quantity rather than a single best price, and as it's the peer to peer book, the website display can include additional liquidity.

Pacing comes from the call allowances rather than a connection or subscription. The quotes endpoint accepts up to 200 market ids per call, and quotes allow 50 requests per 60 seconds for API users, within a default allowance of 1200 requests per 60 seconds across all endpoints, shared across any clients or tokens you run. If any of your batches sit below the 200 market cap, widening them is the most direct way to refresh more often in the final minutes of a race, since fewer calls per sweep means more sweeps from the same allowance.

We are unable to review quote limit increases at this time. Once you've built a larger sample size of activity, we can review and request this for you.

The API reference is at docs.smarkets.com. There is no test or sandbox environment, so when you test order placement you'll be using live funds.

On market maker and liquidity provider arrangements, the Market Maker commission tier isn't available for your account. The Pro tier removes the 1,500 bet and £1m staked monthly limits, and resting orders in the morning racing markets go through the standard order endpoints.

Kind regards,
[name]
Smarkets Support
```

## The changes applied (v1 -> v2), with the reviewer mandates

1. Websocket denial scoped to the API.
   v1: "and the API is REST only, so there is no websocket interface to connect to."
   v2: "and the API is REST only, so it has no websocket interface to connect to."
   - Reviewer 2 mandate: scope as "it has no" so a trader who knows the website
     frontend uses a websocket cannot read the denial as global; matches approved
     precedent A verbatim ("The API is REST only, so it has no websocket interface
     to connect to").
   - Judge whether the replaced wording meets the intent.

2. Coverage example narrowed to the documented place market type.
   v1: "racing win and place"
   v2: "horse racing win and place"
   - Reviewer 1 mandate: horse racing place markets are documented (betting rules
     13.2.1); the greyhound rules file (33_greyhound.md) documents no place market
     type (33.5 only contemplates places), so unqualified "racing win and place"
     risks overclaiming greyhound place markets for a customer who trades
     greyhounds. The umbrella clause "any market within your approved scope" and
     "included" keep the list non-exhaustive.
   - Judge: acceptable, or does the narrowing under-answer the customer's "UK and
     Irish racing win and place" / greyhound flows; propose exact wording only if
     a material gap exists.

3. Global limit no longer asserted as a verified account setting; nesting made explicit.
   v1: "Quotes allow 50 requests per 60 seconds for API users, and your account allows 1200 requests per 60 seconds across all endpoints, shared across any clients or tokens you run."
   v2: "Quotes allow 50 requests per 60 seconds for API users, within a default allowance of 1200 requests per 60 seconds across all endpoints, shared across any clients or tokens you run."
   - Reviewer 2 mandate: "within the default 1200 requests per 60 seconds across
     all endpoints..." to (a) drop the unverified per-account assertion and
     (b) stop the 50 and 1200 figures reading as additive. Main agent adjustment:
     "the default 1200" -> "a default allowance of 1200" for grammar.
   - Judge: (a) does "within a default allowance" encode non-additive nesting;
     (b) is "default" acceptable (live spec: "All API users are subject to a
     default rate limit of 1200 requests per 60 seconds across all endpoints,
     applied per account"); (c) no new factual problem.

4. New opening sentence in the limits paragraph (not a reviewer mandate; added
   to close Reviewer 2's finding that the connection/subscription question was
   only partially answered).
   v2 sentence: "Pacing comes from the call allowances rather than a connection or subscription."
   - Judge: (a) accurate (polling is individual requests; there are no connection
     or subscription limits to work within); (b) does it, together with the
     200-ids-per-call sentence, close the customer's Q4 ("connection and
     subscription limits, for example how many markets at once"); (c) voice
     blend, no new negatives, not a mirror of the customer; (d) if cryptic to a
     trader, propose exact replacement wording.

## Your verification requirements

- Read v1 and v2 in full; diff them; confirm ONLY the four items above changed.
- For each change: judge whether it resolves the flagged issue; verify any new
  factual content against sources; flag any new problem introduced.
- Re-scan v2 in full against the hard gates in the council brief: plain text;
  straight quotes; no em/en dashes; no hyphenated compound modifiers; UK English;
  contractions; banned phrases; no spec/schema/OpenAPI wording; no reroute;
  streaming denial scoped to the API; negative density reported as a number;
  sign-off exactly "Kind regards," / "[name]" / "Smarkets Support"; no huge
  aggregate numbers; no dates or thresholds on the increase recovery path;
  four-job test per sentence; single-decision check.
- Answer explicitly: does v2 read as one author's voice with no committee seams
  (the added sentence and the reworked limits sentence must not read stitched in)?
- Minimal exact fixes only. Your final answer must be the structured report only.

## Reviewer roles

- Reviewer 1 — FACT/source: verify changes 1-4 factually; spot-check that nothing
  else drifted factually in v2.
- Reviewer 2 — ADVERSARIAL/recipient + PROCESS: verify the two mandates resolve
  the satisfaction issues they came from (additive reading; account assertion;
  Q4 closure); check no new refutability in the reworked sentences.
- Reviewer 3 — VOICE/structure/compliance: full mechanical rescan of v2;
  negative-density count as a number; seam check; four-job test on changed
  sentences; single-decision check unchanged.

Output contract (structured): role; grade APPROVED or NEEDS REVISION; findings;
mandatory_fixes (minimal exact wording, or empty).
