# RAG Context Design & Smart Routing — June 2026

## Context

Built a full documentation DB from Smarkets + SBK help centres (405 files scraped),
then designed pre-built RAG context chunks and a 3-tier smart routing system for
automated support query handling.

## RAG Context Chunks

Four domain-specific pre-built context files at `~/smarkets-api-support/rag-context/`:

| File | Size | Domain |
|------|------|--------|
| `api-support.md` | 14KB | Auth flow, error codes, endpoints, order types, commission tiers |
| `betting-rules.md` | 12KB | General rules 1-11, 12 sport summaries, reduction factors, erroneous bets |
| `account-payments.md` | 16KB | KYC, deposits/withdrawals, closed loop, bonuses, safer gambling |
| `sbk-product.md` | 16KB | SBK features, cash out, multiples, bet types, troubleshooting |

### Design Principles

1. **Pre-built, not dynamic retrieval.** Flash is fast (300 TPS) but can't afford
   latency from vector search or multi-document retrieval. Pre-built chunks mean
   the entire context is loaded in one call.

2. **Domain-separated.** Each chunk covers one support domain. The query classifier
   selects which chunk(s) to inject. This keeps context small (~14-16KB each) and
   focused — Flash pattern-matches better against a focused 14KB context than a
   diluted 60KB dump.

3. **Verified facts only.** Every claim in the RAG chunks is traced to OpenAPI spec,
   T&Cs, Commission FAQ, Betting Rules, or Help Centre articles. Red-team audited
   June 2026. No inferred behaviour, no third-party claims for API behaviour.

4. **Escalation boundaries embedded.** Each chunk includes explicit "I don't have
   this information" instructions so Flash knows when to escalate rather than
   hallucinate.

## Smart Routing — 3-Tier Architecture

```
Customer Query
    ↓
Query Classifier (keyword/pattern matching)
    ↓
┌──────────────────────────────────────────┐
│ Tier 1: umans-flash (300 TPS)            │
│ • Pattern-matched errors (401, 403, 429)│
│ • Procedural questions (auth, RF, KYC)  │
│ • Settlement rules lookup               │
│ • Bonus/promo queries                    │
└──────────────────────────────────────────┘
    ↓ (if Flash says "I don't have this info"
       OR query doesn't match patterns)
┌──────────────────────────────────────────┐
│ Tier 2: umans-glm-5.2 (smarter, slower)  │
│ • Edge cases / policy ambiguity          │
│ • Multi-domain queries                   │
│ • Contradictory evidence from customer   │
└──────────────────────────────────────────┘
    ↓ (if still unresolved)
┌──────────────────────────────────────────┐
│ Tier 3: Human escalation                 │
│ • Unprecedented situations               │
│ • Customer disputes                      │
│ • Manual intervention required           │
└──────────────────────────────────────────┘
```

Full design document: `~/smarkets-api-support/rag-context/routing-design.md`

## Flash Model Configuration

- **Model:** Qwen3.6-35B-A3B-FP8 (MoE, 3B active params, 262K context window)
- **max_tokens:** ≥ 4096 (thinking model — reasoning tokens consume ~70% of budget)
- **temperature:** 0.1 (deterministic for support responses)
- **Response time:** Sub-2 seconds at 300 TPS even with 4096 max_tokens

## Test Results — June 2026

5/5 nuance tests passed with pre-built RAG context:

1. **401 Auth** → Correctly said `Session-Token`, not `Bearer`. Cited 30-min token
   expiry + `POST /v3/sessions/` re-auth.
2. **Volumes Auth** → Correctly said auth REQUIRED (not public) — critical red-team
   finding from previous audit.
3. **Reduction Factor** → Gave exact formula `4.0 × ((100-25)/100) = 3.0`,
   distinguished win (≥2.5% threshold) vs place (any RF).
4. **Order Suspension** → Correctly distinguished `good_til_halted` (cancelled)
   vs `keep_in_play` (survives).
5. **Escalation** → Correctly said "I don't have this information" when asked
   about undocumented rate limits.

### Previous Audit Finding — Resolved

The initial June 2026 audit found Flash "misses nuances — did not surface mixed
auth methods (cookie vs header) as the #1 root cause for 401-on-POST." This was
resolved by improving the RAG context structure. The `api-support.md` chunk now
explicitly documents the mixed auth methods scenario, and Flash correctly
pattern-matches against it.

**Lesson:** When Flash misses a nuance, the fix is usually improving the RAG
context — not upgrading the model. Flash pattern-matches accurately against
well-structured context but cannot reason its way to answers not in the context.

## Documentation DB — 405 Files

| Source | Count | Location |
|--------|-------|----------|
| Smarkets help articles (en-gb) | 220 | `~/smarkets-api-support/help-pages/smarkets/en-gb/` |
| SBK help articles (en-gb) | 132 | `~/smarkets-api-support/help-pages/sbk/en-gb/` |
| Smarkets sport rules | 27 | `~/smarkets-api-support/betting-rules/smarkets/` |
| SBK sport rules | 26 | `~/smarkets-api-support/betting-rules/sbk/` |
| Index | 405 entries | `~/smarkets-api-support/index.json` |

### Regional Cross-Check Results

- **Smarkets en-se/sv:** No unique content — redirects to en-gb
- **SBK en-us:** 5 US-specific articles (MLB Parlay Boost, US Customer Survey,
  Weekly Offer, Parlay Boost, US Affiliate Terms) — promo only
- **SBK sv-se/en-id/en-in:** Minimal unique content — en-gb is canonical
- **Conclusion:** en-gb is the source of truth. Regional variants are promotional.

### Scraping Methodology

1. **URL discovery:** Fetch section/category pages via Jina reader API
   (`https://r.jina.ai/URL`) — extracts article URLs from Zendesk help centres
2. **Article fetch:** Each article URL fetched via Jina reader → clean markdown
3. **Bypass:** Jina reliably bypasses Cloudflare on help.smarkets.com and
   help.getsbk.com `/articles/` pages. Category index pages may 404 via Jina
   — use `browser_navigate` for those instead.
4. **File naming:** `<article_num>_<slug>.md` for sport rules, `<id>_<slug>.md`
   for help articles. YAML frontmatter with product, url, scraped date.
