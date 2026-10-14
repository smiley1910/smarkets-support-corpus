#!/usr/bin/env python3
"""
Live OpenAPI Spec Audit Tool — Smarkets example.

Extracts all error codes, auth requirements, and rate limits from a live
OpenAPI v3 spec for comparison against compiled docs.

Usage:
    curl -s -o /tmp/spec.json https://api.example.com/v0/openapi.json
    python3 live-spec-audit.py /tmp/spec.json

Customise for any API by changing the SPEC_URL and the report output.
"""

import json
import sys
from collections import defaultdict


def load_spec(path_or_url):
    with open(path_or_url) as f:
        return json.load(f)


def resolve_ref(ref_str, spec):
    """Resolve a JSON Reference ($ref) within the spec."""
    if not ref_str.startswith('#/'):
        return None
    parts = ref_str.lstrip('#/').split('/')
    obj = spec
    for p in parts:
        obj = obj.get(p, {})
    return obj if obj else None


def extract_endpoint_errors(method_detail, spec):
    """Extract all error codes from a single endpoint+method."""
    results = {}
    responses = method_detail.get('responses', {})

    for status_code, resp_obj in sorted(responses.items()):
        content = resp_obj.get('content', {})
        if 'application/json' not in content:
            continue

        schema = content['application/json'].get('schema', {})
        error_codes = []

        # Pattern 1: oneOf with $ref entries
        for option in schema.get('oneOf', []):
            ref = option.get('$ref')
            if ref:
                resolved = resolve_ref(ref, spec)
                if resolved:
                    enums = (resolved.get('properties', {})
                             .get('error_type', {})
                             .get('enum', []))
                    error_codes.extend(enums)

        # Pattern 2: direct $ref on schema
        ref = schema.get('$ref')
        if ref:
            resolved = resolve_ref(ref, spec)
            if resolved:
                enums = (resolved.get('properties', {})
                         .get('error_type', {})
                         .get('enum', []))
                if enums:
                    error_codes = enums  # direct ref replaces oneOf

        # Pattern 3: inline enum on error_type
        enums = (schema.get('properties', {})
                 .get('error_type', {})
                 .get('enum', []))
        if enums:
            error_codes = enums

        if error_codes:
            results[status_code] = sorted(set(error_codes))

    return results


def extract_rate_limits(method_detail):
    """Scrape rate limit info from description fields."""
    desc = method_detail.get('description', '') or ''
    notes = []
    for line in desc.split('<br>'):
        stripped = line.strip()
        if 'rate limit' in stripped.lower():
            notes.append(stripped)
    return '\n'.join(notes[:3])


def audit_spec(spec):
    """Produce a full audit report."""
    paths = spec.get('paths', {})
    print(f"=== OPENAPI SPEC AUDIT ===")
    print(f"Paths found: {len(paths)}\n")

    all_errors = defaultdict(set)
    per_endpoint = []

    for endpoint, methods in sorted(paths.items()):
        for method, detail in sorted(methods.items()):
            if method not in ('get', 'post', 'delete', 'put', 'patch'):
                continue

            summary = detail.get('summary', '')
            auth = 'YES' if detail.get('security') else 'NO'
            errors = extract_endpoint_errors(detail, spec)
            rl = extract_rate_limits(detail)

            key = f"{method.upper()} {endpoint}"
            for status, codes in errors.items():
                for c in codes:
                    all_errors[(status, c)].add(key)

            per_endpoint.append((key, auth, summary, errors, rl))

    # Print per-endpoint report
    for key, auth, summary, errors, rl in per_endpoint:
        print(f"\n--- {key} ---")
        print(f"  Auth: {auth} | {summary}")
        if rl:
            print(f"  Rate limit: {rl[:100]}")
        for status, codes in sorted(errors.items()):
            print(f"  {status}: {', '.join(codes)}")

    # Print master error list
    print("\n\n=== MASTER ERROR LIST (unique codes) ===")
    by_status = defaultdict(list)
    for (status, code), endpoints in sorted(all_errors.items()):
        by_status[status].append((code, endpoints))

    for status in sorted(by_status.keys()):
        print(f"\nHTTP {status}:")
        for code, endpoints in sorted(by_status[status]):
            eps = ', '.join(sorted(endpoints)[:3])
            print(f"  {code:<50s}  Appears in: {eps}")

    return all_errors, per_endpoint


def compare_docs(live_errors, doc_file_path):
    """
    Compare live errors against a local docs file.
    Reads the file and does a simple string-match for each error code.
    """
    print(f"\n\n=== COMPARISON AGAINST LOCAL DOCS ===")
    with open(doc_file_path) as f:
        doc_content = f.read()

    found = []
    missing = []

    for (status, code), endpoints in sorted(live_errors.items()):
        if code in doc_content:
            found.append((status, code))
        else:
            missing.append((status, code, endpoints))

    if missing:
        print(f"\nMISSING from local docs ({len(missing)} codes):")
        for status, code, eps in missing:
            print(f"  {status} {code:<45s} (in: {', '.join(sorted(eps))})")
    else:
        print("All live error codes are present in local docs.")

    return found, missing


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 live-spec-audit.py <openapi.json> [doc_to_check.md]")
        sys.exit(1)

    spec = load_spec(sys.argv[1])
    live_errors, _ = audit_spec(spec)

    if len(sys.argv) >= 3:
        compare_docs(live_errors, sys.argv[2])
