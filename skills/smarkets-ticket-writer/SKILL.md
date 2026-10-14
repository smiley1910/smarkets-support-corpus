---
name: smarkets-ticket-writer
description: "Draft customer-facing ticket responses for Smarkets and SBK: acknowledgements, denials, complaints handling, regulatory exits, API support. Doc-first workflow grounded in ~/smarkets-api-support/ help pages. Covers both product (SBK/Smarkets) and API tickets."
category: process
---

# Smarkets/SBK Ticket Writer

## When to Use

When you need to draft a customer-facing ticket response for any Smarkets or SBK issue: product (betting rules, account restrictions, SoW/SoF, complaints, payments) or API (auth errors, rate limits, access removal, refunds). This skill produces plain-text, customer-ready responses grounded in official documentation.

## Relationship to Other Skills

- **`process:smarkets-voice-core`**: PINNED hard voice/structure rules. ALWAYS load this alongside this skill. It owns tone, length, STAR order, decision placement, style bans, the complaints route gate and the self check. Where this skill seems to differ, voice-core wins.
- **`process:smarkets-api-support`**: API technical troubleshooting, error code reference, escalation paths. Load this first for API tickets to understand the technical issue. Verify high stakes or changing claims against the live API documentation.
- **`process:smarkets-sbk-chat-snippets`**: concise 100-200 word chat explanations. Use for live chat, not full ticket responses.
- **This skill**: full customer-facing ticket response drafting. The output layer. It uses the other two skills for diagnosis, then produces the customer-facing response.

## Application Modules

| Ticket class | Read |
|---|---|
| Complaints and betting rule disputes (void/reinstate, match market, golf, reduction factor, rounding, format, duty of care) | `references/complaints.md` |
| Standard product tickets (SBK vs exchange, promos, SoW/SoF, cancellation, payments, hacked account, limits, exits, login) | `references/standard-tickets.md` |
| API tickets (limits, auth, order types, scope, liquidity, streaming) | `references/api-tickets.md` |

Workflow instruments (kept as-is): `references/complaint-intake-questionnaire.md`
(mandatory intake), `references/council-verification-template.md` (verification
goal), `references/bet-sequence-remedy-mapping.md` (bet map),
`references/customer-claim-rebuttal-map.md` (rebuttal map).
Variant authority: `references/decline-further-credit-after-prior-credit.md`
for that variant; extended voice operationalisations in
`references/voice-rules-extended.md`. Canonical reusable customer templates
live in `~/smarkets-api-support/templates/` (see `templates/` pointer).

## The Workflow (Always Follow)

### Step 0.0: Complaint intake (mandatory when the ticket is a complaint)

If the customer message is a complaint, a formal complaint, a final-response request, or a
threatened escalation (IBAS, eCOGRA, UKGC, MGA, the EU ODR, a solicitor, or social media),
run `references/complaint-intake-questionnaire.md` BEFORE anything else. Return its output
contract (classification, questions to Michael, optional customer questions, optional holding
draft) and stop. Do not draft a customer response in the same turn unless Michael explicitly
asks for a provisional draft, and never skip the intake to save a step.

### Step 0: Build the case and remedy map

Before drafting, separate the customer's account of events from the approved internal resolution. For multi-bet, multi-market, resettlement, goodwill, refund, or support-advice cases, create a bet-by-bet map using `references/bet-sequence-remedy-mapping.md`. Treat the internal decision as authoritative, but do not fill gaps by inference. If the treatment of any bet is unclear, ask Michael before drafting.

For decline and partial-decline tickets, also produce a customer-claim-by-claim rebuttal map. See `references/customer-claim-rebuttal-map.md` for the full template and pitfalls. The rebuttal map is for Michael's review before the draft goes out. It lays out each customer ask and the corresponding draft paragraph, lists parts of the customer email the draft DELIBERATELY does not respond to, and surfaces risks. Save alongside the draft in `~/smarkets-api-support/responses/` as `<original>-REBUTTAL-MAP.md`.

### Step 1: Search the docs BEFORE drafting

**Never draft from memory.** Always search `~/smarkets-api-support/` for relevant policy/rules first.

```
search_files(pattern="<topic keywords>", path="~/smarkets-api-support", target="content", i=true)
```

Key search locations:
- `~/smarkets-api-support/help-pages/sbk/en-gb/`: SBK help articles
- `~/smarkets-api-support/help-pages/smarkets/en-gb/`: Smarkets help articles
- `~/smarkets-api-support/training/confluence_draft_v2.md`: internal training guide with FAQ
- `~/smarkets-api-support/rag-context/`: consolidated reference docs
- `~/smarkets-api-support/docs/`: API knowledge base
- `~/smarkets-api-support/openapi/smarkets_openapi.json`: OpenAPI v3 spec (single-line JSON; query it with Python field extraction, never with plain search)

The local spec copy can lag the live spec, so verify customer-facing limit and
endpoint claims against the live spec (`https://api.smarkets.com/v0/control/openapi/?tags=trading_api`)
when accuracy is critical. Run `python3 scripts/verify_live_spec.py` before drafting
rate-limit tickets. Detail lives in `references/api-tickets.md`.

### Step 2: Read the source documents

Read the actual articles found in Step 1. Do not rely on search snippets alone. Read the full article to understand context, exceptions and related rules. Cite the specific article title and rule number in your response.

### Step 3: Determine response type

| Response Type | When to Use | Tone |
|--------------|-------------|------|
| **Acknowledgement** | Customer issue is valid, action being taken | Empathetic, transparent, action-oriented |
| **Denial** | Request cannot be fulfilled per rules/T&Cs | Firm but respectful, cite specific rules |
| **Diplomatic exit** | Regulatory/market withdrawal, service discontinuation | Warm, appreciative, clear on next steps |
| **Complaints handling** | Customer requests complaints process | Neutral, provide process, don't argue the complaint |
| **Refund/fee communication** | Returning fees, processing refunds | Clear on amounts, timelines, payment method |
| **Partial grant (good faith credit)** | Customer partly right; credit one position while upholding another | Warm on the credit, firm on the upheld position, good faith stated explicitly, terms backing both limbs |
| **Technical resolution** | API issue diagnosed and fixed/fixed-pending | Direct, technical but accessible, include error context |

### Step 4: Draft the response

Before drafting a resolution, confirm you have enough diagnostic information. If the customer has not provided the full error response (body, not just status code), the response body format, or other critical details, send probing questions FIRST. Do not jump to resolution based on assumptions or inferences. See the smarkets-api-support skill, Step 1: Diagnose First, Resolve Second. You can combine probing questions with a side note about what you've already found so the customer gets value immediately.

If the customer's email IS descriptive enough to form a likely diagnosis, do NOT send multiple blind probing questions. State the likely diagnosis and ask for the ONE piece of evidence that confirms it. Prefer a single soft hypothesis over multiple possibilities. Ask about recurrence rather than reconstruction.

Follow the formatting rules below. Always cite the specific doc/rule that backs your position. If you cannot find a doc that supports the response, say so. Do not fabricate citations.

### Step 4.5: Three-Pass Council Verification (REQUIRED, WITH ONE EXCEPTION)

**You must NEVER present a draft to Michael without completing verification.** Do not claim that a draft was council verified unless `delegate_task` actually ran and returned a report. If a required council was skipped or unavailable, label the draft unverified and say so plainly.

**Simple info tickets skip the council.** A straight policy or info confirmation, with no complaint, no rule dispute, no account-specific data and no decision resting on it, does not need the three-pass council: extra passes add latency without changing a fact-verified answer, and over-deliberating two-question tickets is a standing correction from Michael. Light path for this class only: verify every fact against the live sources, run the voice-core self-check, deliver the draft directly. Everything else still goes through the council, revisions included: complaints, denials, rule interpretation, account outcomes, and any ticket where an error would be costly.

Separate customer reported facts, account verified facts supplied by Michael, internal decision mapping, source documentation, and inference. Michael's explicit account verification outranks an incomplete customer narrative. Do not convert inference into account fact.

Call delegate_task with:
- **toolsets:** ["file", "terminal", "search"]
- **goal:** the verification goal (full text in `references/council-verification-template.md`)
- **context:** (1) the full draft, (2) the customer's original message verbatim, (3) the three pass definitions, (4) relevant skill rules, (5) the docs path ~/smarkets-api-support/

After the subagent returns:
1. If APPROVED: present ONLY the draft to Michael, never the verification report.
2. If NEEDS REVISION: address every flagged issue silently, then present ONLY the revised draft. Note brief disagreement in one line at most.

```
VERIFICATION SUMMARY: (only if Michael explicitly asks)
- Factual: [N] claims verified, [N] flagged as inference: [list]
- Process: [PASS/FAIL per item]
- Voice: [clean / N issues fixed: list]
- Subagent recommendation: [APPROVED / NEEDS REVISION]
```

### Example-auth gate (lead by example)

When the draft names an event, market id, contract id, price, or book as a worked example, verify the example with authenticated calls carrying a session token. If no auth is available, verify existence and shape unauthenticated at most, mark the example `WARNING: unverified example`, and tell the customer to replay the same call with their token. Never present an unauthenticated book as the live customer view.

### Source and citation gate

Before quoting or citing any rule, policy, T&Cs clause, article, endpoint, rate limit, or operational fact, verify that the referenced source exists in the workspace or can be retrieved from the live source. If a referenced file is missing or the source cannot be checked, mark it for Michael as unverified or obtain the source first.

### Case-fact hierarchy and final-draft audit

Use the strongest available case evidence in this order: (1) verified account or event data supplied by Michael, (2) the approved internal decision mapping, (3) the customer's message, and (4) general inference. Before presenting a final response, audit the exact draft again: every operational claim against the case facts, every bet ID and amount against the mapping, every rule quotation against the source file. The council must review the actual final wording.

For a first-time customer or a soft decline, do not collapse the answer into a bare decision. Give enough context to explain what happened, why the position follows under the rule, and the concrete outcome. Preserve relevant event names, bet IDs, liabilities, and the practical reason where they make the result understandable.

When Michael supplies a full customer ticket followed by a narrow internal instruction, return the complete customer-facing reply, not only the narrow sentence he highlighted. Keep it tight by removing repetition, not by omitting material facts.

### Step 5: Provide doc references to the user (Michael)

After the customer-facing response, list the specific articles and rule numbers you relied on, so Michael can verify. Format:

```
Key doc references:
- **Article Title** (help.smarkets.com or help.getsbk.com): specific clause/section
- **Rule X.Y**: what it says
```

## Formatting and voice rules

Voice-core is authoritative for tone, structure, length and style. This section
adds ticket layer mechanics only.

- Use plain text only. No markdown tables, ReST, decorative headings, or formatting that the ticket system may alter.
- Use STRAIGHT quotes and straight apostrophes only (" '). Curly quotes double-encode through ticketing paste paths.
- Use numbered lists only when they genuinely improve clarity. Keep paragraphs short without forcing uniform length.
- Default shape for simple tickets with no rule carrying the decision: greeting, decision or material finding, reason with rule where needed, practical next step if any, sign-off.
- For complaints and denials whose case rests on a rule, voice-core section 1 overrides the default: Review then Reason then Action, with the single decision sentence last. Never put the firm decision in paragraph 2-3 as an early kill.
- The complaints route gate lives in voice-core section 5. Never restate it here; point to it.
- State the position early except where the rule based variant above applies. Do not narrate chronologically unless the sequence explains the remedy. For multi-bet cases use the explicit remedy map.
- Match the case, not a fixed word count. Remove any sentence that only repeats the decision, performs empathy, or tells the customer how to interpret the outcome.
- Write as a competent support agent who knows the product: clear, direct UK correspondence. Every sentence states a material fact, gives the decision, explains the reason, or gives a necessary next step.
- Name the rule and explain how it applies to the facts. One rule per position. Quote wording only where the wording is disputed. Technical documentation may be paraphrased plainly.

### Verify-then-write-action-only

Michael judges tone, not spec numbers:
- Evidence stays Michael-side. Tool results go in key doc references and notes to Michael, never narrated in customer text.
- One question earns one answer. No unasked conditional branches beyond one clause for the probable immediate blocker.
- Write for action, not coverage. Lead with the fact that changes what the customer does next, then stop.
- Centre the customer's evidence. Mirror their stated facts once instead of restating agent probes.

### When Michael edits a draft

Preserve Michael's wording and tone. Fix grammar, factual ambiguity, and formatting only. Do not add warmth, filler, explanations, or polished alternatives he removed. A cut sentence signals it was unnecessary.

## SBK vs Smarkets Disambiguation

**Critical**: SBK and Smarkets are different products with different T&Cs, different betting rules, and different help centres. Always determine which product before drafting.

| Signal | Product | Help Centre |
|--------|---------|-------------|
| "exchange", "lay", "back", "liability", "matched/unmatched", "commission" | Smarkets (exchange) | help.smarkets.com |
| "sportsbook", "app", "accumulator", "Bet Builder", "SBK" | SBK | help.getsbk.com |
| "API", "session token", "endpoint", "POST /v3/" | Smarkets API | help.smarkets.com + docs.smarkets.com |
| "void my bet", "cancel", "stake error" | Could be either, check context | Check both T&Cs |

**When in doubt**: check both. Detail lives in `references/standard-tickets.md`.

## Escalation Routing Rules

- **Never invite speculative queries to api@smarkets.com.** Don't write "contact api@smarkets.com to confirm" when the answer is derivable from docs or testable via endpoints.
- **For whitelisted/approved markets questions:** direct the customer to test the relevant endpoints. Listing calls return exchange data and never prove approved scope; approval is enforced at order placement.
- **For in-play access questions:** same approach, without claiming a returned market proves scope.
- **For policy questions with a clear doc position:** state the position from the T&Cs directly instead of punting.
- **Legitimate api@smarkets.com escalations** are only for: concrete technical needs the public API doesn't meet, or sensitive case-by-case reviews that can't be answered from docs.

## Model Selection for Ticket Drafting

Ticket drafting is structured writing. This skill provides tone, format and doc references. It does NOT require a top-tier model. Use free models to conserve paid provider quota for main agent work. A mid-tier free model is sufficient given the skill's structure; the three-pass council catches errors.

## Pitfalls

- Quote the customer's exact words in the draft because paraphrase drifts into inferred technical terms.
- Label inference as inference because unverified claims stated as fact fail council pass one.
- State the likely diagnosis plus one confirming ask when logs suffice because blind probes read as condescending.
- Multiply events by requests per event before stating counts because logs report events, not requests.
- Cite the 24 hour aim for ID checks only because source of wealth has no documented SLA.
- Frame exits around service level because regulator blame and fault admission both create liability.
- Use plain text only because the ticketing backend breaks on rich markup.
- Check clause numbers per product because SBK and Smarkets numbering differs.
- Read the full article before citing because snippets mislead on exceptions.
- Never describe any endpoint as public or needing no auth because auth posture is not public documentation.
- Flag missing sources to Michael instead of inventing citations because fabricated refs fail verification.
- Say API documentation, never spec internals, because customers read docs, not schema files.
- Answer deprecation from the spec flag alone because forward commentary overpromises.
- Keep bet delay distinct from halted state because conflation misdiagnoses order behaviour.
- Cite data extraction limits without section numbers because no verified source ties them to one.
- Frame hedging through authorised automation plus named prohibitions because a permission claim is unverified.
- State the quotes endpoint shows the P2P book only because the website may aggregate extra liquidity.
- Give known facts plus a concrete next step for doc gaps because dismissal without a path stalls tickets.
- Check tier before stating commission mechanics because rates differ by account type.
- Attribute 1.00 floor settlements to prior advice, never to a rule, because no published rule states it.
- Verify the rounding unit reproduces example figures before drafting because mismatched maths destroys trust.
- Diagnose fixture type before citing period rules because friendly and competitive outcomes flip.
- Cite liability caps for loss refund demands because template complaints need rule anchors, not point rebuttals.
- Carry the closed loop qualifier because returns stay discretionary, never absolute.
- Fetch the live spec before citing rate limits because the local copy omits current text.
- Build the claim by claim rebuttal map for declines because it surfaces gaps before drafting.
- Run the council on every substantial draft including revisions because confidence is when errors slip through; keep two-question info tickets on the light path because over-processing them reads as process, not rigor.
- Present only the draft after approval because process commentary is not the artifact.
- Return the full reply for a full ticket plus narrow instruction because abbreviation drops material facts.
- Keep evidence Michael-side only because probe narration adds no customer action.
- Clarify zero balance early when a cancelled pending withdrawal cleared a resettlement negative balance because customers contact support in distress believing they owe a deposit.
- Write "weighed in result" without a hyphen because "weighed-in" before a noun is a hyphenated compound modifier banned under voice-core.
- Clear session context with /new between distinct customer tickets because accumulated reference files, intake transcripts, and subagent council verification reports inflate session context past 50,000+ tokens, driving up latency and token burn.
- Treat voice-core as the winner over any reference on gates because refs can carry stale defaults.
- Clarify zero balance early when a cancelled pending withdrawal cleared a resettlement negative balance because customers contact support in distress believing they owe a deposit.
- Write "weighed in result" without a hyphen because "weighed-in" before a noun is a hyphenated compound modifier banned under voice-core.
- Clear session context with /new between distinct customer tickets because accumulated reference files, intake transcripts, and subagent council verification reports inflate session context past 50,000+ tokens, driving up latency and token burn.
