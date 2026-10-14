# ReST Syntax Audit — July 2026

Full audit of ReST syntax rules and reply writing rules across the Smarkets API support workspace. Found and fixed 6 issues.

## Issues Found and Fixed

### 1. HERMES_REFERENCE.md — Rules too thin (FIXED)
The ReST syntax summary was a single line listing patterns but missing critical rules. Expanded to full section covering: what to bold, what to wrap in code, list formats (``#.`` not ``1.``), admonition indentation, no-Markdown rule, signature line blocks (``|``), and the known breakage warning.

### 2. HERMES_REFERENCE.md — Missing breakage warning (FIXED)
The skill SKILL.md (line 677) already warns that ReST breaks in the ticketing system (docutils parser), with link syntax, ordered lists, and italics confirmed broken. The reference didn't mention this or the plain text fallback. Now added.

### 3. login-error-ticket-patterns.md — Broken numbered list (FIXED)
Template used ``1.`` ``2.`` ``3.`` instead of ``#.`` for numbered lists. Fixed in the skill's copy.

### 4. Both rewriter files — Wrong hyperlink description (FIXED)
Both ``gemini-gem-ticket-rewriter.txt`` (domain) and the v5 copy said "opening backtick, space, link text" but the actual ReST syntax has NO space after the opening backtick. Fixed in all 3 copies (domain x2, skill x1).

### 5. api-scope-confirmation.txt — Broken signature (NOT FIXED, historical record)
Uses plain ``Best regards,\nMichael`` which ReST collapses into one paragraph. Should use ``|`` line block syntax. Left as-is since it's a sent response, not a template.

### 6. Agent output — Inherited broken template (FIXED by fixing #3)
Agent followed the broken template, producing ``1.`` instead of ``#.``, missing bold, missing ``|`` signature.

## Key ReST Rules (Quick Reference)

- **NEVER use Markdown**: no ``[text](url)``, no single backticks for code, no ``#`` headers, no ``-`` for top-level bullets, no triple backticks
- **Inline code**: double backticks — ``\`\`text\`\``
- **Hyperlink**: `` `link text <https://url>`_ `` — NO space after opening backtick
- **Numbered list**: ``#.`` not ``1.``
- **Bullet list**: ``*`` top level, ``-`` nested only
- **Admonitions**: ``.. note::`` / ``.. warning::`` with 4-space indented content
- **Signature**: ``|`` line block syntax to preserve line breaks
- **Known breakage**: link syntax, ordered lists, and italics may break in the ticketing system (docutils). Fall back to plain text if Michael reports broken rendering.

## Files Modified

- ``~/smarkets-api-support/HERMES_REFERENCE.md`` — expanded ReST rules + breakage warning
- ``~/.hermes/skills/process/smarkets-api-support/references/login-error-ticket-patterns.md`` — fixed ``#.`` + added workflow pitfall
- ``~/smarkets-api-support/gemini-gem-ticket-rewriter.txt`` — fixed hyperlink description
- ``~/smarkets-api-support/gemini-gem-ticket-rewriter (5).txt`` — fixed hyperlink description
- ``~/.hermes/skills/process/smarkets-api-support/templates/gemini-gem-ticket-rewriter.txt`` — fixed hyperlink description
