# Net Liability — Back vs Lay Distinction

## Source Articles

- **"What is net liability?"** — `help.smarkets.com/hc/en-gb/articles/212655565-What-is-net-liability`
- **"Bet liability"** — `help.smarkets.com/hc/en-gb/articles/212105989-Bet-liability`
- **"How to calculate the liability of a lay bet"** — `help.smarkets.com/hc/en-gb/articles/115003381865-How-to-calculate-the-liability-of-a-lay-bet`

## Key Facts (Verified July 2026)

### Net liability is a LAY-bet feature

The "What is net liability?" article says:

> "Net liability refers to your overall exposure incurred on all of your open bets. **When you have multiple lay bets on different outcomes in the same market**, your exposure may be less than the sum of your liabilities for each individual bet. This is because it may not be possible for all of your bets to lose."

- Article labels include `"multiple lay bets"`
- The example uses two LAY bets (laying both Tottenham and Man City)
- The mechanism: system calculates worst-case scenario across all lay positions and only deducts that amount from available balance

### Back bets: liability = stake, deducted upfront, no netting

From "Bet liability" article:

> **Back (for) bets:** "The liability is the value of the stake."
> **Lay (against) bets:** liability = (backer's stake × (odds − 1))

For back bets, the stake IS the liability and is instantly deducted from available balance. The article says "If you have different bets placed on the same event, your risk is decreased and your overall liability is reduced" — but no netting mechanism is described for back-back positions. The net liability calculation (worst-case deduction) is only documented for lay bets.

### No outright market exclusion documented

The documentation does NOT distinguish between market types for net liability. There is no statement saying "net liability does not apply to outrights" or "net liability only applies to match markets." The feature appears to be market-type-agnostic — but it only applies to LAY bets, regardless of market type.

### Documentation gap: back-back positions in binary markets

The docs do not explicitly address whether back-back positions in binary markets (where one outcome must win) should receive credit toward available balance. The "What is net liability?" article only describes the mechanism for lay bets. A user with back positions on both sides of a binary market (guaranteed profit) will still need to top up their account to place additional back bets, because the stakes are already deducted and the system doesn't credit guaranteed future returns from unsettled back positions.

## Zendesk API — Searching Smarkets Help Docs

When you need to search Smarkets help articles (not just read a specific one by ID), use the Zendesk API:

```bash
curl -sL "https://smarkets.zendesk.com/api/v2/help_center/articles/search.json?query=net+liability" | python3 -m json.tool
```

- Returns full article content (title, body HTML, labels, URLs) in JSON
- Supports search across all articles — no need to know the article ID in advance
- Bypasses Cloudflare protection on the web help center
- Use `+` for spaces in the query, e.g. `query=net+liability+outright`

The Jina reader (`https://r.jina.ai/https://help.smarkets.com/...`) is still useful for reading a specific article by URL/ID, but the Zendesk API is better for discovery/search.

## Practical Scenario: Hedging in a Binary Outright

A user has BACK positions on both finalists of a binary outright (e.g., World Cup winner, down to Argentina vs Spain):
- BACK Argentina: +9k profit if Argentina wins
- BACK Spain: +6k profit if Spain wins
- One must win, so guaranteed minimum 6k profit

**Cannot place additional BACK bets without topping up** — stakes are already deducted from available balance, and the system does not credit guaranteed returns from unsettled back positions. This is NOT a net liability scenario because net liability applies to lay bets.

**Alternative**: LAY one of the selections. If the user LAYs Argentina, their existing BACK Argentina position would offset the lay (net liability reduction), potentially requiring little to no additional funds. This reduces the Argentina position rather than adding to the Spain position, but achieves a similar rebalancing.
