# Response Formatting

Extracted from SKILL.md. Ticket response formatting rules, templates, and quality standards.


## Response Formatting

### ReST Syntax (Required)

All customer-facing ticket responses must be formatted in **reStructuredText (ReST)** syntax. Reference: https://wiki.typo3.org/ReST_Syntax (TYPO3 ReST cheat sheet).

.. warning:: **ReST may break in the ticketing system.** If the user reports that ReST-formatted text broke when pasted into the ticketing system (confirmed July 2026), fall back to plain text with plain quotation marks for T&C quotes and bare URLs for links. Do not insist on ReST if the user has already switched to plain text. Investigate which specific syntax broke (link syntax `` `text <url>`_ ``, ordered lists `` #. ``, italics `` *text* ``) so future responses can avoid the problematic constructs.

Key rules:

- **Inline code**: double backticks — `` ``field_name`` ``, `` ``"immediate_or_cancel"`` ``
- **Code blocks**: `` .. code-block:: json `` (or appropriate language) with 4-space indented content
- **Bold**: `` **text** ``
- **Italic**: `` *text* ``
- **Links**: `` `Link text <URL>`_ `` or bare URLs
- **Unordered lists**: `` * `` with indentation for continuation lines
- **Ordered lists**: `` #. ``
- **Admonitions**: `` .. note:: ``, `` .. warning:: `` for important caveats (e.g., default order type gotchas)
- **Line blocks**: `` | `` for preserving line breaks (e.g., sign-offs)
- **Escape**: backslash before markup characters (`` \*not italic\* ``)

A worked example is in `` templates/rest-ticket-response.rst ``.

### Gemini Gem — Standalone ReST Syntax Enforcer

A Gemini Gem (custom Gemini AI assistant) for quick ReST syntax + UK English spell checking of ticket drafts outside Hermes. Paste a draft in → get perfect ReST out, with no wording changes. Instructions: `` templates/gemini-gem-ticket-rewriter.txt ``. To recreate or update the Gem, paste the file contents into gemini.google.com → Gems → New Gem → Instructions.

**Gemini Gem instruction engineering — critical techniques** (full details: `` references/gemini-gem-engineering.md ``):

1. **Do NOT use code block output.** Earlier versions told the Gem to wrap output in triple backticks to preserve whitespace. This was proven WRONG: the triple backticks are not valid ReST and cause parse errors when pasted into the Smarkets ticketing system (verified with docutils — `` ``` `` triggers "Inline literal start-string without end-string" and "Possible incomplete section title" errors). Instead, tell the Gem: "No code blocks. No triple backticks anywhere in your output — triple backticks are Markdown, not ReST, and will break the ReST parser." Emphasize that every character matters and 4-space indentation under admonitions must be preserved as literal space characters.

2. **Keep instructions under ~7K chars.** At 15K chars the Gem lost critical syntax rules. At 6.5K it followed all rules. Prioritize a complete worked example (input → output with a real ticket) over verbose rule descriptions.

3. **Show WRONG vs RIGHT for persistent failures.** Gemini defaults to Markdown and will produce hybrids like `` `text [url](url)`_ `` (ReST wrapper + Markdown URL). Show the exact wrong pattern it produces, label it "WRONG — never do this," and show the correct pattern next to it.

4. **Use "IN EVERY PARAGRAPH" scope language.** Without this, Gemini only bolded key terms inside admonitions, not in the main text. Explicitly state "in the main text AND inside admonitions. Not just inside notes. EVERY paragraph."

5. **End with a numbered final checklist.** Each item targets a specific failure mode (no triple backticks? admonitions indented? Markdown links remaining? bare URLs? bold in every paragraph? single backticks?).

6. **Validate ReST output with docutils before approving.** Run `` python3 -m docutils.core input.rst output.html `` to check for parse errors. The ReST may look correct visually but fail the parser — only docutils validation confirms validity.

The Gem enforces the same ReST rules documented above and defers to https://wiki.typo3.org/ReST_Syntax as its authoritative reference.

### Plain English Tone

Customer-facing responses should be in plain, conversational English — not overly technical. The customer is a developer using the API, but they don't need jargon-heavy explanations. Explain concepts simply:

- **Do**: "The ``price`` field acts as a limit price"
- **Don't**: "The price parameter constrains the matching engine to accept only orders at or below the specified basis points threshold"

Keep the user's voice: warm, approachable, direct. Don't over-formalize. When the user provides their own draft, preserve their exact wording — just apply ReST markup on top. Do not rewrite their sentences.

### Style and Output Rules (Non-Negotiable)

These rules were established from repeated corrections. Follow them from the first draft — the user rewrites AI-sounding responses manually, so writing clean from the start saves them that step.

1. **UK English spellings**: organise, behaviour, colour, optimise, etc.
2. **No em-dashes or excessive hyphenation**: Use commas instead. Em-dashes (—) and hyphenated phrases where commas work are AI writing tells. "jurisdiction-based block" (compound adjective) is fine; "real-time, high-frequency, low-latency" style hyphenation is not.
3. **Less verbose**: Be comprehensive but concise. No padding, no repetition, no excessive context-setting. If the customer asked two questions, answer both directly without framing each one.
4. **Minimal ReST structure**: Do not over-format with bold headers for every section, excessive inline code blocks, or heavy structural markup. Use ReST for inline code (`` ``code`` ``) where genuinely needed, but keep the overall structure light. Plain text with minimal markup reads more naturally.
5. **ReST link syntax**: When using `` `Link text <URL>`_ ``, always double-check the link text is included before the URL. A malformed link (missing text component) breaks the ticket rendering. This was a real bug.
6. **Single copyable block**: Output the response as one contiguous block of text the user can copy directly. No surrounding analysis, no notes, no "here's the draft" framing. Just the response.
7. **Plain conversational tone**: Not structured/formal. Avoid bullet-point-heavy responses where prose works better. Match the tone of the user's own rewritten drafts.

**Style preferences (user-corrected, July 2026):**

- **Avoid em-dashes (—) in customer responses.** Use commas instead. The user considers em-dashes an AI writing tell ("less AI"). This applies to all customer-facing text.
- **Be concise.** For pre-sales and information responses, let the T&C quotes do the work. Don't over-explain when the customer has already read the docs. One sentence of context per T&C quote is enough. If the user says "less verbose," the response is too long.
- **Do not use the term "paper testing" or "paper trading"** in customer responses. There is no paper trading environment (see Pitfalls). Use "initial testing" or "integration testing" instead.

### Internal Analysis & Notes

Internal analysis (ticket audits, review notes, Q&A breakdowns for colleagues) should be concise:
- **One message** — don't split across deliveries
- **Key points only** — bullet format, one line per item
- **Don't re-explain** reasoning already shown in the response draft
- **No padding** — if a question is fully doc-backed, say "fully doc-backed, confident" and move on
- Default to terse; expand only when asked
