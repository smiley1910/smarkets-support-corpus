# Clearly Erroneous Bets Policy — Reference & Audit Guide

> **Source:** Smarkets Help Centre, Article 212819049. Retrieved via Jina reader (verified July 2026).
> **Policy last modified:** June 8, 2018.

## Policy Structure (6 Sections)

### Section 1: Erroneous Bets (Definition)
Bets considered erroneous when: obvious significant input error (stake, price, contract ID) where best price execution cannot account for the error.

**CRITICAL — Price difference convention:** *"price differences noted below are in absolute difference in percentage price unless stated otherwise."* The policy works in PROBABILITY SPACE (percentage), not decimal odds.

Example from the policy: 50% (2.0 decimal) is "10% different" to 40% (2.5 decimal) — i.e., 10 percentage points in probability, NOT 10% of the decimal odds.

### Section 2: Filing a Complaint
- Must be received by support@smarkets.com within **60 minutes** of bet being matched
- Must include: time bet matched, contract/market, matched price, reason
- Exceptional circumstances allowed (bets matched just before market decided)

### Section 3: Outlier Transactions
- Smarkets "may, at its sole and absolute discretion" investigate trades **beyond** the 60-minute window
- **Outlier definition:** bets matched at a price exceeding **±20%** of the determined fair market price
- This is the ONLY mechanism for investigating bets reported after the 60-minute window

### Section 4: Defining Fair Market Price
- Smarkets uses available resources (recent trades, other platforms, etc.) to determine fair market price
- **±15% threshold:** *"If the erroneous bet was matched at a price of ±15% of the fair market price at the time, Smarkets reserves the right to void the bet."*
- This threshold applies to complaints filed **within 60 minutes** (Section 2)
- Voiding is discretionary ("reserves the right to"), not mandatory

### Section 5: Reviewing Bets on Smarkets' Own Motion
- Normal office hours: decision within 120 minutes
- Outside office hours: by 18:00 GMT next business day

### Section 6: Appeal
- Standard Smarkets complaint and dispute resolution process

## Two-Threshold System

| Threshold | Section | Applies When | What It Does |
|-----------|---------|--------------|--------------|
| ±15% | Section 4 | Complaint within 60 min | Smarkets "reserves the right to void" |
| ±20% | Section 3 | Complaint after 60 min (outlier) | Defines outlier; allows investigation beyond window |

**Key distinction:** The 60-minute complaint window determines which threshold applies:
- **Within 60 min** → Section 4 (15%) is the voiding threshold
- **After 60 min** → Section 3 (20%) is the only available mechanism (outlier investigation)

If you don't know the complaint timing, you cannot determine which threshold applies. This is always the first question when auditing an erroneous bet ticket.

## Percentage Price Calculation

The policy's "absolute difference in percentage price" means working in probability space:

1. Convert fair odds to percentage price: `percentage = (1 / decimal_odds) × 100`
2. Subtract the threshold (15 or 20 percentage points)
3. Convert threshold back to decimal odds: `decimal_odds = 100 / threshold_percentage`

### Worked Example: Fair odds 3.4, 20% outlier threshold

```
Fair odds:     3.4  →  percentage price:  29.41%
Threshold:     29.41% - 20pp = 9.41%  →  decimal odds: 10.63
Bet at:        10.0 →  percentage price:  10.0%
Difference:    |29.41% - 10.0%| = 19.41 percentage points
Result:        19.41 < 20  →  within threshold  →  NOT an outlier  →  bet stands
```

### Decimal vs Fractional Odds (+1.00 Stake)

Decimal odds include the stake: `decimal = fractional + 1.00`. The "1.00 floor" is the stake component — decimal odds can never go below 1.00 (that would mean >100% probability).

- Threshold percentage: 9.41% → fractional odds: (1-0.0941)/0.0941 = 9.62
- Decimal odds: 9.62 + 1.00 = 10.63 (mathematically identical to 1/0.0941)

Both methods give the same result. The +1.00 is inherent in the `1/probability` formula. When explaining the calculation to a customer, the key is to show the percentage price conversion — that's what makes the number verifiable.

## Audit Checklist for Erroneous Bet Tickets

1. **Complaint timing** — Was the complaint within 60 minutes? This determines which threshold applies (15% vs 20%). If unknown, flag it — do not assume.
2. **Threshold applied** — Does the ticket apply the correct threshold for the complaint timing?
3. **Calculation verification** — Convert to percentage price, subtract threshold in percentage points, convert back to decimal odds. Verify the agent's figure matches.
4. **Language accuracy** — Don't say "deemed to be an outlier" if the bet is within the threshold. Say "deemed not to be an outlier" or "assessed under the outlier policy."
5. **Calculation explanation** — The customer must be able to verify the math. "20% of 3.4 was odds of 10.63" is opaque — explain the percentage price conversion per Section 1.
6. **60-minute context** — If the outlier threshold was applied because the complaint was late, state this explicitly so the customer understands why this threshold (not the general policy) applies.
7. **ReST syntax** — All ticket responses must use ReST formatting (see skill's Response Formatting section and `templates/erroneous-bet-outlier-response.rst`).

## Stake-Error Void Denials (SBK)

A distinct scenario from price-error complaints: a customer requests a void because they entered the wrong stake amount (e.g., £40 instead of intended £5). This is NOT covered by the Clearly Erroneous Bets Policy's voiding criteria.

### Why the policy doesn't apply to stake errors
- Section 1 mentions "stake" as a type of input error, BUT Section 4's voiding criteria are **price-based only**: "If the erroneous bet was placed at a price of ±15% of the fair market price at the time, Smarkets reserves the right to void the bet."
- There is **no corresponding stake-based voiding threshold** in the policy.
- The policy is designed to protect against price/contract misidentification, not stake amounts the customer confirmed.

### SBK does not cancel bets on customer request
- The "Cancel a bet" help article (212104789) is for the Smarkets EXCHANGE only — unmatched/partially matched bets can be cancelled.
- SBK is a sportsbook — once a bet is placed and confirmed, it cannot be cancelled by the customer.
- General SBK Betting Rules 5.1: voiding is reserved for fraud, clearly erroneous bets (per policy), or technical error — not customer stake errors.

### Face ID / biometric confirmation as defense
If the customer confirmed the bet via Face ID or other biometric confirmation, this is an explicit confirmation of the stake amount and bet details. The customer explicitly verified the amount before the bet was submitted. This is a strong defense: responsibility for verifying the stake sits with the customer at the point of confirmation.

### Denial response key points
1. Once a bet is placed and confirmed on SBK, it cannot be cancelled at the customer's request
2. The bet was confirmed by the customer (via Face ID / biometric / explicit confirmation)
3. The Clearly Erroneous Bets Policy's voiding criteria relate to price discrepancies, not stake amounts
4. No system error or technical malfunction occurred
5. The bet will stand and settle according to its outcome
6. Direct to complaints procedure if they wish to pursue further

### Filing timing note
Even if the customer reports the error within 60 minutes (per Section 2), this doesn't change the outcome — the 60-minute window is for filing a complaint, not an automatic void. The voiding criteria in Section 4 are still price-based.

## Common Pitfalls in Erroneous Bet Communications

- **Conflating outlier definition with voiding threshold** — The 20% defines what an outlier IS. The 15% is the voiding threshold (within 60 min). Don't say "in order to void an outlier bet it must be 20% outside" — say "for a bet to be classified as an outlier, it must exceed ±20%."
- **Saying "deemed to be an outlier" when it's within threshold** — Contradictory and confusing. If it's within 20%, it's NOT an outlier.
- **Opaque calculation** — "20% of 3.4 was odds of 10.63" can't be verified without knowing the percentage price convention. Always explain: fair value → percentage price → subtract threshold in percentage points → convert back to decimal odds.
- **Missing 60-minute context** — Customer doesn't understand why the 20% threshold (not the general policy) applies.
- **Bare URLs in ReST** — Use `` `Link text <URL>`_ `` format, not bare URLs.
- **Google text fragments in URLs** — Remove `#:~:text=...` fragments; they don't work in all email clients.
- **Not stating how fair value was determined** — Section 4 describes the methodology. The ticket should at least reference it.
