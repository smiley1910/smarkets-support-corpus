# Voice Rules — Extended

Detailed voice rules extracted from the main SKILL.md and from real-case learning. The main SKILL.md carries the headline rules; this file carries the operationalisations, worked examples, and the lessons that have come out of specific tickets.

## Negative language: prefer positive framing of refusals

A refusal is a refusal whether you say "we will not" or "the position is" — but the second one reads as professional correspondence and the first reads as a string of "no"s. Customer feedback in real ticket drafting: drafts with multiple "we will not" / "isn't" / "can't" / "won't" / "aren't" feel hostile even when each individual refusal is correct. The fix is to restate the position positively: "the prior credit addressed them" / "the prior credit addressed the overall situation" / "the published terms are what apply" / "the settlement on these bets stands" — and let the absence of an offer carry the decision.

### Heuristic

Before sending any decline, count the negatives in the draft. If there are more than two, rewrite. The full SKILL.md voice rules apply (one apology, no "I understand your frustration", no em-dashes, no hyphens); this heuristic is in addition to those.

### Common patterns to convert

| Negative framing (rewrite) | Positive framing (use) |
|---|---|
| "we will not be making a further credit" | "the prior credit addressed the overall situation" |
| "we will not be topping up the credit" | "the settlement on these bets stands, and the prior goodwill credit addressed them" |
| "the guidance given by a live chat agent isn't a guarantee" | "the guidance given by a live chat agent is the team's view at that time, and the published terms are what apply to settlement" |
| "we can't offer further credit on the back of what a live chat agent said" | (cut entirely; the position above is the answer) |
| "we can't cover this" | "[item] was placed with a different exchange, and a bet on a different exchange is a separate transaction governed by that exchange's terms" |
| "we cannot promise this won't happen again" | "our published terms are the basis for the position above" (or simply omit the paragraph) |
| "we can't make a promise that this won't happen again" | (cut the paragraph; replace with a single line or omit) |
| "I apologise for the inconvenience" (when declining) | (use only once, tied to a specific genuine inconsistency) |

### Worked example (Cerezo Osaka follow-up, 7 Aug 2026)

**Before (8 negatives in 14 lines):**
- "not something the published rules require"
- "does not create an entitlement"
- "we will not be topping up"
- "we will not be making a further credit"
- "isn't a guarantee"
- "can't offer further credit"
- "weren't placed with Smarkets"
- "aren't something we can cover"

**After (0 negatives, same content, same decision):**
> "The prior credit of £799.81 (bet 203590231006015497) was made under rule 4.6 of our general betting rules to correct the post-chat bet in this sequence. The two earlier bets, 203590086076350473 with a £359.87 liability and 203590086253387785 with a £599.79 liability, were settled on the result, and that stands."

The decision is the same. The customer reads the same position. The voice is professional correspondence, not a string of refusals.

## Exact figures, not "around" or "approximately"

When the customer says "around £700" or "approximately £X" for an amount that exists in the account or the prior ticket, use the exact figure. Vague figures from the customer are still exact figures in the account. Copying the customer's hedge is sloppy and is exactly the kind of imprecision that loses customer trust in the position.

### Common cases

- Prior credit amounts — name the exact figure and the credited bet ID
- Bet liabilities — the customer may round, the bet slip does not
- Settlement amounts — name the exact figure, not "around £X"
- Time intervals — "within 24 hours" if the rules say 24, not "about a day"

### Worked example (Cerezo Osaka follow-up)

Customer wrote "The extra 700 or so you already credited me." The actual credit was £799.81. The draft initially said "the prior credit of around £700" — Michael flagged this directly: "stop using the term around 700 - be more to the point with the exact figure." The fix was to use £799.81 and name the credited bet ID (203590231006015497) so the customer can see the prior credit was for a specific bet, not a vague "around £700" gesture.

The exact-figure convention also disambiguates: the customer was conflating the prior credit (£799.81) with the £959.66 (1st-set bets) he was now asking for. Naming the prior credit's bet ID and exact figure made it clear that the prior credit was for the post-chat re-bet, not the pre-chat 1st set.

## "On the X..." opener trap

A draft that opens multiple paragraphs with "On the X..." reads as a checklist and as AI-generated. The skill's general voice rule (no formulaic transitions, no repeated sentence shapes) covers this, but it does not always catch it at draft time. The council catches it on the second pass.

**Heuristic before sending:** if two or more paragraphs open with "On the [noun]...", rewrite the openers. Varied forms:
- "The two specific bets you've asked about..."
- "Regarding the conversation you had with our live chat team..."
- "The lays you placed on a different site..."
- "This is our final position."
- "The same reasoning applies to..."

## Complaints process — the ADR block (pinned gate; this section corrected 2026-10-09)

The pinned rule is `process:smarkets-voice-core` §5, and it is the opposite of an automatic
include. Never proactively offer the complaints route, IBAS, eCOGRA, the MGA or the EU ODR in
a decline. Offer a route only where one of three conditions holds: the customer explicitly
said they want to complain or escalate or named the ADR body; Michael instructed the route for
this case; or this is the final position on a complaint the customer has already filed. A
threat of escalation is not a request, so it neither triggers the route nor blocks it, and we
do not pre-empt it.

Two cases that are often confused:
- Partial grant, where one position is upheld and something is credited: the complaints
  pointer IS included at the end.
- Full grant: the complaints line is ABSENT.

Earlier wording in this file said the block was the default for any decline and was omitted
only on Michael's instruction. That was wrong and contradicted the pinned gate; a drafter
loading this file instead of voice-core §5 would have attached an ADR block to every decline.
If a case appears to need the route and none of the three conditions holds, ask Michael. Do
not assume it.

**If the customer comes back in a follow-up ticket and EXPLICITLY says "I want to complain" or
"I want to take this further,"** route them to the ADR body for their jurisdiction (IBAS in the
UK, eCOGRA outside the UK) at that point. Do not open the door in the first response.

## Pre-credit / post-chat-bet mapping (recurring real-case pattern)

When a customer has multiple bet sets in a sequence (pre-chat, post-chat, different exchange), and one set has already been credited, the drafter must map:
- Each cited bet ID → which set it belongs to
- The prior credit's bet ID and amount → which set it addressed
- The customer's requested credit → which set it targets

If the customer conflates the sets (e.g. "I want credit for all my voided and then unvoided bets"), the drafter's job is to disambiguate in the draft, not to credit all sets. Common approach: name the prior credit's exact bet ID and figure, name the 1st-set bet IDs and figures, and state that the prior credit addressed the 2nd set while the 1st set stands.

**Pitfall:** the drafter may not know which set a particular bet ID belongs to. Flag to Michael for confirmation before sending. The whole email misidentifies both bets if the mapping is swapped.

## Rule attribution: 4.6 (reversal) vs 9.4 (discretion)

A "goodwill gesture" is Rule 9.4 (discretion). A "correction of a void that was applied in error" is Rule 4.6 (reversal of incorrect settlement). These are NOT interchangeable.

- Rule 9.4: "Smarkets reserves the right to use its judgement should an incident that falls outside of these rules occur." Use for discretionary gestures where the rules do not require the action.
- Rule 4.6: "Smarkets reserves the right to reverse the settlement of any market if the market is settled incorrectly in error (technical or human)." Use for corrections of incorrect settlement.

A credit under Rule 4.6 is a correction, not goodwill. A credit under Rule 9.4 is goodwill, not a correction. If a prior credit was framed to the customer as Rule 4.6 reversal, the follow-up must stay consistent. If a prior credit was framed to the customer as "goodwill" but the operative rule was actually 4.6, there is a real risk of the customer pointing out the inconsistency. Verify the original framing before sending the follow-up.

## Loading and using this file

This file is loaded when the main SKILL.md is loaded. It does not need to be loaded separately. The voice rules in the main SKILL.md remain the headline rules; the worked examples and operationalisations here are the in-practice reference for when those rules are not enough.
