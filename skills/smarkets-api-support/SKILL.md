---
name: smarkets-api-support
description: Handle Smarkets API support tickets using the official docs at ~/smarkets-api-support/ as the primary reference. Includes a training module for non-technical agents with pattern-matching escalation zones.
category: process
---

# Smarkets API Support — Technical Escalation Layer

## When to Use
Smarkets API issues (auth, 403/401, rate limiting, connection, orders), SBK/Smarkets betting rules and product questions, account policy (closed-loop payments, account sharing, T&Cs), or escalated non-tech agent tickets.

> **Voice:** For ANY customer-facing ticket, also load `process:smarkets-voice-core` — pinned hard rules for tone/length/STAR/style that override model defaults.

> **Complaints:** if the ticket is a complaint, a formal complaint, a final-response request, or a threatened escalation, run `process:smarkets-ticket-writer` reference `complaint-intake-questionnaire.md` before drafting. Triage helper: `~/smarkets-api-support/scripts/complaint_intake.py <complaint.txt>` classifies the complaint and prints the matching question blocks. Verified ADR route map and the internal SLA conflict (T&Cs 16.1 two working days / 10 days versus the help article's 8 weeks) are in `references/sbk-complaints-process.md`.

For login errors (`DEVICE_NOT_TRUSTED`, `IP_NOT_TRUSTED`), see `references/login-error-ticket-patterns.md` for response templates and the 403 JSON-vs-HTML diagnostic.

## Pitfalls

**Verify factual claims:** Check against primary sources (GitHub, API docs, DNS) before asserting facts. Reference files may carry stale claims from prior sessions. Example (July 2026): `stream.smarkets.com:3801` → archived SDK. See `references/streaming-infrastructure-and-cftc-product.md`.

**SoW vs Verification SLAs:** Do NOT cite the 24-hour review aim for SoW complaints — it's for Account Verification (ID/residency) only. SoW has no defined SLA. See `references/sow-complaint-assessment.md`.

**Assuming 403 mechanism without response body (July 2026):** A customer reported "Forbidden for url: https://api.smarkets.com/v3/sessions/" — this is Python's requests library output (from raise_for_status()), NOT the response body. The agent stated "Cloudflare edge block" as fact without verifying whether the response was HTML (Cloudflare) or JSON (API-level 403 with error_type). These produce the same HTTP 403 status but have different causes and resolutions. Always ask for the full response body before diagnosing the mechanism. When the customer shares a library error message, probe for response.text or suggest running with curl from the server.

**Rephrasing customer terminology:** Do not rephrase the customer's error description into your own terminology. If the customer says "Forbidden for url:...", do not refer to it as "the 403 error" in your response — the customer never said "403". Use the customer's own language when referencing their reported issue.

## Rate Limits
Live spec: `https://api.smarkets.com/v0/control/openapi/?tags=trading_api`. Global: 1200 RPM all endpoints. 6 have per-endpoint caps. Headers: `X-RateLimit-Limit/Remaining/Reset`. See `references/rate-limits.md` and `scripts/rate_limit_quick_check.py`. **Pitfall:** `responses/api-scope-confirmation.txt` says POST /v3/orders/ has no published limit — live spec says 10/sec.
the training guide was built (structure by status code, citation rules, etc.),
load `process:api-support-documentation`. That skill captures the generalisable
approach; this one captures the Smarkets-specific endpoint knowledge.

## Two-Layer System

1. **Non-technical agent** (first responder) → Uses `training/confluence_draft_v2.md` (the improved CS agent KB) to identify the error code, suggest the fix, and know when to flag for escalation. The v2 guide includes exchange basics (back vs lay, SBK vs Smarkets, exposure), API concepts (session tokens, MFA, event hierarchy, paper vs live), order types (GTC/KIP/GTH/IOC/FOK), commission tiers, price/quantity format, and common customer scenarios — all in plain English with no code blocks.
2. **You** (tech-literate agent) → Handle issues that the first responder identified as needing technical investigation

When a ticket reaches you, it should have a clear "flag for technical support" reason attached.

## Operational Constraints

**help.smarkets.com pages are blocked by Cloudflare.** You cannot browser_navigate or curl any help.smarkets.com article directly — they return a Cloudflare challenge page (HTML, 8098+ bytes). This includes T&Cs, bank withdrawal articles, and all `/hc/` pages.

**Note:** The API T&Cs article (article ID 34697834941085, "Smarkets API: Access, Integration & T&Cs") was Cloudflare-blocked during the June 2026 scrape — the saved file contains only the challenge page. The full text was retrieved via Jina reader in July 2026 and is saved in `references/api-tcs-full-text.md`. Use this local file as the canonical API T&Cs reference; re-fetch via Jina if you suspect updates.

**Fallback research strategy for policy questions:**  
1. First check the workspace docs and references — most common policies are already captured  
2. **Try the Jina AI reader** (`curl -sL "https://r.jina.ai/URL"`) — this reliably bypasses Cloudflare on help.smarkets.com and help.getsbk.com and returns clean markdown. Proven working on `/articles/` pages (Lucky 15 article, Full Cover Bet Types, General Betting Rules, Multiples on SBK, Minimum and maximum stakes). The reader sometimes fails on category index pages `/categories/` (those return 403 through it). **Aug 2026:** category pages DID render via Jina in practice (e.g. `/hc/en-gb/categories/360001480411-Betting-Rules` returned the full article list) — if a category fetch fails once, retry before assuming it's blocked. Use it as first bypass attempt before fallbacks below. **Note:** help.getsbk.com category index pages return 404 via Jina — use `browser_navigate` to see the full SBK category listing instead. Section pages (`/sections/`) work fine via Jina on both help centres.  
3. If not found, search third-party review sites (casinosadvisor.com, thepunterspage.com, matchedbettingblog.com) — these often quote Smarkets T&Cs with section numbers  
4. Try Google cache for blocked help articles (https://webcache.googleusercontent.com/search?q=cache:URL) — less reliable than Jina; often returns empty/redirect  
5. Try DuckDuckGo searches targeting specific T&C sections or help article titles  
6. Label reliability: Jina-retrieved content from official help pages is "official documentation as rendered by a third-party reader" — cite the source URL and note it was retrieved via Jina. Third-party reviews are "publicly stated policy as documented in third-party sources". Neither is a verbatim canonical source.  
7. For API-level technical questions that genuinely aren't in our docs — use the "My best analysis" pattern and escalate to api@smarkets.com; third-party reviews don't cover API behaviour

**Zendesk search discovery (verified Aug 2026):** the current help host's JSON API (`help.smarkets.com/api/v2/help_center/...`) returns 403 — don't use it for discovery. The HTML search page renders fine via Jina (`https://r.jina.ai/https://help.smarkets.com/hc/en-gb/search?query=<url-encoded>`), but result links are base64-encoded `/search/click?data=...` redirects — decode them to get real article URLs/titles:

```python
import re, base64, urllib.parse
t = open('search_page.md').read()
for title, data in re.findall(r'\[([^\]]+)\]\(https://help\.smarkets\.com/hc/en-gb/search/click\?data=([A-Za-z0-9%]+)', t):
    dec = base64.b64decode(urllib.parse.unquote(data).split('--')[0]).decode('utf-8', 'ignore')
    url = re.search(r'https://help\.smarkets\.com/hc/en-gb/articles/[^"]+', dec)
    print(title, '->', url.group(0) if url else '?')
```

Search is fuzzy — generic queries ("market amended", "incorrect market") return unrelated sports-rules articles; search exact phrases ("update of the market") to find the article that actually uses a term. Worked example with verified quotes: `references/market-update-terminology.md`.

## Source of Truth

See `references/source-of-truth.md` for verified API facts, canonical behavior documentation, and the complete fact registry.


## Escalation Workflow (Your Role)

### ⚠️ CRITICAL: Step 0 — Determine Platform Before Answering

**Before answering any product/order-type question, determine whether the customer is using the API or the website/SBK app.** The same feature (e.g., Keep in Play) has different answers depending on platform — the API answer references JSON payloads and `type` fields; the website answer references UI controls and bet slip options.

Ask: "Are you using the Smarkets API, or the website/SBK app?"

This was a real correction: a customer asked about Keep in-play, the agent assumed API and gave a payload-based answer, and the customer had to correct: "this is not for the API, it's a UI question." Don't assume API just because this is an API support skill — customers ask product questions that span both surfaces.

### ⚠️ CRITICAL: Step 1 — Diagnose First, Resolve Second

**Send probing questions BEFORE jumping to resolution.** Always. The customer reveals the real issue through their answers — jumping straight to "here's the fix" skips context and frequently misdirects the diagnosis.

**Default first action for every new ticket: send 2-4 diagnostic questions. Do not skip to analysis.**

**Probe + side note pattern (when you can identify a likely factor but cannot confirm the mechanism):** Probe for the missing diagnostic data while noting the likely factor as a side note in the same response. Example: a customer running from a German VPS gets a 403 on POST /v3/sessions/. The VPS location is clearly relevant (Germany is not a supported jurisdiction), but the 403 could be either a Cloudflare HTML edge block OR a JSON API 403 (CLIENT_JURISDICTION_MISMATCH, SOURCE_BLOCKED, IP_NOT_TRUSTED). Do not claim it is specifically a Cloudflare block without seeing the response body. Ask for the full response body (e.g., print(response.text) or curl output) and mention the VPS location as a likely factor in the same response. This lets the customer act on the likely cause immediately while you confirm the exact mechanism.

**Diagnostic questions (select what fits, don't dump all at once):**
- What does the full error response body look like? (status code, error_type, data fields)
- How long have you been using the API? When did this start?
- How frequently are you making requests? (per second, per minute)
- Are you running one client or multiple?
- Have you made any recent changes to your code or setup?
- Can you share the curl command or request payload (redacted)?

Only proceed to Steps 2-6 AFTER the customer has answered.

### Step 2: Understand what the first responder already did
- Which error code did they identify?
- Which suggested fix did they give?
- Why did they flag it? (Check the "When to flag for technical support" sections in the training guide)

### Step 3: Check the training guide for baseline context
The `training/pattern_matching_guide.md` tells you what the customer has already been told. This avoids repeating the same advice.

### Step 4: Dive into technical diagnostics
Use the endpoints reference and schema docs. Common technical actions:

**Read raw request/response data the customer sent:**
- Parse JSON error payloads from the customer
- Identify exact error_type and data fields
- Cross-reference against known error schemas

**Check for common gotchas:**
- 401 on POST but not GET → mixed auth methods (cookie vs header) or stale token
- 403 with HTML body → edge block (not an API auth issue); check for SOURCE_BLOCKED or IP_NOT_TRUSTED in JSON 403s
- 500/503 errors → server-side, escalate internally to api@smarkets.com
- Account activity CSV → datetime MUST be on the hour, exactly 1 hour apart
- Price format → **basis points out of 10,000** (NOT 100,000). Formula: `decimal_odds = 10000 / price`. Example: `5000 = 50% = decimal odds 2.0`, `7194 = 71.94% = decimal odds 1.39`. The "fraction contracts" terminology can mislead — the denominator is 10,000.
- Quantity format → 1/10,000th of currency unit. `50000 = £5.00`. Formula: `gbp = quantity / 10000`.

**When the customer provides curl output, check:**
- Is the Authorization header present and correctly formatted?
- Is the URL using the correct base (api.smarkets.com)?
- Are IDs formatted correctly (numeric strings)?
- What's the full response body (not just status code)?

### Step 5: Determine true cause
Customer-facing errors often mask the real issue:

| Reported Error | Often Actually This |
|---------------|-------------------|
| 401 AUTH_REQUIRED | Mixed auth methods (cookie vs header) |
| 401 AUTH_REQUIRED | Stale token after switching paper→live |
| 401 AUTH_REQUIRED | Token expired — TTL is 30 min with sliding renewal, NOT 24 hours (common customer misconception; see references/api-technical-quirks.md) |
| 403 FORBIDDEN | Under 60-day compliance review |
| 403 FORBIDDEN | Edge block (check if response is JSON or HTML); JSON 403 may also be SOURCE_BLOCKED or IP_NOT_TRUSTED |
| 403 FORBIDDEN (HTML, Cloudflare challenge) | Jurisdiction-based block — server IP in unsupported country (e.g. Hetzner Helsinki = Finland). Not fixable via allowlisting. Customer must relocate server to a supported jurisdiction. |
| 429 RATE_LIMIT_EXCEEDED | Multiple clients using same account |
| Order rejection | Insufficient available balance (exposure consumed it) |
| Empty events | Jurisdiction filter, account restrictions |
| Quotes endpoint returns empty book while website shows prices | API returns P2P-only order book; first-party market-making excluded (see `references/quotes-endpoint-behaviour.md`) |

### Step 6: Choose the right response pattern

**Pattern A — Problem/investigation tickets** (error, bug, unexpected behaviour):
```
1. Acknowledge the issue and what the first responder already did
2. Upon review, state what was checked and the material finding
3. State the action being taken, or the specific next step required
4. Give the technical diagnosis and why it leads to that action (citing the docs)
5. If it's a server-side issue: escalate to api@smarkets.com
```

For all resolved API tickets, use the same strict support sequence: acknowledge the issue, state the review finding, state the action, then explain why. Keep diagnostic facts separate from policy wording. Quote binding policy or T&Cs clauses exactly; do not rewrite them into a narrative.

**Pattern B — Request-denial / information-only tickets** (features that don't exist, read-only access, unconfirmed policies):
```
1. Single sentence acknowledging the request
2. Direct answer quoting the relevant T&C/reference (one quote max — the specific clause or section number)
3. Brief explanation of the constraint (no more than 2 sentences)
4. Optional alternative if one exists
5. Close
```
Keep it tight. The user in this conversation explicitly asked for a *"short response quoting docs to decline them"* — that's the preferred shape for pure no/info responses. Don't pad with multiple theories or excessive caveats.

**Pattern C — Holding response** (waiting on internal/compliance decision, can't give a full answer yet):
```
1. Acknowledge the customer's latest message and apologise for any delay
2. Confirm what you CAN confirm (e.g. their API access is active, they haven't missed any settings)
3. State that you're looking into it and expect to have a clearer update soon
4. Do NOT reveal the internal dependency (e.g. "head of compliance is back Monday")
5. Do NOT promise a specific timeline or outcome
6. Close with appreciation for their patience
```
Use when: waiting on a compliance decision, internal team review, or any situation where you need to buy time without stringing the customer along with false hope.

## Common Technical Scenarios

See `references/technical-scenarios.md` for the full scenario library (~35K chars) covering voids, non-runners, rate limits, authentication, streaming, settlement, and regulatory exits. Each scenario includes API examples, escalation steps, and response templates.

See `references/session-token-rotation-cookie-refresh.md` for the ~20 minute AUTH_REQUIRED rotation case (header-only clients cut at the rotation point; fix is sending the session and refresh cookies and adopting the renewed session token; verified live 2026-10-01).

See `references/401-quotes-mass-event.md` for the mass 401 on /quotes/ diagnostic flow (token expiry vs service disruption vs rate limit, with the "did it resolve on its own?" distinguishing question).

See `references/exchange-netting-settlement.md` for net liability vs gross, net settlement mechanics, the exposure-column reconciliation method (incl. voided / "doesn't count" bets — voids don't move cash), label decoding ("Bet Lost (winner)" = your lay lost, runner won), and a verified worked two-lay example (Aug 2026).


## Response Quality Review — Coaching Someone Else's Draft

When a user (support manager, colleague, or the ticket owner) asks you to review a draft response they've written before sending it, this is a **coaching/review** workflow, not a ticket-handling workflow. The goal is to catch factual inaccuracies and tighten precision while preserving the author's tone and structure.

### Checklist: Common Factual Pitfalls in Draft Responses

**1. "The API has a general limit of X requests per second" — ❌ Not in the docs.**

There is no documented universal requests-per-second cap. Limits are per-endpoint and pre-approved per account. The only documented specific limits are:

| Endpoint | Documented Limit |
|---|---|
| Quotes (`GET /v3/markets/{ids}/quotes/`) | 50 / 60s |
| Login (`POST /v3/sessions/`) | 5 / 300s |
| Cancel all orders (`DELETE /v3/orders/`) | 1 / 60s |
| Cancel one order (`DELETE /v3/orders/{id}/`) | 10 / s |
| Logout (`DELETE /v3/sessions/`) | 30 / 60s |

The correct approach is to direct the customer to check the `count`/`limit`/`expiry` fields in the actual error response, which tell them their specific approved limits.

**2. "These limits can't be increased" — slightly too definitive.**

The order throttle (market integrity protection) is not documented as adjustable. But the general API rate limit *can* be reviewed by us if the customer's use case genuinely needs higher throughput. The correct framing: "Reply here with your use case and we will review whether your rate limits can be adjusted. Approval is at Smarkets' discretion." We ARE the API support team, so never reroute the customer to `api@smarkets.com` in customer-facing text. **Update (30 Sep 2026):** in current practice quote limit increases are not being reviewed at this time — Michael's instruction on the 30 Sep ticket was to advise we cannot review for the moment; use the approved line and the batch-first flow in `references/rate-limit-requests.md`.

**3. Missing the `expiry` field — the single most actionable piece of diagnostic data.**

The `RATE_LIMIT_EXCEEDED` error body includes:
- `count` — requests made so far
- `limit` — the approved cap
- `expiry` — ISO timestamp of when the window resets

Always point the customer to `expiry`. It tells them exactly when to resume — more actionable than "add a small delay" or "slow down."

**4. "10 requests per second" as a general figure.**

This specific number shows up frequently in drafts as a plausible-sounding default. It is **not documented anywhere** as a universal limit. If the author pulled this from memory or general API knowledge, flag it.

**5. Quoting third-party sources for API behaviour.**

Only cite the Smarkets docs in the workspace. Third-party sources (review sites, forums) are acceptable for policy questions (T&Cs, jurisdiction) but never for API-level behaviour like rate limits, error codes, or endpoint schemas.

### Review Structure

When reviewing a draft response, structure your feedback as:

1. **What's good** — lead with validation. Acknowledge the tone, readability, and structure that works.
2. **Specific corrections** — identify each factual issue, cite the doc that disproves it, give the corrected version.
3. **What's missing** — suggest additions (e.g. the `expiry` field) that would make the response more actionable.
4. **Grade the overall accuracy** — "ready to send," "minor fixes needed," or "needs significant revision."

### When to Flag the Draft as "Needs Significant Revision"

- Multiple unsourced numbers claimed as fact (e.g. "10 req/s", "limits never increase")
- No reference to the `expiry` field in a rate-limit explanation
- Generic advice that doesn't distinguish between the two different throttles (general RATE_LIMIT vs ORDER_THROTTLE)
- Confusing the order throttle with the general rate limit

### Pitfall: Don't Use the Draft-Review Workflow When the User Just Wants You to Respond

The "Coaching Someone Else's Draft" workflow is for when the user explicitly asks, *"Review this draft before I send it"* or *"What do you think of this response?"*.

If the user says something like, *"A customer sent this query, please respond"* — they want you to **compose the response and send it**, not analyze their query back to them. Jumping into draft-review mode (offering suggestions, marking up issues, proposing rewrites) when they asked for a reply wastes time and forces them to re-direct you.

**Check before entering review mode:** Did the user say "review this" or "respond to this"? If "respond", just write the response and deliver it. If you're unsure, ask — don't default to review.

## Response Formatting

See `references/response-formatting.md` for formatting rules, quality standards, and template structures for ticket responses.


## Model Capability Awareness

This skill is designed for agentic execution — loading references, following procedures, and composing responses. The vast majority of Smarkets tickets (~90%) are **procedural pattern-matching**: known error codes mapped to known fixes in the docs. A capable reflex-grade agentic model handles these well.

Some tickets (~10%) require deeper reasoning — novel edge cases, contradictory evidence, policy ambiguity the docs don't cover directly, or unusual error patterns that don't match any documented scenario. These benefit from a thinking/reasoning model.

### umans-flash (Qwen3.6-35B-A3B-FP8) — Audited June 2026

Full audit at `references/umans-flash-model-audit-june-2026.md`. Key findings:

**With RAG context (docs provided):** Adequate for Tier 1 procedural queries. June 2026 re-test with improved RAG context chunks: **5/5 nuance tests passed** — correctly identifies auth header format (`Session-Token` not `Bearer`), says volumes endpoint requires auth (not public), calculates reduction factors with exact formula, distinguishes `good_til_halted` vs `keep_in_play` on suspension, and correctly says "I don't have this information" when asked about undocumented rate limits instead of hallucinating. The earlier audit's "misses nuances" finding was resolved by improving the RAG context structure — Flash pattern-matches against well-structured context accurately.

**Without RAG context:** **Do not use** — hallucinates Smarkets-specific API details. Said `Bearer` instead of `Session-Token`, invented a non-existent `X-Smarkets-Token` header. The model has no reliable Smarkets API knowledge in its training data.

**Safety property:** Correctly refuses to answer when docs don't cover the topic — won't hallucinate when it genuinely doesn't know. This makes it safe for RAG use.

**Thinking model:** Uses reasoning_tokens (~70% of completion). Set `max_tokens` ≥ 4096 to ensure visible output after reasoning completes. At ~300 TPS, response time is still sub-2 seconds.

**Three-tier routing (designed June 2026):** Tier 1: Flash (300 TPS) for 90% pattern-matched queries with pre-built RAG context chunks. Tier 2: glm-5.2 or kimi-k2.7 for 10% edge cases (policy ambiguity, multi-domain queries, contradictory evidence). Tier 3: Human escalation (unprecedented situations, customer disputes, manual intervention). Full routing design at `~/smarkets-api-support/rag-context/routing-design.md`. RAG context chunks at `~/smarkets-api-support/rag-context/` (api-support.md 14KB, betting-rules.md 12KB, account-payments.md 16KB, sbk-product.md 16KB). Test script: `scripts/test_flash_rag.py`. See `references/umans-flash-model-audit-june-2026.md` for full audit details.

**Env key quirk:** `UMANS_API_KEY` in `~/.hermes/.env` has single quotes around the value — strip with `tr -d "'\""` or Python `.strip("'\"")` when extracting via shell.

### When to proceed confidently with a reflex model

Tickets where the error code and customer description match a documented scenario in the skill's Common Technical Scenarios section, and the fix is clearly outlined in the workspace docs. Examples:
- 403 RG_ACK_REQUIRED → website RG acknowledgement
- 401 on POST but GET works → mixed auth / stale token / MFA
- Commission tier query with commission_type visible → Standard/Pro/Select explanation
- FOK/IOC confusion → type + minimum_accepted_quantity mapping
- Read-only access request → decline with T&C Section 2

### When to consider switching to a thinking model

Tickets where:
- The error response doesn't match any documented error_type
- Customer describes behaviour that contradicts the docs (API does X but customer says Y)
- Two equally plausible explanations exist and the docs don't disambiguate
- Novel policy question with no reference file covering it
- The customer provides detailed evidence that doesn't fit established patterns

In these cases, flag the ticket internally as "needs investigation" and either switch to a thinking-capable model or, for pure API-level questions not in docs, escalate to api@smarkets.com with your best analysis labelled as such.

### Operational note

The agent's model determines which mode it's in. If you're running on a reflex (non-thinking) model and hit a ticket that crosses into the "needs thinking" zone, surface this to the user: "This looks like an edge case — I've given my best analysis from the docs, but this would benefit from a reasoning model or escalation to api@smarkets.com." Do not force a reflex model to reason through novel territory — it will produce plausible-sounding but wrong answers.

## Pitfalls

See `references/pitfalls-catalog.md` for the full pitfalls catalog covering common mistakes in API support, ticket handling, and customer communication.

