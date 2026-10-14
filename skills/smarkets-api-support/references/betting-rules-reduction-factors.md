# Reduction Factors on Accumulators — Customer FAQ Reference

## Articulation Framework — Three Tiers

Use this escalation path depending on how far the customer pushes back. Start at Tier 1. Move to Tier 2 or 3 only if they challenge it.

### Tier 1 — The One-Liner (first reply in chat)

> *"The reduction factor cuts the **odds**, not the stake. One leg's odds drop by 40%, so the total multiplied odds drop by 40%. Same percentage, just bigger absolute numbers because accumulators multiply everything up."*

### Tier 2 — The Analogy (when customer pushes back with "that's unfair")

> *"Think of it like a relay team. If your fastest runner — who was carrying 40% of the team's speed — pulls up injured, the team doesn't get 10% slower. It gets 40% slower. The reduction factor measures how much that runner was contributing to your bet."*

### Tier 3 — The Honest Explanation (when customer genuinely wants to understand)

> *"A 40% reduction factor doesn't mean 'we randomly picked 40%.' It reflects the withdrawn horse's probability share in its race — it had roughly a 40% chance of winning. That probability was carrying that much of your accumulator's value.*
>
> *"When that runner goes, your odds adjust proportionally — the same proportion whether it's a €10 single or a €1,000 accumulator. The percentage is identical. The absolute number just looks scarier because the accumulator multiplied everything up first.*
>
> *"The alternative is voiding the whole bet, which is worse — you lose all the remaining legs too, not just the adjustment on one."*

### The Sticky Rule (for the agent's own understanding)

> **Reduction factors are about *probability share*, not *leg count*.**
>
> The RF% tells you how much of the race's probability that horse was carrying. 1 horse out of 10 ≠ 10% reduction. A horse carrying a 40% RF was the favourite or near it — pulling 40% of the probability weight.

### Quick Script for "But it was just 1 of my 10 picks"

> *"If you backed the same horse at 2.0 in a single and it got scratched, it's still a 40% loss of potential profit. You just don't notice because the absolute number is smaller. The accumulator makes everything bigger — wins *and* adjustments."*

## Quick Answer (Customer-Facing)

> *"The reduction factor doesn't reduce your stake — it reduces the odds of the affected selection. Because accumulator odds multiply together, reducing one leg's odds by 40% reduces the total potential payout by 40%. The same thing happens on a single bet — it just looks less dramatic because the numbers are smaller."*

## What is a Reduction Factor?

When a horse is withdrawn from a race (Smarkets Rule 13.3), all matched bets on remaining horses get their odds adjusted. This is the exchange equivalent of Rule 4 deductions at racecourse bookmakers. Removing a runner changes the probability of each remaining horse winning, so prices must be recalculated.

### Formula

From Smarkets help centre — "What is a reduction factor?":

- **'To win' markets:** `New odds = Old odds × ((100 − reduction factor) / 100)`
- **'To place' markets:** `New potential winnings = Old potential winnings × ((100 − reduction factor) / 100)`

Example: odds of 4.0 with a 40% reduction factor → 4.0 × 0.60 = 2.4. A €10 back bet goes from returning €40 to returning €24.

## How Reduction Factors Affect Accumulators

### Cross-Event Accumulators (Rule 9.5)

**Rule 9.5.2:** *"If a reduction factor is applied to any market in which a selection in the accumulator has been chosen from, the odds of the multiple bet will be reduced in line with this."*

Accumulator odds = product of all individual selection odds. Reducing one leg's odds by X% reduces the total accumulator odds by exactly X%.

**Worked example — 5-leg accumulator, €10 stake:**

| Leg | Original | With 40% RF on Leg 5 |
|-----|----------|---------------------|
| Leg 1 | 2.0 | 2.0 |
| Leg 2 | 3.0 | 3.0 |
| Leg 3 | 1.5 | 1.5 |
| Leg 4 | 2.0 | 2.0 |
| Leg 5 | 4.0 | **2.4** (40% reduction) |

- Original total odds: 2.0 × 3.0 × 1.5 × 2.0 × 4.0 = **72.0** → return €720
- After RF: 2.0 × 3.0 × 1.5 × 2.0 × 2.4 = **43.2** → return **€432**
- Reduction: exactly **40%**

### Bet Builders / Same-Event Multiples (Rule 9.6)

**Rule 9.6.2:** *"In the case of horse racing bet builders, the full bet will be voided should a reduction factor be applied in any market included in the bet."*

Because all selections come from the same race, you can't isolate one leg's odds change — the reduction factor affects the entire probability landscape simultaneously. The entire bet is voided, not reduced.

## Why It Can't Just Void One Leg

Removing a runner from a race changes the probability of every remaining horse winning. If we voided just that leg and kept the rest at full odds, the customer would get an unfair advantage — the remaining selections now have better chances of winning than when the bet was placed.

## SBK vs Smarkets Exchange

| Aspect | Smarkets Exchange | SBK (Sportsbook) |
|--------|------------------|------------------|
| Mechanism | Reduces odds of matched bets, cancels unmatched bets, reopens market | Standard bookmaker Rule 4 equivalent applied to the selection's odds |
| Multiple treatment | Rule 9.5.2 — odds reduced in line with RF | Same principle (same betting rules govern both) |
| Bet builder treatment | Rule 9.6.2 — entire bet voided if RF applied | Same — entire bet voided |

## Mathematical Intuition

The "feels unfair" perception comes from absolute numbers: a €720 accumulator dropping by €288 (40%) looks more painful than a €40 single bet dropping by €16 (also 40%). But the proportional mathematics is identical.

The reduction factor operates on **odds**, not **stake**. In a single bet, odds go from 4.0 to 2.4. In a multi, the affected leg's odds go from 4.0 to 2.4, and because accumulator odds multiply (leg₁ × leg₂ × ... × legₙ), the reduction cascades proportionally through the whole bet.

## SBK Cashout and Reduction Factors — The Post-Cashout Clawback Scenario

### The Scenario

> User places a multi-leg accumulator on SBK. Some legs win. User **cashes out**. After cashout, a non-runner is declared in a race that hasn't run yet, causing a reduction factor. SBK adjusts the cashout downwards. User complains: *"I already cashed out! The bet was settled. Why are you adjusting a closed bet?"*

### Why This Happens Explained

SBK is a **fixed-odds wrapper on the Smarkets exchange**. It doesn't hold its own book — it hedges every bet on the exchange underneath. The cashout is a **provisional buyback of the remaining legs at current market value**, not a final settlement. The legs haven't actually settled (the races haven't run), so SBK's underlying exchange hedge is still live and subject to exchange rules.

**The chain of events:**

| Step | What Happens | Who's Affected |
|------|-------------|---------------|
| 1 | User places 3-leg accumulator on SBK. SBK lays all 3 on the exchange. | SBK = hedged, User = open |
| 2 | Race 1 wins. 2 legs remaining. SBK keeps its exchange hedge on Race 2 & 3. | Both still have open exposure |
| 3 | User cashes out. SBK pays current market value of remaining legs. | User = paid, but exchange has not settled |
| 4 | Non-runner declared in Race 2. Exchange applies reduction factor to all matched bets in that market — **including SBK's hedge**. | SBK's hedge value drops |
| 5 | SBK passes the reduction back to the user's cashout. | User sees retroactive adjustment |

### The Rule That Enables This

**Rule 4.5** (General Smarkets betting rules):

> *"SBK reserves the right to void or resettle markets should new information become available, such as due to disqualification, cheating or rules violations."*

A non-runner declared after cashout = new information. SBK resettles the cashout to reflect the reduction factor the exchange applied to its hedge.

### The One-Line Explanation for Support

> *"Your bet was hedged on the exchange behind the scenes. The exchange applies reduction factors to all positions — including SBK's hedge. When a non-runner was declared, the exchange adjusted the payout on that race, and that adjustment flows back to your cashout because the event hadn't settled yet. Nothing was truly final from the exchange's side until the race ran."*

### Deeper Answer (When the Customer Challenges)

The perceived unfairness is timing: the user cashed out before the non-runner was announced, so it feels like a retroactive punishment. But:

- If the user **hadn't cashed out**, the accumulator would have been adjusted by the RF directly (Rule 9.5.2) — same financial outcome, just less visible.
- SBK's hedge on the exchange **is still live** and subject to RF adjustments regardless of whether the user has a cashout or an open bet.
- SBK cannot absorb the RF loss itself because the exchange enforces it — similar to how matched bets on the exchange itself are adjusted.
- The alternative (SBK voiding the RF on the user side while accepting it on the hedge side) would create an arbitrage: every user would cash out before known non-runners, then claim the full RF-adjusted payout as a free win.

### What the Customer May Say

- *"I cashed out! The bet was finished. Why are you changing it now?"*
- *"The non-runner happened after my cashout. This has nothing to do with me."*
- *"This is theft. You paid me X and now you're taking some back."*
- *"If I'd known there'd be a non-runner, I wouldn't have cashed out."*
- *"On Betfair they don't do this."*
- *"So what's the point of cashout if you can just change it afterwards?"*

## Key Rule Numbers

| Rule | Content |
|------|---------|
| 4.5 | SBK can void/resettle markets if new information emerges (enables cashout RF adjustment) |
| 9.5.1 | Voided selection in an accumulator → odds reduced to account for it |
| 9.5.2 | Reduction factor on any leg → accumulator odds reduced in line |
| 9.6.1 | Bet builders: individual selections treated differently |
| 9.6.2 | Horse racing bet builders → **entirely voided** if RF applied |
| 13.3.1–13.3.9 | Full reduction factor rules for horse racing markets |

> **Note:** Greyhound racing uses a different mechanism (void-and-re-add) on non-runners. See `references/greyhound-non-runner-rules.md` for details and contrast with horse racing RF handling.

## What the Customer May Say

- *"I placed a 5-fold accumulator and one horse was withdrawn. Why did my entire bet drop by 40%?"*
- *"The reduction factor on one leg shouldn't affect the whole accumulator!"*
- *"Why can't you just void that one leg and keep the rest?"*
- *"This is robbery — one horse changed and my whole payout is slashed."*
- *"On Bet365 they handle this differently / better."*
- *"A 40% reduction factor on one race reduced my €720 to €432. How is that fair?"*
- *"Is this a Smarkets rule or an SBK rule? I don't understand why they're different."*
