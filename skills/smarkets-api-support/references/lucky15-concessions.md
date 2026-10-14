# Lucky 15 Betting Concessions — Smarkets vs SBK vs High Street

## Key takeaway
**Smarkets and SBK do NOT offer "double odds for 1 winner" or any special concessions on Lucky 15 bets.** That concession is a traditional UK high-street bookmaker feature (William Hill, Betfred, Coral, etc.) — it is not a universal or standard rule.

## Smarkets Exchange (API)
- The exchange API (`POST /v3/orders/`) places individual back/lay orders on single exchange contracts
- Lucky 15s cannot be placed as a single order through the API
- A Lucky 15 on the exchange would require manually placing 15 separate orders and managing them independently
- The `GET /v3/orders/fullcover/` endpoint is read-only: it lists any fullcover orders on an account, it cannot create them. Full covers cannot be placed on Smarkets itself (the website does not support them), so there is no supported placement path today

## SBK (Smarkets Fixed-Odds Sportsbook)
- Lucky 15s are available through the SBK website/app only (not via API)
- SBK's [Full Cover Bet Types article](https://help.getsbk.com/hc/en-gb/articles/14436160505245-Full-Cover-Bet-Types) describes the Lucky 15 mechanically:
  > *4 singles, 6 doubles, 4 trebles, 1 fourfold — just one successful selection guarantees a return*
- No mention of double odds, bonuses, or any concession on a single winner anywhere in SBK documentation
- "Just one successful selection guarantees a return" means you get *some* return from the winning single — not that it's doubled
- SBK's [Multiples on SBK](https://help.getsbk.com/hc/en-gb/articles/4412914835345-Multiples-on-SBK) article covers reduction factors and voided-selection rules but adds no concessions
- Minimum stake: £/€0.05. Maximum stake per bet: £/€99,999.99

## High-Street Bookmaker Concession (for comparison)
- Many UK bookmakers offer "double odds for 1 winner" on Lucky 15, Lucky 31, and Lucky 63 bets (typically horse racing only)
- If only 1 of 4 selections wins, that winning single is paid at 2× the normal odds
- Some also offer "treble odds for 1 winner" on Lucky 31, "quadruple odds" on Lucky 63
- These are promotional concessions each bookmaker chooses to offer — they are not standardised

## Sources
- Smarkets Lucky 15 article: https://help.smarkets.com/hc/en-gb/articles/4405845528977-What-Is-a-Lucky-15-bet (via Jina reader)
- SBK Full Cover Bet Types: https://help.getsbk.com/hc/en-gb/articles/14436160505245-Full-Cover-Bet-Types (via Jina reader)
- SBK Multiples on SBK: https://help.getsbk.com/hc/en-gb/articles/4412914835345-Multiples-on-SBK (via Jina reader)
- SBK Min/Max Stakes: https://help.getsbk.com/hc/en-gb/articles/4412908289809-Minimum-and-maximum-stakes (via Jina reader)
- Smarkets General Betting Rules (Section 9.5 accumulator rules): https://help.smarkets.com/hc/en-gb/articles/212183509-1-11-General-Smarkets-betting-rules (via Jina reader)
