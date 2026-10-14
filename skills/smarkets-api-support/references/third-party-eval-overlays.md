# EV & P&L Display Questions — Session Examples

## Correction History

**Initial assumption (wrong):** That all EV displays on Smarkets pages are from third-party browser extensions.

**Correction received (June 2026):** *"Old Smarkets DID calculate EV weird — I opened a position and EV appears beside it."*

**Updated understanding:** There are **two distinct scenarios** — the legacy Old Smarkets platform had a native EV display on open positions, AND there are third-party extension overlays. The two are easily confused. Always check where the EV is displayed (on an open position vs overlaid on market listings).

## Live Example: England vs Costa Rica, Half Time Result

From a support ticket handled June 2026:

**Customer reported seeing on the market page:**
- Market: England vs Costa Rica (Half Time Result)
- "Traded £34k"
- "P&L 278.27/-£399.66"
- "EV: +£18.75"

**Resolution steps taken:**
1. Initially assumed third-party overlay (incorrect — see Correction History above)
2. User clarified customer had an **open position** on Old Smarkets platform
3. Correction: Old Smarkets **did** calculate and display EV beside open positions
4. The "weird" EV was a native platform calculation, not a tool overlay

**Lesson learned for future tickets:** Always ask "Are you seeing this EV on an open position you hold, or overlaid on the market listing page?" before deciding the answer.

## What Each Figure Actually Represents

### On Old Smarkets (Open Position EV) — Legacy UI

| Field | Meaning |
|---|---|
| "EV: +£18.75" | Smarkets' own EV calculation for the open position, based on entry price vs current market-implied probability |
| Position P&L | Standard profit/loss showing current state of trade |
| Formula | Not documented — but standard exchange EV would use: (current implied probability × potential profit) + (1 - current implied probability × potential loss) |

The EV could appear "weird" because:
- It uses the **current market price** (not the entry price) for implied probability
- If the market has moved significantly, the current-odds-based EV can differ dramatically from the customer's intuitive expectation
- The customer may expect EV to reflect their entry price analysis, not the current market

### On Current UI / SBK (Market Page) — Third-party Overlay Likely

| Field | Smarkets Reality |
|---|---|
| Traded £34k | Total matched volume across all outcomes on that selection |
| £278.27 | Best back liquidity available at that price level |
| -£399.66 | Best lay liquidity (negative = liability amount) |
| "P&L" label | Extension's label — Smarkets calls these "Back £X / Lay £Y" |
| EV: +£18.75 | External tool's EV calculation, not from Smarkets |

## Common Tools Known to Overlay EV on Exchange Pages

| Tool | Type | Website |
|---|---|---|
| OddsMonkey Toolbar | Matched betting browser extension | oddsmonkey.com |
| RebelBetting | Value betting web app + extension | rebelbetting.com |
| BettingHero | Value betting service | bettinghero.com |
| Outplayed OddsMatcher | Web-based matched betting tool | outplayed.com |

## Quick Diagnosis Questions

*"Are you seeing the 'EV' figure on an **open position** you currently hold, or is it overlaid on the market listing page where you see prices?"*

If on an **open position**: "This was a feature of the Old Smarkets exchange platform — it calculated EV for your open positions based on current market prices. The exact formula isn't documented, but if you share your entry price, stake, and the current best price, I can check whether the displayed EV makes mathematical sense."

If on the **market listing page**: "This is from a third-party browser extension, not Smarkets. Which tool are you using? (Check your browser's extension list.)"

*"Which browser extension or tool is showing you the EV figure?"*
*"What does the tool call the figure — 'EV', 'Expected Value', 'Value', or something else?"*

