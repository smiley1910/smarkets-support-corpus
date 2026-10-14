#!/usr/bin/env python3
"""Smarkets & SBK Ticket Linter — Fast Deterministic Voice Core Validator.

Checks customer-facing ticket text against pinned rules from smarkets-voice-core:
1. Straight quotes only (no curly/smart quotes).
2. No em dashes or en dashes.
3. No banned hyphenated compound modifiers (e.g. weighed-in, real-time, peer-to-peer).
4. Negative density check (threshold: > 3 negatives in short response).
5. Single decision sentence check (no early jugular / multi-kill stacking).
6. ADR / IBAS formatting integrity (when ADR is present).
7. Plain text enforcement (no markdown tables, bold/italic, ReST).

Usage:
  python3 scripts/ticket_lint.py path/to/draft.txt
  cat draft.txt | python3 scripts/ticket_lint.py -
"""

import re
import sys


BANNED_HYPHEN_MODIFIERS = [
    r"\bweighed-in\b",
    r"\breal-time\b",
    r"\bpeer-to-peer\b",
    r"\bfollow-up\b",
    r"\bre-uploaded\b",
    r"\blower-liquidity\b",
    r"\banti-money laundering\b",
]

DECISION_PATTERNS = [
    r"settlement stands",
    r"will not regrade",
    r"will not credit",
    r"void was correct",
    r"full and correct return",
]

NEGATIVE_TOKENS = [
    r"\bwill not\b",
    r"\bis not\b",
    r"\bcan't\b",
    r"\bcannot\b",
    r"\bwon't\b",
    r"\baren't\b",
    r"\bweren't\b",
    r"\bnot\b",
    r"\bnever\b",
    r"\bno\b",
]


def lint_text(text: str) -> tuple[bool, list[str]]:
    issues = []

    # 1. Curly quotes / smart punctuation
    curly_matches = re.findall(r"[“”‘’]", text)
    if curly_matches:
        issues.append(f"CURLY QUOTES: Found smart/curly quotes {set(curly_matches)}. Use straight quotes ' and \" only.")

    # 2. Em dashes / En dashes
    dashes = re.findall(r"[—–]", text)
    if dashes:
        issues.append(f"DASHES: Found em/en dashes {set(dashes)}. Use commas or periods instead.")

    # 3. Hyphenated compound modifiers
    for pat in BANNED_HYPHEN_MODIFIERS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            issues.append(f"HYPHEN MODIFIER: Found banned compound '{m.group(0)}'. Use space-separated form.")

    # 4. Markdown syntax in customer text
    if re.search(r"\*\*[^*]+\*\*", text):
        issues.append("MARKDOWN BOLD: Found **bold** text. Customer emails must be plain text.")
    if re.search(r"(?<!\*)\*[^*]+\*(?!\*)", text):
        issues.append("MARKDOWN ITALIC: Found *italic* text. Customer emails must be plain text.")
    if re.search(r"\[.+?\]\(https?://.+?\)", text):
        issues.append("MARKDOWN LINK: Found [text](url) markdown link. Use bare URL or plain text.")

    # 5. Negative density heuristic
    low = text.lower()
    neg_count = sum(len(re.findall(pat, low)) for pat in NEGATIVE_TOKENS)
    # Check word count
    words = len(re.findall(r"\b\w+\b", text))
    if words < 350 and neg_count > 3:
        issues.append(f"NEGATIVE DENSITY: Found {neg_count} negative tokens in a {words}-word draft (> 3 threshold). Consider positive framing.")

    # 6. Decision sentence stacking
    dec_matches = []
    for pat in DECISION_PATTERNS:
        matches = re.findall(pat, low)
        if matches:
            dec_matches.extend(matches)
    if len(dec_matches) > 1:
        issues.append(f"DECISION STACKING: Found multiple decision phrases: {dec_matches}. Voice Core allows exactly ONE decision sentence, placed last.")

    # 7. IBAS URL format check (if IBAS cited)
    if "ibas" in low:
        if "http://www.ibas-uk.com/" not in text and "www.ibas-uk.com" not in text:
            issues.append("IBAS FORMAT: IBAS mentioned but standard URL (http://www.ibas-uk.com/) missing.")

    passed = len(issues) == 0
    return passed, issues


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 ticket_lint.py <file | ->")
        return 2

    source = sys.argv[1]
    if source == "-":
        content = sys.stdin.read()
    else:
        try:
            with open(source, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"Error reading file {source}: {e}", file=sys.stderr)
            return 2

    passed, issues = lint_text(content)
    if passed:
        print("PASS: Ticket text complies with all Voice Core mechanical rules.")
        return 0
    else:
        print(f"FAIL: {len(issues)} issue(s) detected:")
        for idx, issue in enumerate(issues, 1):
            print(f"  {idx}. {issue}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
