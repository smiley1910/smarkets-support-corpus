# Greyhound Racing — Non-Runner Handling (Void & Re-Add)

## The Mechanism

For greyhound racing, when a non-runner (trap withdrawal) is declared, the approach differs from horse racing:

| Sport | Non-Runner Handling | Mechanism |
|-------|-------------------|-----------|
| **Horse racing** | Reduction Factor (Rule 13.3) | Odds adjusted on existing matched bets; market stays open |
| **Greyhound racing** | Void & Re-Add | Entire event voided, then re-added with corrected runner list |

## Why Greyhounds Are Different

- **Smaller fields** — typically 6 dogs vs ~10-20 horses. Removing one runner has a much larger proportional impact on the probability landscape
- **Trap draw matters** — specific trap positions affect running dynamics in ways that don't have a direct horse racing equivalent
- **Runner list volatility** — greyhound withdrawals can happen closer to the off, making the cleanest handling to reset the market entirely

## What Happens in Practice

1. Non-runner is declared (trap withdrawn)
2. All existing matched bets on that event are **voided** — stakes returned
3. The event/market is removed from the active lineup
4. A new event is created/re-added with the corrected runner list (usually 5 dogs instead of 6)
5. Customers must re-enter their bets on the new market

## Customer-Facing Explanation

> *"Greyhound racing handles non-runners differently from horse racing. Because the field is smaller (typically 6 dogs), a withdrawal changes the race dynamics significantly. Rather than applying an odds adjustment, the entire event is voided and re-added with the corrected runner list. Your stake is returned and you can place bets on the updated market."*

## How This Differs from Horse Racing (RF) Approach

| Aspect | Horse Racing (Reduction Factor) | Greyhound Racing (Void & Re-Add) |
|--------|-------------------------------|----------------------------------|
| Existing bets | Stay active, odds adjusted | Voided, stakes returned |
| Market continuity | Market stays open | Market removed and re-created |
| Customer action | Nothing — bet adjusts automatically | Must re-place bets on new market |
| Accumulator impact | RF cascades proportionally (Rule 9.5.2) | Accumulator leg voided — rest continues per Rule 9.5.1 |

## Key Points for Support

- This is standard industry practice, not unique to Smarkets/SBK
- The void-and-readd approach is documented in Smarkets greyhound betting rules
- If a customer has an accumulator containing a greyhound leg that is voided: the leg is removed and the accumulator continues on remaining legs (Rule 9.5.1 treatment)
- Bet builder / same-event multiples on greyhounds: if the entire event is voided and re-added, the bet builder is voided in full

## Gap in Current Documentation (as of June 2026)

The existing `betting-rules-reduction-factors.md` covers horse racing RF rules (Rules 13.3, 9.5, 9.6) and the SBK cashout clawback mechanism (Rule 4.5) but does **not** cover greyhound non-runner handling. This file fills that gap.
