# Void and Reinstate — Decline Further Credit After Prior Credit

The fourth variant of the void-reinstate complaint class. Customer has ALREADY received a credit (typically a Rule 4.6 correction of one set of bets in a sequence), and is now asking for credit on a DIFFERENT set of bets that were also voided then settled. The position is decline — no further credit.

## When to Use

- Customer's bet sequence has at least two distinct sets (e.g. pre-chat bets, post-chat re-bets, on a different exchange)
- Smarkets has already credited ONE set under Rule 4.6 (or similar reversal provision)
- Customer is now asking for credit on the OTHER set(s), often conflating the sets
- Customer may threaten escalation (UKGC, IBAS, social media)
- The internal decision is to decline further credit
- The credited set is already resolved; the un-credited set stands as settled

This is the NEGATIVE of `void-reinstate-goodwill-credit-pattern.md`. Where that pattern credits the customer in full or in part, this pattern credits nothing further.

## Real-case mapping (Cerezo Osaka vs Dortmund, 7 Aug 2026)

Three distinct bet sets in the customer's sequence:

- **1st set (pre-chat, the two bet IDs the customer names):**
  - 203590086076350473 — £359.87 liability
  - 203590086253387785 — £599.79 liability
  - Total: £959.66
  - Status: voided then SETTLED ON THE RESULT. Stand as settled. NOT credited.

- **2nd set (post-chat re-bet):**
  - 203590231006015497 — £799.81 liability
  - Status: CORRECTED by the prior credit of £799.81 under Rule 4.6 (reversal of the void).

- **3rd set (different exchange):**
  - Not our transaction. Not in scope.

**Customer's argument:** Chat told me the 1st-set bets would not be unvoided, so I want £959.66 credit on top. Plus I want credit for "all my voided and then unvoided bets." Plus I want assurance it won't happen again. Plus UKGC/IBAS/social media threats.

**Position:** The £799.81 already credited was the Rule 4.6 correction of the 2nd set (the post-chat re-bet). The 1st set (£959.66) was voided then settled on the result and stands. No further credit. The customer's chat agent had a view at the time; settlement is determined by the trading team per the published terms. Lays on a different exchange are governed by that exchange's terms. We do not open the complaints door for him; if he comes back and explicitly complains, we route to IBAS then.

## Verified rule quotes

- **Rule 4.6** (general_rules_1-11.md, line 48): "Smarkets reserves the right to reverse the settlement of any market if the market is settled incorrectly in error (technical or human)."

Rule 4.6 is the operative rule for the prior credit. Do NOT cite Rule 9.4 here — that is the discretion provision for goodwill gestures, and the prior credit was a correction, not a goodwill gesture. The customer may have called it "goodwill" in their follow-up; the original sent response should have framed it as Rule 4.6. If the original response called it "goodwill," there is a real risk of the customer pointing out the inconsistency. Verify the original framing before sending the follow-up; if the original was Rule 4.6, the follow-up is consistent; if the original was "goodwill," consider whether to soften the follow-up framing to avoid contradicting a previously-sent position.

## Argument structure

1. **Situation paragraph (often a single line):** "Thanks for the follow up" or equivalent. No situation recap needed — the customer knows what happened, and a long setup reads as defensive.

2. **The position on the requested credit:** Name the prior credit with the EXACT figure and the credited bet ID (not "around £700" if the figure is £799.81). State which rule it was made under. State what the 1st-set bets did (settled on the result) and that they stand. State the position on the other bets in the sequence (already covered by the prior credit, no further credit). One paragraph, no hedging.

3. **Chat guidance paragraph (if the customer raised chat inconsistency):** "The guidance given by a live chat agent is the team's view at that time, and the published terms are what apply to settlement." One apology if there was genuine inconsistency, tied to the customer's experience not to the chat being wrong. Skill rule: neutral framing of chat guidance — never "incorrect information", "wrong advice", "misinformed" in your own prose.

4. **Different exchange / different transaction paragraph (if the customer placed bets elsewhere):** "The lays you placed on a different site were placed with a different exchange, and a bet on a different exchange is a separate transaction governed by that exchange's terms." Do NOT engage with the customer's claimed loss figure. State the position in one line, move on.

5. **Closing line:** Short, final, no complaints route offered. "That's the position on this." or "This is our final position. Our published terms are the basis for the position above."

## Verified operational facts (do not paraphrase into weaker wording)

- "X was credited under rule 4.6" — Rule 4.6 is the operative provision for a Rule 4.6 correction, not Rule 9.4.
- "X was settled on the result" — use this phrasing, not "stood", "remained", "was upheld as voided" or the customer's "unvoided". The skill's loaded-word rule applies: avoid "unvoided" / "unvoid" / "reinstated" — use "settled on the result" or "the void was reversed under Rule 4.6".
- "A bet on a different exchange is a separate transaction governed by that exchange's terms" — this is the only response to a third-exchange bet; do not engage with the claimed loss.

## Complaints process — the ADR block (pinned gate; corrected 2026-10-09)

The pinned rule is `process:smarkets-voice-core` §5, not an automatic include. Never
proactively offer the complaints route or IBAS/eCOGRA in a decline. Offer it only where the
customer explicitly asked to complain or escalate, where Michael instructed it, or where this
is the final position on a complaint already filed. This pattern (decline further credit after
a prior credit) is a plain decline, so the ADR block is normally ABSENT.

Earlier wording in this file said the block was the default and was omitted only on Michael's
instruction, and told drafters to default to including it when no direction was given. That
was wrong and contradicted the pinned gate.

- If Michael has explicitly decided to open the complaints door for this customer, include the
  block. Otherwise it does not go in.
- The customer's threat of escalation is not a basis for offering the route.
- If the customer comes back in a follow-up ticket and EXPLICITLY says "I want to complain" or
  "I want to take this further," route them to the ADR body for their jurisdiction at that
  point. Do not open the door in the first response.

## Approved final draft (Cerezo Osaka, 7 Aug 2026 — post-iteration)

```
Hi [name],

Thanks for the follow up.

The prior credit of £799.81 (bet 203590231006015497) was made under rule 4.6 of our general betting rules to correct the post-chat bet in this sequence. The two earlier bets, 203590086076350473 with a £359.87 liability and 203590086253387785 with a £599.79 liability, were settled on the result, and that stands.

Regarding the conversation you had with our live chat team, the guidance given by a live chat agent is the team's view at that time, and the published terms are what apply to settlement. The settlement of a market is determined by our trading team based on the event facts and the published terms. I appreciate the inconsistency this has caused, and I am sorry for the frustration.

The lays you placed on a different site were placed with a different exchange, and a bet on a different exchange is a separate transaction governed by that exchange's terms.

That's the position on this.

Kind regards,
[name]
Smarkets Support
```

## Voice lessons from this case

- **Negative language is a first-class issue.** Customers (and Michael) read "we will not be making a further credit" / "isn't a guarantee" / "can't offer further credit" / "aren't something we can cover" as a string of refusals. Restate the position positively — "the prior credit addressed them" / "the prior credit addressed the overall situation" / "the published terms are what apply" — and let the absence of an offer carry the decision. Count negatives in the draft; if there are more than two, rewrite. (Michael flagged this directly: "is there less negative language as a whole?")
- **Vague figures from the customer are still exact figures in the account.** The customer wrote "around £700" but the actual credit was £799.81. Use the exact figure and the credited bet ID. Naming the figure and the ID also disambiguates which bets were credited (often the customer is conflating two sets — the prior credit and the new ask).
- **Avoid the customer's loaded word "unvoided".** Skill rule. Use "settled on the result" / "the void was reversed under Rule 4.6" / "the prior credit was made under Rule 4.6 to correct the post-chat bet" instead.
- **One apology only, tied to genuine inconsistency, not to chat being wrong.** "I appreciate the inconsistency this has caused, and I am sorry for the frustration." Do not say "I apologise for the chat" or "sorry for the wrong advice" — that concedes the chat was substantively wrong, which is not the position.
- **No "we will not be" / "we cannot" / "we won't" stacks.** Restate the position in positive terms. The customer is being declined; they know. The email is the position, not the refusal.
- **No IBAS/eCOGRA block by default for this pattern.** Per Michael's direction. If the customer comes back and explicitly complains, route to IBAS then. We do not open the door.
- **One paragraph per logical job.** Do not stack multiple "On the X..." openers. Each paragraph opens with the subject of the job it does: position, chat guidance, different exchange, closing.

## Pitfalls

- **Conflating the bet sets.** The customer's email often describes the sequence in a way that mixes pre-chat, post-chat, and different-exchange bets. The drafter must map the credited bet ID(s) to which set, and the requested credit to which set, before writing. If a bet ID does not match the set the customer describes, flag it to Michael before drafting — the whole email misidentifies the bets if the mapping is wrong.
- **"Around £X" copying the customer's hedge.** If the customer says "around £700" and the actual figure is £799.81, use £799.81. Copying the customer's hedge is sloppy and is exactly the kind of imprecision that loses customer trust in the position.
- **Citing Rule 9.4 for the prior credit if it was Rule 4.6.** Rule 9.4 is the discretion provision. Rule 4.6 is the reversal provision. If the prior credit was framed as a Rule 4.6 reversal (which is the case for the Cerezo Osaka £799.81), the follow-up must stay consistent.
- **Stacked quotes.** Quote Rule 4.6 once, with the operative clause in full and character-exact, including "(technical or human)". Do not also quote Rules 5.1, 4.7, 9.2 in the same paragraph. The skill v4 lesson: full sentence character-exact with "Smarkets reserves the right to" lead-in, ONE rule per paragraph.
- **"On the X..." openers.** Five in a row was flagged by the council. Vary the openers — "The two specific bets...", "Regarding the conversation...", "The lays you placed on a different site..." — and do not start every paragraph with "On the...".
- **Hyphenated compound modifiers.** "One-time", "post-chat", "pre-chat" if used in customer-facing text — check against the skill's HARD RULE. "Post-chat" appears in internal docs but the customer-facing draft should use the plain form ("the bet you placed after the live chat") not the hyphenated form.
- **Engaging with the threat.** UKGC / IBAS / social media threats are not a basis for the decision. Do not respond to the threat. If the user has decided to omit the IBAS block, the omission is silent and the closing is the position statement.
