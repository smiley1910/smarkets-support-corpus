# Smarkets API Support — Hermes Reference

## Structure
- docs/ — documentation files
- openapi/ — OpenAPI specs (audited May 2026)
- scripts/ — API helper scripts
- training/ — training materials (14pg PDF)
- troubleshooting/ — common issues guide

## Key Docs
- betting-rules-reduction-factors.md — SBK cashout + Rule 4.5 clawback
- customer-policy-faq.md — closed-loop, account sharing

## API Quick Facts
- 21 documented endpoints
- Auth: Session-Token
- Contact: api@smarkets.com
- GBP 150 setup fee

## API Jurisdiction Requirements
- API users must host servers in a jurisdiction where Smarkets is licensed
- Supported: UK, Sweden, Malta, Ireland. Finland is NOT supported
- Cloudflare blocks unsupported jurisdictions at the edge (403, not 451)
- Two failure factors: (1) jurisdiction check, (2) IP reputation on datacenter IPs
- Even in a supported jurisdiction, datacenter IPs may be challenged by Cloudflare, requiring internal allowlisting request (api@smarkets.com)

## Streaming Infrastructure & CFTC Product
- Frontend JS (public, no auth) leaks: sio-live.smarkets.com (WebSocket, gambling exchange), cftc-sio-live.smarkets.com (CFTC prediction market)
- Old deprecated SDK (smk_python_sdk on GitHub, archived Jan 2019) used stream.smarkets.com:3801 (protobuf/TCP). Endpoint is NXDOMAIN (verified July 2026). SDK still publicly visible.
- CFTC product: "Smarkets Predictions", positioned as trading not gambling
- US entities: Smarkets USA Op Co. (Colorado license #90034372 since April 2020), Smarkets Holdings USA Inc (Indiana)
- Full detail in skill: ~/.hermes/skills/process/smarkets-api-support/references/streaming-infrastructure-and-cftc-product.md

## Top Gotchas
1. Mixed auth (cookie vs header) — check which endpoint uses what
2. 403 errors — Cloudflare block vs API rejection (check if response is JSON or HTML)
3. Paper→live token invalidation — tokens don't carry over

## Customer-Facing Email Rules
- Pull VERBATIM quotes from ~/smarkets-api-support/betting-rules/ — never paraphrase from memory
- User caught error: said set-piece events void bets when they actually extend pending period (Rule 12.8.5–12.8.6)
- Include links to live help centre pages
- Don't disclose internal feed errors to customers (e.g. scout flagged something that didn't happen) — present mechanism factually

## ReST Syntax Rules (ticket responses)
Reference: https://wiki.typo3.org/ReST_Syntax
Full rewriter prompt: ~/smarkets-api-support/gemini-gem-ticket-rewriter.txt
Template example: skill templates/rest-ticket-response.rst

**NEVER use Markdown.** No [text](url), no single backticks for code, no # headers, no - for top-level bullets, no triple backticks anywhere.

Patterns:
- **bold**: `**text**` — double asterisks
- *italic*: `*text*` — single asterisks
- Inline code: `` ``text`` `` — DOUBLE backticks, never single
- Code block: `.. code-block:: json` (or text/bash), content indented 4 spaces
- Hyperlink: `` `link text <https://url>`_ `` — backtick, text, space, <url>, backtick, underscore. NO space after opening backtick.
- Bullet list: `*` for top level, `-` for nested only. Blank line before and after.
- Numbered list: `#.` auto-enumerated. Do NOT use `1.` `2.` `3.`
- Admonitions: `.. note::` / `.. warning::`, content indented 4 spaces, blank line after directive
- Signature: use `|` line block syntax to preserve line breaks:
  | Kind regards,
  | Michael

What to bold: bet refs, monetary amounts, rule numbers, market names, status words (voided, settled, pending, matched), dates/times, action items
What to wrap in code: IDs, API endpoints, HTTP methods/codes, JSON keys, error codes, header names

ReST validation: double-check link text is properly included before URL. Malformed links break ticket rendering. Always validate ReST before presenting.

**KNOWN BREAKAGE (confirmed July 2026):** ReST may break in the ticketing system (docutils parser). Constructs confirmed to break: link syntax `` `text <url>`_ ``, ordered lists `` #. ``, italics `` *text* ``. If Michael reports broken rendering, fall back to plain text with plain quotation marks for T&C quotes and bare URLs for links. Do not insist on ReST if he has already switched to plain text. Triple backticks also cause parse errors — never use them.

## Open Ticket Watch (Michael will ask about these in future sessions)
- **James decline ticket — Cerezo Osaka saga, customer 2 (2026-08-03).** Decline of compensation request. £1,177.02 pre-void back bets on Dortmund, 9 further bets (backs + draw lays) → £2,033.88 net loss, £3,210.90 total. Never got through support queue; no explicit guidance ever given; declined kindly per Michael's direction. Anchors: Rule 4.6 verbatim + Rule 4.7. Final council-approved draft + full anatomy + house rules: skill `smarkets-ticket-writer` → references/voided-market-reactivation-credits.md → "Decline variant — customer 2". DISTINCT from Jack ticket 63732918 (credited £1,335.19, bet 1 stands). NEVER merge the two customers — caused a memory bleed (phantom £435 full-grant draft) on 2026-08-03.

## Documentation Style Preferences
- Ctrl+F searchable — Quick-Find Index upfront
- "What customer may say" phrase lists
- "Search for this code" first column, grouped tables
- Live OpenAPI audit before trusting local docs

## Support Email Style
- Michael's voice, not AI style. Concise, no padding
- UK English. No em-dashes/excessive hyphenation, use commas
- Plain conversational tone. Write clean so he can paste directly

## Email AI-Detection Rules (CRITICAL — customer flagged as AI)
A real customer email was caught as AI. These rules are hard-won from that incident.

**BANNED phrases/patterns:**
- "documented" used more than once per email
- Spec quoting (quoting T&Cs verbatim without context)
- Enum-as-prose (listing things as "firstly, secondly, thirdly")
- Zero contractions (always use don't, can't, won't, it's)
- Section headers in emails
- "furthermore", "additionally", "I understand"
- Hedging language
- Inviting follow-up emails ("send me IDs", "I'll dig in", "I can find out more")
- Preaching (give facts, not conclusions)

**SIGN-OFF IS NOT BANNED.** "Should you need any further assistance, do not hesitate to reach out" + "Wishing you a lovely day" ARE Smarkets standard corporate sign-off, used by ALL human agents. Do NOT treat as AI tells. Keep them in all ticket responses. If a customer flags them as AI, it's provable company template = plausible deniability. This overrides the general banned-phrases list.

**Organic writing =** contractions, direct, casual doc refs, push back, clarify when guessing, answer inline, matter-of-fact not friendly. When user edits your draft, preserve their wording + fix grammar only.

## Ticket Style — HARD RULE (customer complaint incident)
NEVER use hyphens or em-dashes in customer-facing text. Customer called out AI patterns. No AI-isms: no "furthermore", "additionally", "I understand", no hedging, no em-dashes, no bullet hyphens. Write like a human support agent: direct, conversational, slightly imperfect. Plain text only (docutils breaks on ReST). This caused a real customer complaint.

## Ticket Output Format
- All customer email/ticket responses: single copyable message, no analysis or notes around it
- Just the response text Michael can paste directly

## Docs mirror + drafting rules (moved from memory 2026-09-28)

- `~/smarkets-api-support/docs/` is SOURCE (not git). Mirror to git via
  `~/smarkets-api-responder`: run `scripts/sync_docs.sh`, then gates
  (check_manifest, check_no_emdash, cargo) + commit/push.
- Drafting: practice-first (own tooling behavior) over doc quotes; direct
  imperatives; hedge stacks read as AI. Unregistered contacts: never claim account
  checks; backend offers conditional on account ID. Concise drafts + council-of-3
  verification. See skill `smarkets-ticket-writer`.
