# Smart Routing System — Design Document

> Routes Smarkets/SBK support queries to the appropriate model + RAG context.
> Goal: Use umans-flash (Qwen3.6-35B-A3B-FP8, ~300 TPS) for 90% of procedural queries, escalate the rest.

---

## Architecture

```
Customer Query
    │
    ▼
┌──────────────────┐
│  Query Classifier │  ← keyword matching + error code detection
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
 Tier 1    Tier 2
 Flash     GLM-5.2
+ RAG     (complex)
    │
    ▼
┌──────────────────┐
│  Response Review │  ← confidence check, escalation triggers
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
 Deliver   Escalate
 to user   to human
```

---

## Query Classification

### Category Detection (Keyword → Category → RAG Context)

| Category | Keywords/Patterns | RAG Context File | Model |
|----------|-------------------|------------------|-------|
| `api_auth` | session token, 401, login, authenticate, bearer, sessions/ | api-support.md §1-2 | Flash |
| `api_errors` | 403, 429, 500, 503, 504, rate limit, forbidden, error_type | api-support.md §2 | Flash |
| `api_endpoints` | /v3/, GET, POST, DELETE, orders, markets, quotes, events | api-support.md §3 | Flash |
| `api_orders` | place bet, cancel order, order type, IOC, GTH, KIP, fill | api-support.md §4 | Flash |
| `api_commission` | commission, 2%, 1%, 3%, pro tier, select tier | api-support.md §5 | Flash |
| `api_access` | £150, setup fee, API request form, access, approved | api-support.md §6 | Flash |
| `betting_rules` | settlement, void, non-runner, reduction factor, rule | betting-rules.md | Flash (if sport-specific) / GLM (if ambiguous) |
| `account_kyc` | verify, KYC, document, ID, passport, proof of address | account-payments.md | Flash |
| `payments` | deposit, withdraw, bank transfer, paypal, skrill, closed loop | account-payments.md | Flash |
| `sbk_product` | cash out, multiples, acca, SBK, bet feed, fullcover | sbk-product.md | Flash |
| `bonus` | bonus, promotion, welcome offer, 0%, promo | account-payments.md | Flash |
| `gambling_safe` | self-exclude, timeout, deposit limit, self-exclusion | account-payments.md | Flash |
| `complex` | (doesn't match any pattern, or matches multiple) | all context files | GLM-5.2 |

### Classification Logic (Pseudocode)

```python
def classify_query(query: str) -> tuple[str, str]:
    q = query.lower()
    
    # API error codes — highest priority, unambiguous
    if any(code in q for code in ['401', 'auth_required', 'session token', 'unauthorized']):
        return ('api_auth', 'api-support.md')
    if any(code in q for code in ['403', 'forbidden', 'not approved']):
        return ('api_errors', 'api-support.md')
    if any(code in q for code in ['429', 'rate limit', 'too many requests']):
        return ('api_errors', 'api-support.md')
    if any(code in q for code in ['500', '503', '504', 'internal error', 'timeout', 'zeus']):
        return ('api_errors', 'api-support.md')
    
    # API endpoints
    if '/v3/' in q or any(w in q for w in ['endpoint', 'api call', 'curl', 'post request']):
        return ('api_endpoints', 'api-support.md')
    if any(w in q for w in ['order type', 'cancel order', 'place bet', 'ioc', 'good_til', 'keep_in_play']):
        return ('api_orders', 'api-support.md')
    if 'commission' in q or 'pro tier' in q or 'select tier' in q:
        return ('api_commission', 'api-support.md')
    if '£150' in q or 'api request form' in q or 'api access' in q:
        return ('api_access', 'api-support.md')
    
    # Betting rules
    if any(w in q for w in ['settlement', 'void', 'non-runner', 'reduction factor', 'betting rule']):
        return ('betting_rules', 'betting-rules.md')
    
    # Account & payments
    if any(w in q for w in ['verify', 'kyc', 'document', 'passport', 'proof of address', 'id']):
        return ('account_kyc', 'account-payments.md')
    if any(w in q for w in ['deposit', 'withdraw', 'bank transfer', 'paypal', 'skrill', 'closed loop']):
        return ('payments', 'account-payments.md')
    if any(w in q for w in ['bonus', 'promotion', 'welcome offer', '0%', 'promo']):
        return ('bonus', 'account-payments.md')
    if any(w in q for w in ['self-exclud', 'timeout', 'deposit limit', 'problem gambl']):
        return ('gambling_safe', 'account-payments.md')
    
    # SBK product
    if any(w in q for w in ['cash out', 'multiples', 'acca', 'sbk', 'bet feed', 'fullcover']):
        return ('sbk_product', 'sbk-product.md')
    
    # Default: complex → escalate
    return ('complex', 'all')
```

---

## Escalation Triggers

### Auto-Escalate to GLM-5.2 (Tier 2)

1. **No pattern match** — query doesn't match any keyword category
2. **Multi-domain** — query spans 2+ categories (e.g., "Why was my order cancelled AND my commission increased?")
3. **Contradiction evidence** — customer says docs are wrong with specific evidence
4. **Policy ambiguity** — query about T&C interpretation, not factual lookup
5. **Emotional escalation** — customer uses language like "disgusted", "legal action", "ombudsman", "complaint"

### Auto-Escalate to Human (Tier 3)

1. Flash/GLM says "I don't have this information" or "contact support"
2. Account-specific investigation needed (can't resolve without looking up account)
3. Financial disputes (bet settlement disputes, missing funds)
4. Regulatory/legal queries (IBAS, gambling commission, GDPR SAR)
5. Vulnerable customer indicators (mentions of addiction, mental health, financial hardship)

---

## Implementation Options

### Option A: Hermes Skill (Recommended)
Create a Hermes skill that:
1. Takes a customer query as input
2. Classifies it
3. Loads the appropriate RAG context file
4. Calls umans-flash with the context
5. Reviews the response for escalation triggers
6. Escalates to GLM-5.2 if needed

**Pros:** Runs in Hermes, uses existing provider config, can be triggered by cron/email/webhook
**Cons:** Needs to be triggered manually or via webhook

### Option B: Standalone Python Script
A Python script that:
1. Reads queries from a queue (file, database, API)
2. Classifies and routes them
3. Writes responses back

**Pros:** Can run as a daemon, integrate with Zendesk/email
**Cons:** Needs to manage API keys, model calls separately

### Option C: Hermes Cron Job
A cron job that:
1. Polls a support inbox (email, Zendesk API)
2. Classifies and processes new queries
3. Delivers responses

**Pros:** Fully automated
**Cons:** Latency (batch processing, not real-time)

---

## Flash Configuration for Support

```
Model: umans-flash (Qwen3.6-35B-A3B-FP8)
Temperature: 0.1 (deterministic, factual)
Max Tokens: 4096 (thinking model needs budget for reasoning)
System Prompt: 
  "You are a Smarkets/SBK API support assistant. 
   Use ONLY the provided context to answer. 
   If the answer is not in the context, say 'I don't have this information — please contact api@smarkets.com for technical queries or support@smarkets.com for general queries.'
   Never invent endpoints, error codes, or auth formats.
   The auth header format is 'Authorization: Session-Token <token>' — NOT Bearer."
```

### Why max_tokens=4096
Flash is a thinking model (MoE with 3B active params). Reasoning tokens consume the budget before text output. With max_tokens=2000, the model sometimes truncates reasoning before generating the answer. 4096 gives enough room for both reasoning and a complete response.

### Why temperature=0.1
Support queries need factual, deterministic answers. Low temperature prevents creative but wrong responses. Not 0.0 because some flexibility helps with rephrasing the customer's question into a search query.

---

## RAG Context File Structure

```
~/smarkets-api-support/rag-context/
├── api-support.md          ← auth, errors, endpoints, orders, commission, T&Cs (DONE)
├── betting-rules.md        ← general rules + sport-specific settlement rules
├── account-payments.md     ← KYC, verification, deposits, withdrawals, bonus, RG
├── sbk-product.md          ← SBK features, cash out, multiples, bet feed
└── full-index.json         ← searchable index of all help articles
```

### Context Loading Strategy
- **Single category**: Load only the relevant RAG file (~10-15KB)
- **Cross-category**: Load 2 files (~20-30KB)
- **Complex/unknown**: Load all files + escalate to GLM-5.2

### Why Pre-Built Context (Not Dynamic Retrieval)
1. Flash is fast (~300 TPS) — don't want to bottleneck on vector search
2. Help centre is small enough (~350 articles) to fit in pre-built chunks
3. Pre-built chunks are curated and verified (red-team audited)
4. Dynamic retrieval risks pulling irrelevant or outdated articles
5. Flash's 262K context window easily handles 20-30KB of context

---

## Expected Performance

| Query Type | % of Volume | Model | Avg Latency | Accuracy |
|------------|------------|-------|-------------|----------|
| API auth/errors | 40% | Flash | ~2s | 95%+ with RAG |
| API endpoints/orders | 20% | Flash | ~2s | 90%+ with RAG |
| Betting rules (sport-specific) | 15% | Flash | ~2s | 85%+ |
| Account/KYC/payments | 15% | Flash | ~2s | 90%+ |
| Complex/ambiguous | 10% | GLM-5.2 | ~8s | N/A (escalated) |

### Cost Savings
- Flash at 300 TPS vs GLM-5.2 at ~50 TPS = 6x faster
- 90% of queries on Flash = 90% of queries 6x faster
- Effective average latency: 0.9 × 2s + 0.1 × 8s = 2.6s (vs 8s if all on GLM)
