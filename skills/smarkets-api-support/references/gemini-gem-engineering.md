# Gemini Gem Instruction Engineering — Lessons from the Smarkets Ticket Rewriter

Created: July 2026
Last updated: July 2026 (v6 — code block output proven WRONG)
Context: Building a Gemini Gem that converts Smarkets support ticket drafts into perfect reStructuredText (ReST) with UK English spell checking.

## The Problem

Gemini Gems (custom Gemini AI assistants) need instruction text (system prompt) that reliably produces a specific output format. The Smarkets Ticket Rewriter Gem needed to:
- Take a raw ticket draft as input
- Fix UK English spelling errors (without changing wording)
- Apply ReST syntax formatting (bold, code, links, lists, admonitions)
- Output clean ReST with zero Markdown contamination

## Iteration History

### v1 — Syntax reference manual (15K chars)
Described every ReST element with syntax patterns. Result: Gemini passively output near-unformatted text. It knew the syntax but didn't know WHAT to format or WHEN.

**Lesson:** Describing syntax is not enough. The Gem needs to be told what to actively look for and format.

### v2 — Added hyperlink conversion rules
Added 5 cases for URL conversion with a checklist. Result: Hyperlinks still broken — Gemini output a Markdown/ReST hybrid: `` `text [url](url)`_ ``

**Lesson:** Showing the correct pattern isn't enough when Gemini defaults to Markdown. Must show the WRONG pattern explicitly next to the RIGHT pattern.

### v3 — Complete rewrite with two-pass model (15K chars)
Added what-to-bold lists, admonition detection, code wrapping rules. Result: Still broken — 15K chars was too long, the Gem lost critical patterns in the noise.

**Lesson:** Keep Gem instructions under ~7K chars. Long instructions cause the Gem to lose track of critical syntax rules. Shorter + worked example > longer + rules.

### v4 — Cut to 6.4K with worked example
Added a complete input→output example using a real ticket. Result: Three persistent failures:
1. No bold in the first paragraph (only bolded inside admonitions)
2. Note content not indented (sat at column 0, breaking ReST)
3. Hyperlink still using Markdown `[url](url)` instead of angle brackets `<url>`

**Lesson:** A worked example alone doesn't fix deeply ingrained LLM behaviors. Need to address the root cause.

### v5 — Code block output (6.5K chars) — APPEARED TO WORK, BUT WAS WRONG
Key change: Told the Gem to wrap its ENTIRE output in a triple-backtick code block. Result: All three failures appeared fixed — bold in every paragraph, note content indented, hyperlinks using angle brackets.

**Why it appeared to work:**
- **Indentation failure:** Gemini's chat renderer strips leading whitespace from non-code-block text. The Gem WAS outputting 4-space indents, but the renderer ate them. Code block output preserved whitespace.
- **Markdown contamination:** When Gemini sees `**bold**` in instructions, it may interpret it as rendered formatting rather than literal characters to output. Code block output forced literal character output.
- **Bold only in admonitions:** Adding "IN EVERY PARAGRAPH" emphasis and a checklist item fixed this.

**BUT:** The output was never tested against a real ReST parser. It looked correct in Gemini's chat, but the triple backtick markers were included in the output.

### v6 — Code block output proven WRONG (6.5K chars) ✅ CURRENT
The user pasted v5's output into the Smarkets ticketing system and got: "Error formatting content of this ticket, please check syntax https://wiki.typo3.org/ReST_Syntax"

**Diagnosis with docutils:**
```python
# Test 1: Clean ReST (no triple backticks) → CLEAN (zero errors)
# Test 2: ReST wrapped in triple backticks → ERRORS:
#   - "Inline literal start-string without end-string"
#   - "Possible incomplete section title"
#   - "Possible title underline, too short for the title"
```

**Root cause:** Triple backticks (`` ``` ``) are Markdown syntax, NOT ReST. In ReST, `` `` `` (double backticks) start an inline literal, and a line of only `` ``` `` is interpreted as a potential section title overline/underline. The ReST parser chokes on them.

**Fix:** Removed all code block / triple backtick instructions from the Gem. Replaced with:
- "No code blocks. No triple backticks anywhere in your output — triple backticks are Markdown, not ReST, and will break the ReST parser."
- "Your output will be pasted directly into a ReST parser. Every character matters. You MUST preserve all whitespace exactly, especially the 4-space indentation under .. note:: and .. warning:: directives."
- Final checklist item 1: "Is your output free of triple backticks and code blocks? It must be."

**Remaining risk:** Without code blocks, Gemini's chat renderer may strip the 4-space indentation again (the original v4 problem). This is a trade-off: code blocks preserve whitespace but break ReST; no code blocks produce valid ReST but may lose indentation in the chat display. The user may need to manually verify indentation after copying from Gemini.

**Validation technique:** Always validate ReST output with docutils before approving:
```bash
python3 -c "
import docutils.core, io
settings = {'report_level': 1, 'halt_level': 5, 'warning_stream': io.StringIO()}
docutils.core.publish_doctree(rst_text, settings_overrides=settings)
# Check warning_stream for errors
"
```

## Key Techniques (Reusable for Any Gemini Gem)

### 1. Do NOT Use Code Block Output for ReST
Earlier versions (v5) used code block output to preserve whitespace. This was proven WRONG: triple backticks are not valid ReST and cause parse errors. Instead:
- Explicitly forbid triple backticks in the instructions
- Tell the Gem the output will be pasted directly into a ReST parser
- Emphasize that every character matters and whitespace must be preserved
- Accept that Gemini's chat renderer may display indentation incorrectly — the raw text is what matters

**Exception:** If the output is NOT going into a ReST parser (e.g., Python code, YAML config), code blocks may still be appropriate. But for ReST output specifically, never use them.

### 2. Keep Instructions Short
Aim for under 7K characters. Long instructions cause the Gem to lose track of critical rules. Prioritize:
- A complete worked example (input → output)
- The 3-5 most critical rules stated explicitly
- A short final checklist

Cut verbose explanations. The worked example teaches more than 5 pages of rules.

### 3. Show WRONG vs RIGHT for Persistent Failures
When Gemini keeps producing a specific wrong pattern, show it explicitly:

```
WRONG — never do this:
`text [https://url](https://url)`_

CORRECT:
`text <https://url>`_
```

This is more effective than only showing the correct pattern, because Gemini needs to recognize its own mistake.

### 4. Use "IN EVERY PARAGRAPH" Language
Gemini may apply formatting rules only in certain contexts (e.g., only inside admonitions). Explicit global scope language fixes this:
- "in the main text AND inside admonitions"
- "Not just inside notes. EVERY paragraph."
- Checklist: "not just inside notes?"

### 5. Complete Worked Example with Real Data
Use a real ticket/input, not a synthetic example. Show:
- The exact input
- The exact correct output
- A "STUDY THE EXAMPLE" section pointing out each formatting decision

### 6. Final Checklist
End with a numbered checklist the Gem must run before outputting. Each item targets a specific failure mode:
1. Is output free of triple backticks and code blocks?
2. Are admonitions indented 4 spaces?
3. Any Markdown links remaining?
4. Any bare URLs?
5. Are key terms bolded in EVERY paragraph?
6. Any single backtick code?

### 7. Validate with docutils Before Approving
Never approve ReST output based on visual inspection alone. Run it through docutils to catch parse errors that aren't visible in chat rendering.

## Gemini-Specific Pitfalls

1. **Gemini defaults to Markdown** — It will mix Markdown into ReST if not explicitly forbidden. Show the exact wrong Markdown pattern and say "NEVER."

2. **Chat renderer strips whitespace** — Leading spaces on lines are eaten by the renderer unless inside a code block. This breaks any syntax that relies on indentation (ReST admonitions, Python, YAML). Without code blocks, the user must verify indentation manually after copying.

3. **Gemini interprets markup in instructions as formatting** — When instructions contain `**bold**`, Gemini may see "bold text" rather than "output the literal characters asterisk-asterisk-bold-asterisk-asterisk."

4. **Long instructions lose critical rules** — At 15K chars, the Gem followed some rules but lost others. At 6.5K, it followed all rules. Keep it short.

5. **Gemini only bolds in certain contexts** — Without explicit "EVERY paragraph" language, Gemini applied bold only inside admonitions, not in the main text.

6. **Gemini wraps URLs in Markdown even inside ReST** — It produced `` `text [url](url)`_ `` — a hybrid of ReST wrapper + Markdown URL. Must show this exact wrong pattern and forbid it.

7. **Code block output breaks ReST parsers** — Triple backticks (`` ``` ``) are Markdown, not ReST. They cause "Inline literal start-string without end-string" and "Possible incomplete section title" errors in docutils. Never use code block output for ReST that will be pasted into a ReST parser.

8. **Visual inspection is not validation** — ReST that looks correct in Gemini's chat may fail the parser. Always validate with docutils before approving.

## File Locations

- Gem instructions (current working version): `templates/gemini-gem-ticket-rewriter.txt`
- Workspace copy: `~/smarkets-api-support/gemini-gem-ticket-rewriter.txt`
- ReST syntax reference: https://wiki.typo3.org/ReST_Syntax
- ReST ticket template: `templates/erroneous-bet-outlier-response.rst`
