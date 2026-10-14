#!/usr/bin/env python3
"""
Verify the local OpenAPI spec copy against the live spec.
Reports differences in info.description and endpoint descriptions.

Usage: python3 scripts/verify_live_spec.py
Exit 0 if no differences, exit 1 if differences found.
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

LIVE_URL = "https://api.smarkets.com/v0/control/openapi/?tags=trading_api"
LOCAL_PATH = Path.home() / "smarkets-api-support" / "openapi" / "smarkets_openapi.json"

def fetch_live():
    try:
        req = urllib.request.Request(LIVE_URL, headers={"User-Agent": "smarkets-spec-verifier"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        print(f"ERROR: Could not fetch live spec: {e}")
        sys.exit(3)
    except json.JSONDecodeError as e:
        print(f"ERROR: Live spec response is not valid JSON: {e}")
        sys.exit(3)

def load_local():
    if not LOCAL_PATH.exists():
        print(f"ERROR: Local spec not found at {LOCAL_PATH}")
        sys.exit(2)
    with open(LOCAL_PATH) as f:
        return json.load(f)

def get_endpoint_descriptions(spec):
    """Extract all endpoint descriptions from paths."""
    descs = {}
    for path, methods in spec.get("paths", {}).items():
        for method, detail in methods.items():
            if method in ("get", "post", "put", "delete", "patch"):
                key = f"{method.upper()} {path}"
                d = detail.get("description", "")
                if d:
                    descs[key] = d
    return descs

def main():
    print("Fetching live spec...")
    live = fetch_live()
    print("Loading local spec...")
    local = load_local()

    diffs_found = False

    # 1. Compare info.description
    live_desc = live.get("info", {}).get("description", "")
    local_desc = local.get("info", {}).get("description", "")

    if live_desc != local_desc:
        diffs_found = True
        print("\n=== DIFF: info.description ===")
        if len(live_desc) > len(local_desc):
            extra = live_desc[len(local_desc):]
            print(f"Live spec has ADDITIONAL text not in local copy:")
            print(f"  {extra[:500]}...")
        elif len(live_desc) < len(local_desc):
            extra = local_desc[len(live_desc):]
            print(f"Local spec has text not in live spec:")
            print(f"  {extra[:500]}...")
        else:
            print("Descriptions differ in content (same length).")
            # Show first divergence
            for i, (a, b) in enumerate(zip(live_desc, local_desc)):
                if a != b:
                    print(f"  First difference at char {i}:")
                    print(f"  Live:  ...{live_desc[max(0,i-50):i+100]}...")
                    print(f"  Local: ...{local_desc[max(0,i-50):i+100]}...")
                    break

        # Check for specific known fields
        if "1200" in live_desc and "1200" not in local_desc:
            print("\n  WARNING: Live spec documents '1200 requests per 60 seconds' global limit")
            print("  but local copy does NOT contain this figure.")
            print("  The local spec is STALE — fetch the live spec before citing rate limits.")
    else:
        print("info.description: MATCH")

    # 2. Compare endpoint descriptions
    live_endpoints = get_endpoint_descriptions(live)
    local_endpoints = get_endpoint_descriptions(local)

    new_in_live = set(live_endpoints.keys()) - set(local_endpoints.keys())
    missing_from_live = set(local_endpoints.keys()) - set(live_endpoints.keys())

    if new_in_live:
        diffs_found = True
        print(f"\n=== Endpoints in LIVE but not in LOCAL: {len(new_in_live)} ===")
        for ep in sorted(new_in_live):
            print(f"  {ep}")

    if missing_from_live:
        diffs_found = True
        print(f"\n=== Endpoints in LOCAL but not in LIVE: {len(missing_from_live)} ===")
        for ep in sorted(missing_from_live):
            print(f"  {ep}")

    # Check for content differences in shared endpoints
    shared = set(live_endpoints.keys()) & set(local_endpoints.keys())
    content_diffs = []
    for ep in sorted(shared):
        if live_endpoints[ep] != local_endpoints[ep]:
            content_diffs.append(ep)

    if content_diffs:
        diffs_found = True
        print(f"\n=== Endpoint descriptions with content differences: {len(content_diffs)} ===")
        for ep in content_diffs:
            print(f"\n  {ep}:")
            # Check for rate limit mentions
            for label, desc in [("LIVE", live_endpoints[ep]), ("LOCAL", local_endpoints[ep])]:
                if "rate" in desc.lower() or "limit" in desc.lower() or "maximum" in desc.lower():
                    for line in desc.split("\n"):
                        if "rate" in line.lower() or "limit" in line.lower() or "maximum" in line.lower():
                            print(f"    {label}: {line.strip()}")

    # 3. Summary
    print("\n" + "=" * 60)
    if diffs_found:
        print("STALE: Local spec differs from live spec.")
        print("ACTION: Fetch live spec and update local copy:")
        print(f'  curl -sL "{LIVE_URL}" -o {LOCAL_PATH}')
        sys.exit(1)
    else:
        print("OK: Local spec matches live spec.")
        sys.exit(0)

if __name__ == "__main__":
    main()
