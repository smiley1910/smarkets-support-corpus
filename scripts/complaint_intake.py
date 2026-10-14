#!/usr/bin/env python3
"""Complaint intake triage for Smarkets/SBK.

Reads a complaint (file or stdin) and emits the intake output contract:
classification signals plus the exact Part B question blocks for the matched
classes, pulled from the single source of truth:
  ~/.hermes/skills/process/smarkets-ticket-writer/references/complaint-intake-questionnaire.md

Deterministic, stdlib only. No network, no writes.

Usage:
  python3 complaint_intake.py complaint.txt
  pbpaste | python3 complaint_intake.py -
  python3 complaint_intake.py --self-test
"""

from __future__ import annotations

import argparse
import os
import re
import sys

QUESTIONNAIRE = os.path.expanduser(
    "~/.hermes/skills/process/smarkets-ticket-writer/references/complaint-intake-questionnaire.md"
)

# class id -> (label, keywords). Keyword hits score the class.
CLASSES: dict[str, tuple[str, tuple[str, ...]]] = {
    "1": (
        "Settlement or result dispute",
        ("settled", "settlement", "wrong result", "incorrectly settled", "result was",
         "regrade", "payout", "paid out", "market was settled"),
    ),
    "2": (
        "Void, unvoid or reinstatement",
        ("void", "voided", "unvoid", "reinstate", "reinstated", "cancelled bet",
         "stake returned", "rebet", "re-bet", "re bet"),
    ),
    "3": (
        "Match market or market definition",
        ("90 minutes", "ninety minutes", "extra time", "penalties", "to advance",
         "match winner", "full time result", "1x2", "draw selection", "overall winner"),
    ),
    "4": (
        "Dead heat or multiples interaction",
        ("dead heat", "bet builder", "betbuilder", "accumulator", "acca", "multiple",
         "top 10", "top 5", "top 20", "each way", "place terms"),
    ),
    "5": (
        "Reduction factor",
        ("reduction factor", "withdrawn", "non runner", "non-runner", "nonrunner",
         "rule 4", "tattersalls", "price reduced", "horse racing"),
    ),
    "6": (
        "Non-standard match format",
        ("friendly", "quarters", "30 minute", "periods", "abandoned", "shortened",
         "format", "the match was played"),
    ),
    "7": (
        "Bet cancellation or stake error",
        ("cancel my bet", "cancel the bet", "wrong stake", "stake error", "mistake",
         "clearly erroneous", "input error", "typed", "cancel bet"),
    ),
    "8": (
        "Account restriction, verification, SoF or SoW",
        ("source of funds", "source of wealth", "sow", "sof", "verification",
         "verify", "restricted", "restriction", "blocked", "suspended", "kyc",
         "documents", "payslip", "bank statement", "affordability check"),
    ),
    "9": (
        "Payment or withdrawal",
        ("withdraw", "withdrawal", "deposit", "closed loop", "payment method",
         "my money", "payout to my bank", "skrill", "paypal", "card"),
    ),
    "10": (
        "Bonus or promotion",
        ("bonus", "promotion", "promo", "free bet", "offer terms", "welcome offer",
         "cashback", "commission offer", "0%"),
    ),
    "11": (
        "API technical",
        ("api", "endpoint", "401", "403", "429", "rate limit", "session token",
         "requests per", "forbidden", "unauthorized", "streaming", "websocket", "order"),
    ),
    "12": (
        "Unauthorised access or hacked account",
        ("hacked", "unauthorised", "unauthorized access", "someone logged in",
         "not me", "fraud", "stolen", "compromised", "cybercrime", "vpn"),
    ),
    "13": (
        "Reliance on live chat guidance",
        ("live chat", "chat agent", "your agent told me", "i was told", "advisor said",
         "support said", "confirmed by", "chat said"),
    ),
    "14": (
        "Social responsibility, affordability or duty of care",
        ("afford", "affordability", "duty of care", "social responsibility", "lccp",
         "ukgc", "gambling harm", "addiction", "vulnerable", "refund all my losses",
         "self exclude", "self-exclude", "resolution", "resolver", "solicitor",
         "ombudsman"),
    ),
    "15": (
        "Service complaint",
        ("poor service", "no response", "ignored", "waited", "delay", "still waiting",
         "unacceptable service", "complaint about your service"),
    ),
    "16": (
        "Complaint about handling",
        ("previous complaint", "still not resolved", "you already replied",
         "final response", "escalate", "investigate again"),
    ),
}

# Triage signals: (name, patterns, values)
PRODUCT_SIGNALS = (
    ("SBK sportsbook", ("sbk", "sportsbook", "accumulator", "bet builder", "getsbk")),
    ("Smarkets API", ("api", "endpoint", "session token", "v3/", "rate limit")),
    ("Smarkets exchange", ("exchange", "lay", "back the", "liability", "matched bet",
                           "commission", "trade out", "unmatched")),
)

STATUS_SIGNALS = (
    ("final response requested", ("final response", "final position", "my final")),
    ("formal complaint filed", ("formal complaint", "i want to complain",
                                "i wish to complain", "raising a complaint",
                                "i am complaining")),
    ("ADR named or filed", ("ibas", "ecogra", "mga", "maltese gaming",
                            "eu odr", "ombudsman", "adjudication")),
)

UK_HINTS = ("uk", "united kingdom", "england", "scotland", "wales", "northern ireland",
            "britain", "british", "gbp", "£")
EU_HINTS = ("ireland", "malta", "germany", "france", "spain", "italy", "netherlands",
            "portugal", "poland", "romania", "greece", "cyprus", "estonia", "latvia",
            "lithuania", "finland", "austria", "belgium", "croatia", "denmark",
            "hungary", "czech", "slovak", "slovenia", "bulgaria", "luxembourg")


def load_blocks(path: str) -> dict[str, str]:
    """Extract Part B class blocks keyed by class id ('1', '2', ... '16')."""
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        raise SystemExit(f"Cannot read questionnaire at {path}: {exc}")
    part_b = text.split("## Part B.", 1)
    body = part_b[1] if len(part_b) > 1 else text
    body = re.split(r"\n## Part C\.", body)[0]
    blocks: dict[str, str] = {}
    matches = list(re.finditer(r"^### ([\d and]+)\.\s*(.+)$", body, re.M))
    for i, m in enumerate(matches):
        ids = re.findall(r"\d+", m.group(1))
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chunk = body[m.start():end].rstrip()
        for cid in ids:
            blocks[cid] = chunk
    return blocks


def score_classes(text: str) -> list[tuple[int, str, list[str]]]:
    low = text.lower()
    scored = []
    for cid, (label, kws) in CLASSES.items():
        hits = [k for k in kws if k in low]
        if hits:
            scored.append((len(hits), cid, hits))
    scored.sort(key=lambda t: (-t[0], int(t[1])))
    return scored


def detect(text: str, signals) -> list[str]:
    low = text.lower()
    out = []
    for name, kws in signals:
        if any(k in low for k in kws):
            out.append(name)
    return out


def detect_jurisdiction(text: str) -> str:
    low = text.lower()
    if "sweden" in low or "swedish" in low or "sverige" in low or "svensk" in low:
        return "Sweden (16.4 MGA carve-out applies; route is eCOGRA and EU ODR)"
    if any(h in low for h in UK_HINTS):
        return "UK (route: IBAS, T&Cs 16.2)"
    if any(h in low for h in EU_HINTS):
        return "EU/EEA (route: eCOGRA, plus EU ODR under 16.5)"
    return "UNKNOWN - ask the customer; do not infer from timezone or league"


def main() -> int:
    ap = argparse.ArgumentParser(description="Smarkets/SBK complaint intake triage")
    ap.add_argument("path", nargs="?", default="-", help="complaint file, or - for stdin")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--questionnaire", default=QUESTIONNAIRE)
    args = ap.parse_args()

    blocks = load_blocks(args.questionnaire)

    if args.self_test:
        return self_test(blocks)

    text = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    if not text.strip():
        print("Empty complaint text.", file=sys.stderr)
        return 2

    products = detect(text, PRODUCT_SIGNALS) or ["UNCLEAR - ask which product"]
    statuses = detect(text, STATUS_SIGNALS) or ["first-line reply"]
    jurisdiction = detect_jurisdiction(text)
    scored = score_classes(text)

    if not scored:
        matched = ["(no class matched - classify manually against the class list)"]
        ids: list[str] = []
    else:
        ids = [cid for _, cid, _ in scored[:3]]
        matched = [f"{cid} {CLASSES[cid][0]} (hits: {', '.join(h)})" for _, cid, h in scored[:3]]

    print("=" * 68)
    print("COMPLAINT INTAKE TRIAGE")
    print("=" * 68)
    print("CLASSIFICATION")
    print(f"  Product:      {'; '.join(products)}")
    print(f"  Jurisdiction: {jurisdiction}")
    print(f"  Status:       {'; '.join(statuses)}")
    print("  Class:")
    for m in matched:
        print(f"    - {m}")
    print()
    print("ADR GATE (repeat to Michael, do not offer unless it applies):")
    print("  customer asked to complain/escalate, or Michael instructed, or final")
    print("  position on a filed complaint. A threat alone is not a request.")
    print()
    printed_blocks: set[str] = set()
    for cid in ids:
        chunk = blocks.get(cid, f"### {cid}. (block not found in questionnaire)")
        if chunk in printed_blocks:
            continue
        printed_blocks.add(chunk)
        print("-" * 68)
        print(chunk)
        print()
    print("-" * 68)
    print("THEN return the intake output contract and STOP: classification, questions")
    print("to Michael, optional customer questions, optional holding draft. No position,")
    print("no rule quote, no draft until the answers are in.")
    return 0


def self_test(blocks: dict[str, str]) -> int:
    failures = []
    if len(blocks) < 15:
        failures.append(f"expected at least 15 class blocks, found {len(blocks)}")
    for cid in ("1", "2", "11", "14"):
        if cid not in blocks:
            failures.append(f"missing class block {cid}")
    # classification sanity
    cases = [
        ("My accumulator on the golf was voided as a dead heat and you voided the whole bet",
         {"2", "4"}),
        ("I keep getting 429 on the quotes endpoint with my api session token", {"11"}),
        ("You should never have let me deposit, duty of care, refund all my losses", {"14"}),
        ("My horse was withdrawn and you reduced my price with rule 4", {"5"}),
    ]
    for text, want in cases:
        got = {cid for _, cid, _ in score_classes(text)[:3]}
        if not (want & got):
            failures.append(f"classify failed: wanted any of {want}, got {got} for {text!r}")
    if blocks.get("1") and "Settlement" not in blocks["1"]:
        failures.append("block 1 does not contain its heading")
    if failures:
        print("SELF-TEST FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"SELF-TEST PASSED: {len(blocks)} class blocks parsed, classification OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
