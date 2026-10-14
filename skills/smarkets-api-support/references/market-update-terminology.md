# Smarkets "Market Update" Terminology (verified Aug 2026)

Question that produced this: "give me a Smarkets term to allow us to change the wording/update a market with matched money" — help-page/product terminology, NOT API.

## The term: "market update"

Smarkets' own help rules phrase it "the update of the market on Smarkets". Consistent company-wide — the WebSocket/API layer also pushes market metadata changes as a "market update" message type, so product, API, and help docs share the term.

## Verified rule quotes (via Jina reader, help.smarkets.com, Aug 2026)

- **Greyhound rules 33.3** (article 360007024158): *"If a non-runner or reserve runner is declared then all matched bets prior to the update of the market on Smarkets will be void and unmatched bets, including those to be kept in play, will be cancelled."*
- **Horse Racing 13.3.5** (article 209277269): non-runner reduction-factor path — RF ≥2.5% in win markets → matched bets adjusted by factor, unmatched cancelled, market reopened; 13.3.6 same for place markets regardless of RF size.
- **General rules 4.5** (article 212183509): *"SBK reserves the right to void or resettle markets should new information become available, such as due to disqualification, cheating or rules violations."* — the catch-all authority for updating a market that already has matched money.
- **General rules 4.6/4.7**: reverse settlement if settled incorrectly in error (technical or human); balance amendments follow resettlement.

## Finding: no dedicated article for wording-only changes

The help centre only documents market updates in runner-change / void / resettle contexts. For help-page content covering "we corrected the wording on a market with matched money": anchor to existing vocabulary — "market update" as the term, rule 4.5 as the authority for matched bets standing or being voided at Smarkets' discretion. Do not invent new terminology.

## How it was found (search technique)

Zendesk HTML search via Jina with the exact phrase "update of the market" → greyhound rules. Generic queries ("market amended", "incorrect market", "market name changed") return unrelated sports-rules articles — search exact phrases, and decode the base64 `/search/click` redirect URLs to see real article titles (see SKILL.md "Zendesk search discovery").
