---
name: smarkets-sbk-chat-snippets
description: Generate concise, verified chat-style explanations of SBK and Smarkets betting concepts for customer support chat. Includes concept registry, verification workflow, and format templates.
category: process
---

# Smarkets/SBK Chat Snippet Creator

## When to Use

When you need a concise, verified chat-style explanation of an SBK or Smarkets concept — for customer support chat, internal Slack, or quick-reference responses. The goal is a self-contained answer a customer or colleague can read in under 30 seconds.

## Relationship to Other Skills

This is the **chat-snippet format layer**. For full ticket-handling workflows, escalation paths, and API troubleshooting, load `process:smarkets-api-support`. This skill focuses on producing the *format* and *content* of concise explanations, not on the full support workflow.

## Snippet Format (The Template)

Every snippet follows this structure:

```
1. DIRECT ANSWER (1 sentence — yes/no or the core fact)
2. MECHANISM (2-4 sentences — how it actually works, bold key terms)
3. EXAMPLE (concrete numbers from docs or a realistic scenario)
4. PRACTICAL TAKEAWAY (1 sentence — what this means for the customer)
5. FOLLOW-UP (optional — a clarifying question or "see also")
```

### Format Rules

- **Length**: 100–200 words max. If it's longer, it's not a snippet — it's a doc.
- **Bold**: Key concept names only (e.g. **net liability**, **exposure**, **GTC**). Don't bold entire sentences.
- **Numbers**: Always use real examples with £ amounts and odds. Abstract explanations lose people.
- **No jargon without unpacking**: "liability" → "liability (the amount you'd pay out if your lay bet loses)".
- **Label uncertainty**: "This is my best analysis — not confirmed in the docs" when applicable.
- **SBK vs Smarkets**: Always state which product the answer applies to if there's any ambiguity.
- **No hedging stacks**: One uncertainty marker, then move on. Don't layer caveats throughout.
- **Tone**: Conversational, direct, no fluff. Like a knowledgeable colleague explaining over chat.

### Example Snippet (the reference gold standard)

> Yes, that's exactly how it works. Here's the key distinction:
>
> **Net liability** reduces your *total* reserved balance across all your bets in a market to the worst-case scenario — not the sum of each individual liability. The article's example shows £21.50 + £15.20 = £36.70 of individual liabilities, but only £11.50 (the worst case) is actually reserved.
>
> **But** — when you place a *new* lay bet, the system still needs to see you can cover that bet's individual liability at the point of placement. The netting/recalculation happens once the bet is matched and the system reconciles across all your positions. So you need enough free balance to place each bet individually, even though the total reserved amount will later drop to the net liability.
>
> Also worth noting — net liability only applies **within the same market** (same race). If you're laying horses across different races, they're independent events and there's no netting at all.

## Concept Registry

When a topic comes up, find it here to know where to verify before producing the snippet. If a topic isn't listed, follow the Verification Workflow below.

### Exchange Mechanics (Smarkets)

| Topic | What it is | Where to verify |
|-------|-----------|-----------------|
| Net liability / combined liability | Worst-case exposure across multiple **lay** bets in same market — reduces reserved balance to worst-case amount. Does NOT apply to back bets (stake = liability, deducted upfront, no netting mechanism). No market-type exclusion (outrights included) — but only for lays. See `references/net-liability-back-vs-lay.md` for back-vs-lay distinction and binary outright hedging scenario. | `help.smarkets.com/hc/en-gb/articles/212655565` (Zendesk API or Jina reader) |
| Exposure / available balance | Liability locked up from open orders, reducing available balance | `training/confluence_draft_v2.md` → "What is exposure?" section |
| Back vs lay | Back = betting something will happen; Lay = betting it won't | `training/confluence_draft_v2.md` → "Back vs Lay" section |
| Matched vs unmatched orders | Open orders waiting for a counterparty vs filled orders | `training/confluence_draft_v2.md` → exchange basics |
| Order types (GTC/GTH/KIP/IOC/FOK) | How long an order stays alive | `training/confluence_draft_v2.md` → "Order Types Explained Simply"; `references/fok-ioc-orders.md` |
| Commission tiers (Standard/Pro/Select) | 2% default on net winnings (Standard), 1% on profit AND loss per matched bet (Pro), 3% (Select); 60-day 0% intro offers possible — never state "nothing when you lose" unconditionally | `references/commission-tiers-faq.md`; `process:smarkets-ticket-writer` → `references/sbk-promo-eligibility.md` |
| Price format | Basis points out of 10,000 (decimal_odds = 10000 / price) | `references/noauth-quotes-endpoint.md`; `training/confluence_draft_v2.md` → "Price & Quantity Format" |
| Market suspension | Why markets go live/suspend/halt | `training/customer_faq.md` → Markets section |
| In-play betting | Live betting during events; bet acceptance delay | `references/noauth-quotes-endpoint.md` → coverage_delay analysis |
| Settlement | When and how markets settle | `training/customer_faq.md` → Markets section |

### SBK (Sportsbook)

| Topic | What it is | Where to verify |
|-------|-----------|-----------------|
| SBK vs Smarkets | SBK = bookmaker (house sets odds); Smarkets = exchange (P2P) | `training/confluence_draft_v2.md` → "What is SBK vs Smarkets?" |
| Separate balances | SBK and Smarkets are separate products with separate balances | `training/confluence_draft_v2.md` → "What is SBK vs Smarkets?" |
| Multiples/accumulators | Multi-leg bets on SBK | `help.smarkets.com` → "Multiples on SBK" (via Jina reader) |
| Lucky 15 | 4-selection multiple with concessions | `references/lucky15-concessions.md` |
| Reduction factors | Odds adjustment when a runner is declared non-runner | `references/betting-rules-reduction-factors.md` |
| Non-runner rules (horse racing) | Void and recalculate vs RF approach | `references/betting-rules-reduction-factors.md` |
| Non-runner rules (greyhounds) | Void-and-readd approach | `references/greyhound-non-runner-rules.md` |
| Market update / "update of the market" | Smarkets' term for changing a market's details — matched bets before the update are void (greyhound 33.3); general rule 4.5 void/resettle catch-all; no dedicated article for wording-only changes | `process:smarkets-api-support` → `references/market-update-terminology.md` |
| Full cover bet types | Yankees, Canadians, Heinz etc. | `help.smarkets.com` → "Full Cover Bet Types" (via Jina reader) |
| Promotions eligibility | SBK promos are for primary SBK customers; existing Smarkets Exchange users excluded (welcome bonus clause 14: "are not existing SBK/Smarkets Exchange users"; SB10K clause 22: "users with access to Smarkets are not able to participate") | `rag-context/sbk-product.md` L154/L160; `process:smarkets-ticket-writer` → `references/sbk-promo-eligibility.md` |

### Account & Policy

| Topic | What it is | Where to verify |
|-------|-----------|-----------------|
| KYC / verification | Identity verification requirements | `training/confluence_draft_v2.md` → "Account Verification (KYC)" |
| Closed-loop payments | Must withdraw to same method used to deposit | `references/customer-policy-faq.md` |
| Account sharing | Prohibited under T&Cs | `references/customer-policy-faq.md` |
| Payment name mismatch | Name on payment method must match account name | `references/payment-name-mismatch.md` |
| Responsible gambling | RG acknowledgement, self-exclusion, timeouts | `training/confluence_draft_v2.md` → "Responsible Gambling" |
| Withdrawals | Processing times, methods | `training/confluence_draft_v2.md` → "Deposits & Withdrawals" |

### Security & Audit (internal)

| Topic | What it is | Where to verify |
|-------|-----------|-----------------|
| Staging publicly accessible | betsbk-staging.com serves full app bundle with no auth gate | `process:smarkets-api-support` → `references/sbkscores-security-audit-june-2026.md` (Finding 3) |
| Missing security headers on betsbk.com | Production betting platform has no CSP/HSTS/X-Frame-Options | `process:smarkets-api-support` → `references/sbkscores-security-audit-june-2026.md` (Finding 2) |
| Internal infra leaked via CSP | oddsindex.com CSP exposes private IPs, localhost, staging | `process:smarkets-api-support` → `references/sbkscores-security-audit-june-2026.md` (Finding 1) |
| coverage_delay on public API | BetGenius feed delay exposed on unauthenticated event states | `process:smarkets-api-support` → `references/sbkscores-security-audit-june-2026.md` (Finding 4) |
| CEO briefing restructuring | How to restructure technical audit for executive audience | `process:smarkets-api-support` → `references/ceo-briefing-structure.md` |

### API-Specific (for technical snippets)

| Topic | What it is | Where to verify |
|-------|-----------|-----------------|
| Authentication / session tokens | How API auth works | `training/customer_faq.md` → Authentication & Sessions |
| Rate limiting | Per-endpoint limits, 429 handling | `training/customer_faq.md` → Rate Limits; `docs/quick_reference_cheatsheet.md` |
| Error codes | 401/403/429/451/500/503/504 | `training/confluence_draft_v2.md` → error code sections |
| Order placement | POST /v3/orders/, rejection codes | `training/confluence_draft_v2.md` → "Order Rejection Codes" |
| No-auth endpoints | Quotes/last_executed_prices/volumes work without auth | `references/noauth-quotes-endpoint.md` |
| Read-only access requests | Not available — full product only | `process:smarkets-api-support` → "Read-Only / Data-Only" section |
| Jurisdiction queries | Country-specific eligibility | `references/sweden-jurisdiction.md`; `process:smarkets-api-support` → "Jurisdiction queries" |

## Verification Workflow

**Before producing any snippet, verify the facts.** Order of priority:

1. **Check the Concept Registry** above — find the topic and its reference file
2. **Read the referenced file** in `~/smarkets-api-support/` — this is the primary source
3. **If the topic isn't in our docs**, search the Smarkets help centre via the Zendesk API (best for discovery — returns full article content in JSON, bypasses Cloudflare):
   ```bash
   curl -sL "https://smarkets.zendesk.com/api/v2/help_center/articles/search.json?query=net+liability" | python3 -m json.tool
   ```
   Use `+` for spaces. Returns title, body HTML, labels, and URLs for all matching articles.
4. **To read a specific article by ID/URL**, use the Jina AI reader (returns clean markdown):
   ```bash
   curl -sL "https://r.jina.ai/https://help.smarkets.com/hc/en-gb/articles/ARTICLE_ID"
   ```
5. **For SBK-specific articles**, try `help.getsbk.com` via the same Jina reader
6. **If still not found**, search third-party sites (thepunterspage.com, matchedbettingblog.com) — but label as "third-party source, not official documentation"
7. **If nothing verified**: produce the snippet with an explicit label: "This is my best analysis — not confirmed in official docs." Or say you can't verify and escalate.

### Verification Labels

Always use these labels in snippets when applicable:
- **[Verified]** — confirmed against official docs (workspace files or Jina-retrieved help articles)
- **[Analysis]** — best explanation based on available evidence, not directly confirmed
- **[Third-party]** — from third-party sources, not official Smarkets documentation

## SBK vs Smarkets Disambiguation Rules

Before producing a snippet, determine which product the question is about:

| Signal in the question | Product |
|----------------------|---------|
| "lay", "back and lay", "exchange", "liability", "exposure", "matched" | Smarkets (exchange) |
| "accumulator", "multiple", "Lucky 15", "odds", "bookmaker" | Could be either — check context |
| "API", "session token", "endpoint", "POST /v3/" | Smarkets API |
| "SBK", "sportsbook", "app" | SBK |
| "commission", "Pro Tier", "Standard Tier" | Smarkets (exchange) |
| "reduction factor", "non-runner", "Rule 4" | Could be either — SBK uses Rule 4; exchange uses RF differently |

**When in doubt**: ask "Is this about SBK (the sportsbook app) or Smarkets (the exchange)?" — the answer changes the explanation entirely.

## Common Snippet Patterns

### Pattern A: "How does X work?"

```
[Direct answer — what X is in one sentence]
[2-3 sentences explaining the mechanism, bold key terms]
[Concrete example with £ and odds]
[One-line practical takeaway]
```

### Pattern B: "Why can't I do X?" (constraint explanation)

```
[Direct answer — no, and the one-sentence reason]
[Brief explanation of the constraint, citing the source]
[One-sentence alternative if one exists]
```

### Pattern C: "X vs Y" (comparison)

```
[One-line summary of the distinction]
[2-3 bullet points on key differences]
[Practical takeaway: which applies to the customer's situation]
```

### Pattern D: "Is this normal?" (reassurance)

```
[Direct answer — yes/no, this is expected]
[One-sentence explanation of why it happens]
[One-line on what to do (often: nothing, or wait)]
```

## Tone & Voice Guidelines

- **"Kind" = direct with context, NOT appeasement (2026-08-15, Michael's verbatim rejection: "you sound like a negotiator trying to appease a bad situation that doesnt exist").** When asked for a kind/positive message, state the position plainly, give the context that explains it, pivot factually to what the customer DOES have, close in one line. No "Unfortunately" softeners, no "it's nothing to do with your account" reassurance, no "the upside is" salesy framing, no "I'm happy to help" closers. ~140 tight words beats ~200 padded ones. Full lesson + approved template shape: `smarkets-ticket-writer` → `references/kind-template-direct-context.md` (also `~/smarkets-api-support/templates/sbk-promo-ineligible-exchange-template.md`).
- **Conversational but precise** — like a knowledgeable colleague on Slack, not a corporate FAQ
- **Use analogies from the training material** — "think of it like a stock market for sports", "like a cinema ticket"
- **No corporate speak** — "We regret to inform you" → "Unfortunately"
- **No unnecessary hedging** — one "this is my best analysis" is enough, don't repeat it
- **Match the customer's register** — if they're technical, use technical terms; if not, use plain English
- **Always state which product** — SBK and Smarkets are different products with different rules
- **Numbers are king** — abstract explanations without numbers are less useful than concrete examples
- **Sound human, not AI** — use contractions ("we've", "can't", "it's"), be direct ("we can't do that" not "we are unable to"), refer to docs casually ("the rules say..." not "pursuant to Section 4.2..."). Push back when the customer is wrong ("that's not quite right"). Ask for clarification when guessing ("is this SBK or the exchange?"). Vary sentence length. Don't structure every response the same way.
- **Banned phrases** — "I can confirm that", "I'm pleased to advise", "Please be advised", "furthermore", "additionally", "I understand your frustration", "Should you need any further assistance, do not hesitate to reach out", "Wishing you a lovely day", "I can't confirm whether"
- **Banned structural patterns** — section headers for each question (answer inline), transcribing spec enum values into prose, "However, X — it does not reflect Y" em-dash parentheticals, quoting the spec verbatim in quotation marks, using "documented" more than once per email, zero contractions in an entire response

## Pitfalls

- **Don't produce snippets without verifying** — always check the Concept Registry and read the reference file first. The one exception is if you've just read the relevant article (e.g. via browser_navigate) and the facts are fresh. This also applies to informal product questions — if a user asks "does X apply to Y?", don't speculate based on general exchange mechanics. Search the Zendesk API or read the docs first, then answer. Speculation without evidence will get pushed back on.
- **Net liability ≠ back-back credit** — net liability is a LAY-bet feature (reduces reserved balance to worst-case across multiple lays). For BACK bets, the stake is the liability, deducted upfront with no netting. A user with back positions on both sides of a binary market still needs to top up to place more back bets — the system doesn't credit guaranteed future returns from unsettled back positions. See `references/net-liability-back-vs-lay.md`.
- **Don't confuse SBK and Smarkets rules** — non-runner rules, settlement, and bet types differ between the sportsbook and the exchange.
- **Don't invent numbers** — if you don't have a verified example, use placeholder structure ("e.g. if you lay at 3.0 for £10, your liability would be £20") and mark it as illustrative.
- **Don't over-pad** — if the answer is "no, that's not possible", say that in one sentence with the reason. Don't write three paragraphs of context for a simple no.
- **Don't skip the follow-up** — a clarifying question ("Are all your lays on the same race?") often resolves ambiguity faster than a longer explanation.
- **Don't be dismissive when you don't know something** — if the docs don't cover a topic, don't just say "the docs don't mention it" and move on. Give what you DO know and offer a concrete next step. "The docs don't mention X. What I can tell you is Y — if you're seeing Z, let me know and I'll look into it." Not "I'm not sure, the docs don't mention anything about that."
- **Don't use "username" in customer-facing language** — Smarkets customers authenticate with their email. The API field is called `username` but the value IS the email.
- **Price denominator is 10,000** — not 100,000. `decimal_odds = 10000 / price`. Getting this wrong produces odds 10x too high.
- **Net liability only applies within the same market** — laying horses in different races = independent events, no netting.
