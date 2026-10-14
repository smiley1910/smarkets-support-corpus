# Quotes Endpoint vs Website — Discrepancy Analysis

> **Related:** `references/noauth-quotes-endpoint.md` documents that the quotes
> endpoint works WITHOUT any auth header (returns delayed prices). This document
> covers a separate issue: quotes returning empty books on low-liquidity markets.
> Both are true simultaneously.

## The Core Question

Customer reported that `GET /v3/markets/{market_ids}/quotes/` returns `bids=[]` and `offers=[]` (empty books) for in-play football markets where the Smarkets website visibly shows active back/lay prices.

## What the Quotes Endpoint Returns

The `/v3/markets/{market_ids}/quotes/` endpoint returns the **raw peer-to-peer order book**. The response schema per market contains a `book` object:

```json
{
  "bids": [{"price": 5000, "quantity": 10000}, ...],
  "offers": [{"price": 5000, "quantity": 10000}, ...]
}
```

These represent **limit orders placed by Smarkets users on the exchange**. When there are no open limit orders at a given price level, the corresponding array is empty (`[]`). An empty book is **valid** when no user has an active order in that market.

## Most Likely Explanation — Confirmed June 2026

**Smarkets posts first-party (exchange-operated) limit orders** on lower-liquidity in-play markets to maintain visible pricing (market-making). The REST `quotes` endpoint returns only P2P (user-to-user) order book data. The website merges both for a unified display.

**Confirmation evidence (June 2026 audit):**
- Order books accessed without auth show P2P characteristics: uneven depth, tiny retail orders (£0.30 alongside £320), wide spreads on unpopular outcomes, thin offers on Draw contracts (sometimes only 1 level at £34)
- `coverage_delay: 8` in event states confirms the delayed feed mechanism
- The no-auth endpoint returns the same P2P-only data as the authenticated endpoint (delayed, not a different data set)
- If MM pricing were included, every contract would have both sides populated with consistent sizes and tighter spreads — this is not observed

This fits all observed evidence:

| Observation | Explanation |
|------------|-------------|
| Website shows live bids/offers for lower-tier in-play matches | Smarkets' own market-making orders are visible in the unified UI |
| `quotes` returns `[]` for same market | API filters out the exchange's own liquidity — you only see other users' orders |
| Premier League works (98%+) | P2P liquidity is abundant enough that first-party orders aren't needed |
| Persistent, not transient | It's a design choice in what the API exposes, not a race condition |

## Other Possible Factors (less likely)

| Factor | Why less likely |
|--------|----------------|
| **Market state suspension** — order book clears during in-play halts (goals, VAR, half-time) | Website would stop showing live prices during suspension too; customer reports consistent live display |
| **Last-traded price fill** — website shows last executed price when order book is empty | Customer confirmed they see live bids/offers with amounts, not a single last-price indicator |
| **Sportsbook pricing** — Smarkets' proprietary sportsbook (first-party fixed odds) appears on website but not in API | Customer confirmed they are viewing exchange pricing tab, not sportsbook view |

## The Direct Ask (Validated Approach)

When the evidence points to P2P-only filtering but the docs don't confirm it, the best move is a direct question to Smarkets:

> **"Does the `/v3/markets/{}/quotes/` endpoint return only P2P (non-Smarkets) liquidity, or does it include all exchange orders including those posted by Smarkets itself as a market maker? We're seeing a consistent discrepancy on in-play lower-tier matches and need to understand the data scope to determine if it's fit for our use case."**

If the customer prefers not to tip their hand about analysing Smarkets' architecture, a more neutral phrasing:

> **"We're seeing empty quotes on markets that appear liquid on the website — is there any difference in how pricing data is served between our REST integration and the web UI?"**

## Response Principles (from customer interaction)

- When the customer provides evidence contradicting your first theory: **stop, incorporate it, refine once.** Do not rotate through increasingly speculative explanations. Each new theory that gets shot down erodes trust — after two strikes, you should be thinking "this isn't in the docs, time to escalate" rather than "what else could it be?"
- Give a **single weighted answer** — "from all the information, the most likely issue is X" — not a laundry list of possibilities.
- **Be direct.** Prefer to give the single clearest answer upfront rather than layering on caveats and hedging. If the user has to say "be direct" or "give me the answer", you've already lost time. Signal uncertainty once at the top, then state your conclusion — don't interleave caveats throughout.
- The "direct ask" approach is preferred: help the customer formulate the exact right question for Smarkets' support team, then let that conversation resolve the architectural uncertainty. This is faster and more honest than cycling through theories.
- **Decision rule for when to escalate:** After you've exhausted (a) the OpenAPI spec schema, (b) all local documentation, and (c) one weighted analysis, and the answer is still unclear — escalate to api@smarkets.com. Do not reach for a third theory. The docs said everything they say about this endpoint. What remains is an architectural question for engineering, not a documentation gap.

## Supporting Evidence

### High-Liquidity Control (Premier League)
Markets with high P2P liquidity consistently show healthy quote coverage:

| Fixture | Event ID | Quote Coverage |
|---------|----------|---------------|
| Liverpool vs Brentford | 45081604 | 98.37% |
| Fulham vs Newcastle | 45081602 | 98.36% |
| West Ham vs Leeds | 45081611 | 98.32% |
| Brighton vs Man Utd | 45081598 | 98.32% |
| Tottenham vs Everton | 45081610 | 98.47% |

This confirms the quotes endpoint does work for in-play markets with sufficient liquidity. The issue is specific to **lower-liquidity markets** where P2P order books are thin.

### Lower-Liquidity Example (Palermo vs Catanzaro)
- Prematch: quotes populated normally
- In-play: quotes returned empty (`bids=[], offers=[]`)
- Website: continued showing back/lay prices
- Response: 200 OK (no errors, no rate limiting)
- Full-time result market eventually settles or closes

## Suggested Customer Response

1. **Confirm understanding** — yes, the quotes endpoint returns the raw P2P order book. Empty bids/offers means no user has an active order. This is correct API behaviour.

2. **Explain most likely cause** — the website draws from additional data sources (internal pricing/market-making) that the REST quotes endpoint does not cover.

3. **Suggest investigation steps**:
   - Test with a small limit order: place it, then poll quotes — does your order appear?
   - Check event state (`GET /v3/events/{event_ids}/states/`) at discrepancy timestamps for halts
   - Compare against `GET /v3/markets/{market_ids}/last_executed_prices/`

4. **Direct ask** — formulate the exact question for api@smarkets.com to get a definitive answer about data scope.

## Common Misconception

**"The quotes endpoint should return the same prices I see on the website."**

Not necessarily. The website is a full user-facing product that may aggregate multiple data sources (P2P orders, internal prices, last-traded prices, market-making quotes). The REST API's quotes endpoint returns only one specific source: the limit order book.
