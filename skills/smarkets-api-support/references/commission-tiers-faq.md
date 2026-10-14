# Commission Tiers — FAQ for API Users

## Overview

Smarkets has three commission tiers that apply regardless of how the user accesses the exchange (website, mobile, or API). There is **no automatic API discount** — the same thresholds and rules apply to everyone.

## The Three Tiers

| Tier | Rate | How You Get It | Category |
|------|------|---------------|----------|
| **Standard** | 2% | Default for all new accounts | Net profit per market |
| **Pro** | 1% | Must reach 80% of 1,500 bets/month OR £1M staked/month, then **opt in** by contacting support | Per matched bet: on winnings if it wins, on losses if it loses |
| **Select** | 3% | Applied automatically when net profit exceeds £25,000 over 12 months | Per matched bet: same basis as Pro |

## Key Distinctions

### Pro Tier (1%) — NOT automatic
- The user must actively **opt in** by contacting support once they pass 80% of either volume threshold
- The rate applies from the point of opt-in, not retroactively
- If a user's volume drops below the threshold in subsequent months, they may be moved back to Standard
- API access alone does not qualify — volume is the only criterion

### Select Tier (3%) — automatic, not a downgrade
- Applied automatically by the system — no opt-in needed
- It is NOT punishment — it's a structural mechanic to cap net exposure from high-profit accounts
- Some users interpret it as a penalty or a sign they did something wrong. It isn't — it's a standard market-making protection applied across the industry

### What's NOT available to API users
Per Section 3 of the API T&Cs:
- Affiliate commission offers — ineligible
- 60-day 0% commission for new customers — ineligible
- Any promotional commission rate — ineligible

The Pro Tier (1%) is NOT a promotional offer — it's the standard volume-based tier. API users can still qualify for and opt into it.

## What the Customer May Say

- *"I'm using the API, shouldn't I get a lower commission rate?"*
  - **Answer:** No — API access doesn't change your commission tier. The standard volume thresholds apply to everyone.

- *"My commission_type shows 0.02. Can I get the Pro Tier?"*
  - **Answer:** 0.02 = Standard 2% tier. You can get Pro (1%) if your volume passes 80% of 1,500 bets/month or £1M staked/month, and you contact support to opt in.

- *"Why is my commission 3% now? I didn't change anything."*
  - **Answer:** This is the Select Tier, applied automatically when your net profit exceeded £25,000 over the trailing 12 months. It's not a penalty — contact support if you want to discuss it.

- *"Another exchange gives API users lower fees. Why doesn't Smarkets?"*
  - **Answer:** Smarkets doesn't differentiate commission by access method — only by volume and profit. Standard pricing applies to all accounts.

- *"I've been trading for months, why am I still on 2%?"*
  - **Answer:** Check your monthly volume against the thresholds. The Pro Tier requires you to opt in once eligible — it's not applied automatically.

## Diagnostic: What commission rate is the customer on?

Check the `commission_type` field from the API session response or account endpoint:

| Value | Tier |
|-------|------|
| `0.02` | Standard (2%) |
| `0.01` | Pro (1%) |
| `0.03` | Select (3%) |

If the customer doesn't know their `commission_type`, they can check under Account → Settings → Commission on the website, or by inspecting the session response from `POST /v3/sessions/`.

## Market Maker Tier — NOT in UK Documentation

**Verified July 2026:** A "Market Maker" (sometimes "Make Maker") commission tier with ~20% on lifetime profit is NOT mentioned anywhere in the UK documentation (en-gb help pages, T&Cs Section 3, commission FAQ, or training docs). Only three tiers exist in UK docs: Standard (2%), Pro (1%), Select (3%).

This tier appears to be a Swedish-market-specific offering. It is not available for UK/non-Swedish accounts.

**When a customer asks about the Market Maker tier:**
1. Decline: "The Market Maker commission tier isn't available for your account."
2. Do NOT explain that it exists in Sweden (security/jurisdiction exposure).
3. Offer Pro Tier as the alternative — it removes the 1,500 bet and £1M staked monthly limits that typically trigger the inquiry.
4. Do NOT engage with the "20% on lifetime profit" figure — it's not in UK docs, so don't confirm or deny the rate.

**Pattern B response** (short decline + alternative):
- Single sentence declining the Market Maker tier
- Offer Pro Tier (1%) which removes the order/staked limits
- Note the 3-month minimum before opting back out (Commission FAQ; the API T&Cs Section 3 contains no such clause — do not cite it)
- Ask if they want to proceed

## Pitfalls

- **Don't confuse "Pro Tier" with "API Pro Tier"** — there is no such thing as an API-specific Pro Tier. The term comes up because some customers assume API access implies volume, which implies Pro. It doesn't.
- **Don't say "API users get Standard rates"** as a definitive statement — it's true unless the customer has opted into Pro, but you need to verify their volume.
- **The API T&Cs say "standard Customer Commission"** — that means the same tier system as everyone else, not "Standard Tier specifically". Don't quote this to shut down a Pro Tier inquiry.
- **API customers are ineligible for promotional rates** (0% new-user, affiliate) — but Pro Tier is not a promotional rate, it's a volume-based tier. Don't conflate these.
- **Select Tier (3%) can surprise users** — they often feel punished. Reassure that it's a standard market structure mechanism, not a penalty or mistake.
- **When customers ask "how do I opt into Pro Tier?"** — the answer is "contact support." There is no self-serve toggle. Don't send them on a wild goose chase through account settings.
- **"Market Maker" / "Make Maker" tier requests** — decline and offer Pro Tier. The MM tier is not in UK docs. See the section above.
- **Pro thresholds count unmatched and cancelled bets** — the Commission FAQ states the bets-placed and amount-staked metrics are "based on all bets placed, whether they are unmatched, partially matched or fully matched. The limits are based on the initial bet placement", and amount staked is "the liability of all bets placed". An algo placing and replacing orders can cross 1,500 bets/month at a small fraction of £1M staked, so never tell a customer that volume alone determines their tier.

## Source Links

- Commission FAQ: https://help.smarkets.com/hc/en-gb/articles/212654665-Smarkets-commission-FAQ
- API T&Cs (Section 3): https://help.smarkets.com/hc/en-gb/articles/34697834941085-Smarkets-API-Access-Integration-T-Cs
