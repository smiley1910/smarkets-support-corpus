# 2026-10-13 — Lee / SBK extra cash-outs: refund email — council brief

Three independent reviewers verify ONE customer-facing SBK support draft before it
is presented to Michael. The brief is a map, not gospel: re-verify its claims
against primary sources and report disagreement explicitly. Do not rewrite the
draft wholesale; list minimal, specific fixes with exact wording.

Draft under review:
`/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-13-lee-cashout-refund-draft-v1.txt`

## What this email is

Follow-up resolution for an SBK customer ("Lee"). He previously raised confusing
balance changes around his Arsenal bets on 10 October; support explained the
mechanics. Michael has now reviewed the product behaviour and decided: as an SBK
customer, he should have had three back bets and three cash outs only, no
further; the four extra cash outs acted as extra hedges that ate away his peak
profit illogically; he is due £118.29. This email explains, apologises, and
returns the £118.29. It is a new resolution email (stand-alone clarity), not an
edit of the earlier explanation.

## Michael's instruction (verbatim)

"so as they are SBK, they should have had 3 back bets, and 3 cash outs, no
further, the 4 extra acted almost like hedges that ate away peak profit
illogically, I calculate they are due 118.29 which was hedged out of their peak
profit, does the math make sense, can you audit and ensure this is correct then
draft an email explaining and apologising for the issue"

## Case facts (statement-derived; verified in the 11 Oct session)

Customer: Lee (SBK). Event: Arsenal vs Leeds United, Full-time result, settled
10 October 2026. Times below are UTC (statement) = local +1 (customer-visible
emails use the local times, no BST/UTC labels).

The three back bets (full IDs supplied by Michael):
- 203616290557276169 — £30 back Arsenal @ 4.4, placed 12:47:16 UTC (13:47 local)
- 203616290594029577 — £30 back Arsenal @ 4.5, placed 12:47:25 UTC
- 203616290622816265 — £30 back Arsenal @ 4.5, placed 12:47:32 UTC
    (statement shows these as "Bet Won (winner) – For Arsenal")

First three cash outs (closing the three backs; IDs truncated in the statement
as 2.0361629…E+17): matched 13:00:53, 13:00:58, 13:01:03 UTC
(14:00:53–14:01:03 local). Counter positions of 103.85 @ 1.30, 103.85 @ 1.30,
102.31 @ 1.29; reserved 31.16, 31.16, 29.67 (sum £91.99).

Four further cash outs (the disputed ones): placed 13:01:51, 13:01:54, 13:01:57,
13:02:34 UTC; matched 13:02:02, 13:02:04, 13:02:06, 13:02:38 UTC (local
14:01:51–14:02:38). Counter positions of 105.47 @ 1.28, 105.47 @ 1.28,
102.31 @ 1.29, 105.47 @ 1.28; reserved 29.54, 29.54, 29.67, 29.54
(sum £118.29).

Account figures (statement):
- Settled balance flat at £133.01 through the bets; moving position value
  −123.00 → 187.02 (after the three cash outs) → 68.73 (after the four further
  cash outs, via −29.54, −29.54, −29.67, −29.54).
- £200.00 withdrawal 13:20:57 UTC (14:20 local): settled balance −£66.99.
- Settlement 13:25:05 UTC (14:25 local): net +£101.73 credited → £34.74 final.

## Audit of the £118.29 (parent-verified; reviewers must recompute independently)

1. 133.01 + 187.02 = 320.03 (peak available; matches statement arithmetic).
2. 320.03 − 118.29 = 201.74 (the drop the customer saw).
3. Four further cash outs' reservations: 29.54+29.54+29.67+29.54 = 118.29.
4. Net market result: three backs win +312.00 (105+105+102); all seven counter
   positions lose 91.99+118.29 = 210.28 → net +101.72 ≈ statement +101.73.
   Without the four: net +220.01.
5. Counterfactual final balance: 34.74 + 118.29 = 153.03; cross-check
   133.01 + 220.02 − 200 = 153.03. Both routes give the same £118.29 make-good
   (allow ≤1p rounding noise from truncated statement figures).

Conclusion: £118.29 is exactly what the four further cash outs cost, on both the
peak-available measure and the end-state measure. Michael's figure is confirmed.

## Prior approved customer text (11 Oct session; must stay consistent on figures/times/terms)

"...After your first three cash outs at 14:01 your available balance was
£320.03. Between 14:01 and 14:02 four further cash outs were placed. Once the
first cash outs had secured that value, each further cash out traded part of it
away. As Arsenal went on to win, these reduced your available balance by
£118.29, from £320.03 to £201.74..."

## SBK help-centre grounding (help.getsbk.com article "Cash out on SBK")

- "Cashing out is the same thing as betting on the opposite outcome to happen.
  So when you cash out, the app will immediately place a counter bet to the one
  you placed originally."
- "When you cash out of your bet, you will receive the cash out amount offered
  immediately."
- (Accumulator section) "Do not constantly tap the cash out button, as this may
  cause the feature to lag and place the offer without your confirmation, or
  even cash out of the same bet twice."
NOTE: this customer is SBK. Do not use lay/hedge/exchange/matched terminology in
customer text; cash outs are cash outs. "Counter bet" is public help-centre
language but the draft deliberately avoids it.

## Draft v1 under review

```
Hi Lee,

Thank you for raising the cash outs on your Arsenal bets from 10 October.

I have reviewed the full sequence. Once your three £30 bets on Arsenal had been cashed out in full at 14:01, there was nothing left to cash out. The four further cash outs between 14:01 and 14:02 went beyond your bets and traded away part of the £320.03 you had secured, reducing your available balance to £201.74. Those further cash outs should not have been possible, and I am sorry that this happened.

I am returning the £118.29 that the further cash outs took from your balance. You will see it added to your account.

If you have any questions about this, just reply here.

Kind regards,
Michael
Smarkets Support
```

## Hard gates (voice-core; pass/fail each)

- Plain text only; no markdown, no tables, no headers.
- Straight quotes only; no em/en dashes; no hyphenated compound modifiers
  ("cash outs" spaced, "Full-time" not used in draft; "14:01" fine).
- UK English; contractions where natural.
- Banned: "Unfortunately", "I'm sorry to say", "I understand", "the upside is",
  "furthermore", "additionally", "Please be advised", "I can confirm that",
  "do not hesitate", "Thanks for the detailed overview".
- Exact figures only (no "around/about £118"); times in local, no UTC/BST labels.
- Exactly one apology, tied to the specific issue ("should not have been
  possible"); one decision sentence ("I am returning the £118.29 ..."); no
  stacked decisions; no promises beyond the £118.29 (no systemic guarantees, no
  dates beyond what is written).
- Complaints pointer: treated as full grant of the remedy → pointer ABSENT per
  voice-core §5. Reviewer 2 to validate this classification.
- No lay/hedge/exchange/matched jargon; no spec/internal leakage; no naming
  colleagues; sign-off exactly "Kind regards," / "Michael" / "Smarkets Support".
- Four-job test per sentence; negative density reported as a number.

## Reviewer roles and deliverable

- Reviewer 1 — FACT/AUDIT: recompute every figure above from the raw numbers
  (do not trust the brief's sums); verify the draft's claims and figures against
  the case facts (times and amounts); confirm the £118.29 figure under both
  measures; flag any inference vs verified (the "should not have been possible"
  claim is Michael-directed — check the draft states it as fact consistent with
  his instruction, not softened or over-extended).
- Reviewer 2 — ADVERSARIAL/recipient + PROCESS: read as the customer. Does the
  email (a) explain the issue clearly, (b) apologise appropriately without
  grovelling, (c) state the remedy with exact amount and destination, (d) avoid
  new refutability or overpromise, (e) avoid lay/hedge jargon, (f) work as a
  stand-alone email (assume he may only read this one)? Check the complaints
  pointer gate classification and flag any missing element that a sharp customer
  would immediately ask about.
- Reviewer 3 — VOICE/structure/compliance: full mechanical scan; negative
  density count as a number; four-job test; single-decision and one-apology
  checks; register consistency with Michael's prior emails in this case.

Output contract (structured): role; grade APPROVED or NEEDS REVISION; findings;
mandatory_fixes (minimal exact wording, or empty).
