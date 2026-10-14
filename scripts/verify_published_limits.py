#!/usr/bin/env python3
"""Print the published limits, tier wording and 429 body shapes from a live spec.

Companion to live-spec-audit.py: that one audits a whole documentation set
(error codes, auth, categories); this one answers the narrow, recurring
question - "what may I tell a customer about rate limits?" - straight from the
live OpenAPI document, so no figure is ever quoted from a compiled note.

    python3 verify_published_limits.py --url https://api.example.com/openapi.json
    python3 verify_published_limits.py --url <spec> --json reports.json

Read-only: fetches one public URL, sends no credentials, places nothing.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.request


def fetch_spec(url: str, timeout: int = 60) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "api-docs-verify"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def plain(text: str) -> str:
    """OpenAPI descriptions are HTML fragments; flatten them to lines of text."""
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</(p|h[1-6]|li|div)>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text)


def spec_level_lines(spec: dict) -> list[str]:
    """Whatever the document says about limits/tiers outside individual routes."""
    desc = plain(spec.get("info", {}).get("description", ""))
    keys = ("rate limit", "requests per", "x-ratelimit", "api user", "quota", "throttl")
    out = []
    for line in desc.splitlines():
        line = " ".join(line.split())
        if line and any(k in line.lower() for k in keys):
            out.append(line)
    return out


def tier_notes(spec: dict) -> list[str]:
    notes = set()
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if not isinstance(op, dict):
                continue
            for line in plain(op.get("description") or "").splitlines():
                line = " ".join(line.split())
                if re.search(r"non-API users|need to be a .* API user|registered .* user", line, re.I):
                    notes.add(f"{method.upper()} {path}: {line}")
    return sorted(notes)


def route_caps(spec: dict) -> dict[str, list[str]]:
    caps = {}
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if not isinstance(op, dict):
                continue
            text = plain((op.get("description") or "") + "\n" + (op.get("summary") or ""))
            found = [
                " ".join(line.split())
                for line in text.splitlines()
                if re.search(r"(maximum|limit(ed)? to)\s+\d+\s+requests?\s+per", line, re.I)
            ]
            if found:
                caps[f"{method.upper()} {path}"] = found
    return caps


def error_shapes(spec: dict) -> dict[str, str]:
    """Which 429 bodies carry structured fields and which use an inline schema."""
    shapes = {}
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if not isinstance(op, dict):
                continue
            body = (op.get("responses") or {}).get("429")
            if not body:
                continue
            blob = json.dumps(body)
            if "$ref" in blob and "inline" not in blob.lower():
                shapes[f"{method.upper()} {path}"] = "referenced schema (resolve it before describing fields)"
            elif re.search(r"count|expiry|limit", blob):
                shapes[f"{method.upper()} {path}"] = "structured: count/limit/expiry present"
            else:
                shapes[f"{method.upper()} {path}"] = "inline: generic data field (no count/limit/expiry)"
    return shapes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True, help="live OpenAPI spec URL")
    ap.add_argument("--json", metavar="PATH", help="also write the report as JSON")
    args = ap.parse_args()

    spec = fetch_spec(args.url)
    report = {
        "source": args.url,
        "spec_title": spec.get("info", {}).get("title"),
        "spec_version": spec.get("info", {}).get("version"),
        "spec_level": spec_level_lines(spec),
        "tier_notes": tier_notes(spec),
        "per_route_caps": route_caps(spec),
        "rate_429_shapes": error_shapes(spec),
    }

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(report, fh, indent=2)

    print(f"spec: {report['spec_title']} v{report['spec_version']} ({args.url})\n")
    print("SPEC-LEVEL LIMIT / TIER TEXT")
    for line in report["spec_level"] or ["(none found)"]:
        print(f"  {line}")
    for note in report["tier_notes"]:
        print(f"  {note}")
    print("\nPER-ROUTE CAPS")
    for route, caps in sorted(report["per_route_caps"].items()):
        for cap in caps:
            print(f"  {route:52} {cap}")
    print("\n429 BODY SHAPE")
    for route, shape in sorted(report["rate_429_shapes"].items()):
        print(f"  {route:52} {shape}")

    if not report["per_route_caps"] and not report["spec_level"]:
        print(
            "\nWARNING: no limit text found - the spec may have changed shape; "
            "read it directly before quoting anything.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
