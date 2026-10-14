# Smarkets & SBK Support Knowledge Corpus

Comprehensive, airgappable operational repository for Smarkets (Exchange), SBK (Sportsbook), and the Smarkets Trading API.

Contains the complete corpus of official betting rules, help centre documentation, training guides, OpenAPI specifications, voice core standards, response templates, and past case precedents.

Designed to be run as an airgapped, high-speed ticket writing harness using `oh-my-pi` (`omp`) or lightweight terminal agents.

---

## Repository Structure

```
smarkets-api-support/
├── betting-rules/                 # Official betting rules for SBK and Smarkets
│   ├── sbk/                       # 24 sports (football, racing, golf, tennis, etc.) + General Rules 1-11
│   └── smarkets/                  # Exchange sports rules + General Rules 1-11
├── help-pages/                    # Full scraped help centre articles (Zendesk corpus)
│   ├── sbk/en-gb/                 # SBK help articles (payments, promotions, verification, Safer Gambling)
│   └── smarkets/en-gb/            # Smarkets exchange articles (commission, API, trading, trading out)
├── docs/                          # Smarkets API technical documentation
│   ├── smarkets_api_knowledge_base.md
│   ├── api_endpoints_reference.md # All 21 endpoints extracted from OpenAPI spec
│   ├── request_response_schemas.md
│   └── quick_reference_cheatsheet.md
├── openapi/                       # OpenAPI v3 specifications (raw JSON specs, audited versions)
├── rag-context/                   # High-density reference guides (betting rules, sbk product, payments)
├── skills/                        # Full ticket writing workflows & voice standards
│   ├── smarkets-voice-core/       # Hard voice rules: 4-job test, STAR, anti-jugular close, style bans
│   ├── smarkets-ticket-writer/    # Workflow: intake questionnaire, remedy mapping, rebuttal maps
│   ├── smarkets-api-support/      # API technical support troubleshooting & triage
│   ├── smarkets-sbk-chat-snippets/# Live chat snippets & explanations
│   └── smarkets-reply-style/      # Core reply style standards
├── templates/                     # Canonical response templates (Steve style, SBK promo denial, etc.)
├── training/                      # Confluence drafts, customer FAQ guides, pattern-matching manuals
├── troubleshooting/               # Common API issues, Cloudflare edge blocks, rate limits
├── responses/                     # Archive of verified drafts, council briefs, and rebuttal maps
├── scripts/                       # Operational scripts & deterministic validation
│   ├── ticket_lint.py             # Fast Voice Core linter (em dashes, quotes, negative density, decisions)
│   ├── complaint_intake.py        # Triage and Part B question generator for formal complaints
│   └── rate_limit_discovery.py    # API rate limit probing & verification
└── omp/                           # Configuration and system prompt for Oh-My-Pi (OMP) harness
```

---

## Voice Core Essentials

Customer-facing communications must adhere strictly to `VOICE_CORE_PINNED.md` and `skills/smarkets-voice-core/SKILL.md`:

1. **The 4-Job Rule:** Every sentence states a material fact, gives the decision, explains the reason, or gives a necessary next step. Cut all throat-clearing and empathy padding.
2. **STAR Order for Complaints:** Acknowledge (1 line) -> Review (findings) -> Reason (applied rule) -> Action (decision).
3. **Anti-Jugular Close:** Exactly ONE decision sentence per response, placed in the closing paragraph after the reasoning has done the work.
4. **Mechanical Bans:** Plain text only, straight quotes (`" '`) only, zero em dashes (`—`), zero hyphenated compound modifiers (`weighed in result`, `real time`), negative density $\le 3$.
5. **Complaints Gate:** Proactively offer IBAS (UK) or eCOGRA (non-UK) only when the customer explicitly requested escalation or on a final position for a filed complaint.

---

## Fast Deterministic Linter

Validate any draft against the Voice Core mechanical rules in milliseconds:

```bash
python3 scripts/ticket_lint.py responses/YYYY-MM-DD-<topic>-DRAFT.txt
```

---

## Running with Oh-My-Pi (OMP)

Launch an airgapped, high-speed terminal agent inside this repository:

```bash
omp --system "$(cat omp/system_prompt.md)"
```

See `omp/README.md` for full instructions.
