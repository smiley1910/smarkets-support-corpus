# Complaints and Betting Rule Disputes

Application module of `process:smarkets-ticket-writer`. Universal voice,
structure, length and style gates live in `process:smarkets-voice-core` and
are not restated here. Where a gate applies, this file points to it. If this
file ever seems to contradict voice-core, voice-core wins.

Absorbs (with gate corrections): `void-reinstate-complaint-pattern.md`,
`void-reinstate-goodwill-credit-pattern.md`, `voided-market-reactivation-credits.md`,
`voided-bets-dispute.md`, `partial-grant-goodwill-pattern.md`,
`match-market-complaint-pattern.md`, `reduction-factor-low-odds-pattern.md`,
`stake-display-rounding-pattern.md`, `non-standard-match-format-pattern.md`,
`social-responsibility-duty-of-care-complaint.md`, `diplomatic-decline-patterns.md`,
`decision-led-ticket-writing.md`, the complaints sections of
`ticket-scenarios-and-examples.md`, and the ADR section of
`drafting-pitfalls-from-real-tickets.md`. Originals removed after merge;
verbatim history stays in the skill backup.

## Before drafting any complaint

Run `references/complaint-intake-questionnaire.md` first and return its
output contract, then stop. Build the bet by bet map
(`references/bet-sequence-remedy-mapping.md`) and, for declines, the claim by
claim rebuttal map (`references/customer-claim-rebuttal-map.md`) before
writing customer text. Never merge two customers from the same fixture saga
into one remedy; verify which ticket each follow up belongs to.

## Shape for rule based complaints

Use Review then Reason then Action, with one decision sentence placed last
after the reasoning has done the work (voice-core section 1). Simple
procedural replies with no rule carrying the case may keep decision first.
Never stack two or three decision variants in one ticket. Let the rule quote
carry the case instead of adding emphasis sentences after it.

## The complaints route gate

Voice-core section 5 owns this gate. Plain declines end at the position with
no ADR exit. Partial grants carry the reply to complaints pointer ("If
you would like to take this further, reply to this email and we will go
through the complaints process"). The IBAS or eCOGRA block goes only in a
final position on a filed complaint, when the customer explicitly asks to
escalate, or when Michael instructs it. A threat to go to a regulator or ADR
is not a request and gets no route. Full grants carry no complaints line.

## Rule attribution

Keep Rule 4.6 reversal (void reversed, bet settled on the result) strictly
separate from goodwill credit (discretionary, under Rule 9.4, never
rule mandated). Verify which provision a prior credit was processed under by
reading the original sent response before drafting a follow up. Name one
operative rule per position. Explain how it applies to the facts; quote
wording only where the wording itself is disputed (voice-core section 3).

## Void and reinstate variants (never merge them)

1. Denial: void reinstatement correct, no credit. Cite 4.6 and 9.4. The only
   voids that are permanent by rule are 8.3.5 (Instant Match pending
   confirmation) and 12.4 (3 hour abandonment); cite them only to bound
   permanence claims. Answer Consumer Rights Act claims with the published
   plus accepted limb (1.7, 6.17), the reserved correction powers (6.16,
   4.6, 9.2) and status availability (6.9); state the position without
   spelling out the conclusion for them.
2. Partial grant (customer right): original bet upheld per rules plus rebet
   credited as a single goodwill gesture because it was placed on chat advice
   about a cancelled event. Two limbs kept distinct. Say "good faith"
   literally, label the gesture once, apologise once for the guidance
   inconsistency, include the reply to complaints pointer.
3. Full grant: both limbs credited with exact bet IDs and total, chat
   guidance stated plainly once where authorised, stern going forward note
   (a void may be reversed and settled once a result is determined; do not
   expect the same adjustment again). No complaints line.
4. Decline further credit after prior credit: see
   `references/decline-further-credit-after-prior-credit.md`, which is
   authoritative for this variant. Position is one positive framed decline:
   the published terms apply to all bets in the sequence and the prior credit
   addressed its own set. No proactive route, no promise about recurrence.
5. Uphold both (no chat advice, customer rebet on own initiative): original
   reversed under 4.6 and settled on the result plus second stands. Restating
   the resulting figure with "no refund due" is allowed. One apology only,
   and the opener must be a non apology acknowledgement.

State the chat position neutrally ("the guidance given by a live chat agent
is the team's view at that time, and the published terms are what apply to
settlement"). Never write "incorrect information", "wrong advice" or
"misinformed" in your own prose unless Michael authorises the plain form.
Decline kindly with soft negation ("we are not in a position to") and let
the absence of an offer carry the decision; count negatives and rewrite past
two. Use exact figures with bet IDs, never hedges, when the account gives
them. Never write "reuploaded" or "unvoided"; use "settled on the result".

## Match market (knockout) denial

Rule 12.1: all football match markets settle on 90 minutes including
stoppage time unless stated otherwise. Three pillars: the Draw option
distinguishes the 90 minute market (an overall winner market would have no
Draw), the separate To advance market under 12.5.20 is the market the
customer says they wanted, and Rule 2.1 plus T and Cs section 6 place rule
awareness on the customer. Decision lands last in a single sentence. Do not
lecture about presentation. Assert "no system error" only against verified
event data; otherwise write "settled in line with our published rules".

## Multiple events, one fixture

Rule 4.1 (settlement timing) plus T and Cs 6.24 (customer responsibility for
the intended selection) answer why one match lists several events.

## Golf Bet Builder denial

Rule 9.6.1 (whole multiple voided with stake returned where a selection is
voided or settles as a dead heat, regardless of other selections, including
selections already lost) controls the multiple; Rule 14.3.2 dead heat
provisions apply at single market level and do not prevent the void. Mirror
the customer's term once, name the figures they calculated once without
recalculating them, show the available alternative (standard accumulators
across different events) as flat fact. Decision last, single sentence.

## Reduction factor below 1.00

Rule 13.3.2: the factor is the withdrawn horse's percentage chance, not a
share of matched money. Formula is old odds times (100 minus factor) over
100. Rule 13.3.5: at or above 2.5% matched bets adjust and unmatched cancel.
No published rule states a 1.00 floor; attribute the full stake return to
prior advice, never to a rule. Runner count disputes are answered by the
percentage price fact (field size does not change the maths), sidestepping
unverifiable counts. Check tier before stating any commission mechanics.

## Stake display rounding

Reductions adjust price and payout only, never the stake. The app derives
displayed stake as payout divided by displayed odds with whole number
rounding, which becomes visible at very long odds. Verify the stated
rounding unit reproduces the example figures before drafting. Anchor in one
rule with a lead in. One apology tied to the confusing display only.

## Non standard match format

Rule 12.2 (friendlies settle on the full duration of regular time play
according to the match officials) is the sports specific rule and supersedes
General Rule 6.6 under the preamble. Confirm the fixture type first: if
competitive, 6.6 may genuinely apply and the outcome flips. Answer "every
other bookmaker voided" with T and Cs section 6 (rules vary between
operators).

## Resettlement and negative balances (withdrawal prior to correction)

Rule 4.6 (reversing erroneous settlement) and Rule 4.7 (balance amendments
to reflect corrected settlement) govern markets where an initial result is
revised. Where winnings were already withdrawn before the correction, Rule
5.2 establishes the right to recover funds disbursed in error.

For horse racing disputes, Rule 13.1.1 establishes that initial settlement
on first past the post is subject to the weighed in result as the official
result. Write "weighed in result" without a hyphen ("weighed-in result" is
a hyphenated compound modifier that violates voice-core section 4).

Key handling rules:
- Two distinct limbs: the rule-backed limb (settlement correction and
  balance adjustment under Rules 4.6, 4.7, 5.2, and sport-specific rules
  like 13.1.1) versus any discretionary relief limb (waiver, partial credit,
  or repayment terms under Rule 9.4).
- Cancelled pending withdrawal variant (clearing negative balance): when a
  customer tries to withdraw provisional winnings before resettlement and
  the withdrawal is still pending when the market is resettled, reversing
  the provisional winnings initially triggers a negative balance on the
  account ledger. Subsequently cancelling the pending withdrawal returns
  those funds to the ledger, fully clearing the negative balance to zero.
  Customers frequently contact support during or immediately after the
  resettlement believing they are in debt and being forced to deposit funds.
  In this case, immediately clarify in the opening substantive paragraph
  that the balance is zero and no deposit is required, then explain the
  accounting sequence factually.
- The "withdrawn in good faith" argument: Validate before correcting.
  Acknowledge that the funds were displayed and withdrawn in good faith
  before the correction occurred. Do not accuse, lecture, or moralise about
  withdrawing early. Explain plainly that settlement is governed by the
  official outcome, and the rules specifically provide for balance
  adjustments (Rule 4.7) and recovery of funds disbursed in error (Rule 5.2).
- Single decision: If declining a waiver or goodwill payment, use diplomatic
  refusal framing ("we are not in a position to offer a goodwill payment or
  balance adjustment") so that "The settlement stands." remains the sole
  closing decision sentence at the end. Do not stack blunt negation ("no
  payment will be made. The settlement stands."). Avoid aggressive
  debt-collection language. If discretionary relief is authorised by
  Michael, label it once as a goodwill adjustment under Rule 9.4.

## Social responsibility duty of care

A formal complaint gets acknowledgement, confirmation that internal review is
underway, and the 10 day timeline from T and Cs 16.1. Refund denial cites
13.1 plus 13.5. No apology for the losses, no emotional script. The ADR
block goes in the final response after review, never the first. Never invent
trigger criteria or intervention indicators; never cite clause 2.1 for
gambling responsibility; never fold affordability or source checks into
section 11. Use account facts only as Michael supplies them.
