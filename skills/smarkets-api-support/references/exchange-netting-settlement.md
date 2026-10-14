# Exchange netting, liability & settlement (verified Aug 2026)

Worked mechanics for explaining "why is my exposure X" / "why did my balance change" on the market executions page.

## Net liability (not gross)
- Exchange exposure ≠ sum of gross lay liabilities. Only one runner can win, so the exchange nets positions across the market. **Net liability = worst-case outcome P&L.**
- Lay liability = stake × (odds − 1); lay win = stake.
- Worked example (17:55 To-win market, three lays):
  - DOM lay £50 @ 2.00 (liab £50) · Calef lay £50 @ 2.74 (liab £86.99) · Calef lay £11.54 @ 2.32 (liab £15.23). Gross = £152.22.
  - DOM wins: −50 + 50 + 11.54 = **+11.54** · Calef wins: +50 − 86.99 − 15.23 = **−52.22** · other wins: +111.54
  - Max net liability = **£52.22** = the exposure column once fully matched. The two lays hedge (can't lose both; if both lose you win both).
- Exposure column = max net liability at that moment. Adding a hedged lay can move the worst case from one outcome to another (−£50 DOM-only → −£36.99 after Calef matched).

## Net settlement
- Market settles as **ONE net cash flow**: Σ winning stakes − Σ losing liabilities. No per-bet transfers; the balance column moves by the net amount only.
- Balance check: balance_before + net_settlement = balance_after (must close exactly).
- Executions rows still show per-bet [stake, liability, odds, prob] — don't read them as individual cash movements.

## Label decoding (confusing by design)
- "Bet Lost (winner)" = YOUR lay lost because the runner WON.
- "Bet Won (loser)" = your lay won because the runner LOST.
- Parenthetical = the runner's result, not yours.

## Exposure-column caveats & reconciliation
- A row's exposure may include OTHER open positions (other markets, or bets later voided). It may not decompose from a filtered bet list — verified case: −£85.50 on rows where visible bets alone give −£50.
- **Reconciliation method:** verify settlement closes using only the visible bets. If it closes exactly (e.g. +£11.54, £2845.63 → £2857.17), anything extra in exposure rows = bets outside the view (other markets, or voided / "doesn't count" bets).
- **Voided/"doesn't count" bets:** zero exposure after removal, zero settlement contribution.
- **Voids and cancellations do NOT move cash** — cash only moves at settlement (or deposit/withdrawal). A mid-session balance jump ⇒ some market settled (or a top-up), never a void refund. (Contrast: post-settlement reversals DO move cash back — the goodwill/voided-market case.)

## Commission
- Standard: 2% on net market winnings (winnings − losses in that market). Header "Market Settled Commission: £0.00" with a net win ⇒ 0% commission promo active (2% of £11.54 ≈ £0.23 would display, not 0.00).

## Customer-facing shape
Same content, plain English, one worked example, no code. Lead with the outcome table (per-runner P&L), then "the exchange settles the whole market as one net amount" — that's the sentence that lands for most customers.
