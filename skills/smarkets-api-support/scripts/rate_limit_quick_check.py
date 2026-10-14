#!/usr/bin/env python3
"""
Smarkets API — Quick Rate Limit Check
=====================================
Hits each endpoint once, captures X-RateLimit-* headers and per-endpoint
documented limits. Lightweight version of the full 4-phase discovery script.

The full discovery script (hammers endpoints until 429, tests shared pool)
lives at: ~/smarkets-api-support/scripts/rate_limit_discovery.py

Usage:
  python3 rate_limit_quick_check.py                          # public endpoints only
  python3 rate_limit_quick_check.py --email X --password Y   # all endpoints

Reference: references/rate-limits.md
"""
import requests, json, sys, argparse, time

BASE = "https://api.smarkets.com"
TIMEOUT = 15

# (id, method, path, auth, path_params, query_params, body, documented_limit)
ENDPOINTS = [
    ("POST /v3/sessions/", "POST", "/v3/sessions/", False, {}, {}, {"username":"x@x.invalid","password":"x"}, (5, 300)),
    ("POST /v3/sessions/verify/", "POST", "/v3/sessions/verify/", True, {}, {}, {"token":"x","code":"000000"}, None),
    ("DELETE /v3/sessions/", "DELETE", "/v3/sessions/", True, {}, {}, None, (30, 60)),
    ("GET /v3/events/", "GET", "/v3/events/", False, {}, {"limit": 1}, None, None),
    ("GET /v3/events/{ids}/states/", "GET", "/v3/events/{event_ids}/states/", False, {"event_ids":"1"}, {}, None, None),
    ("GET /v3/events/{ids}/competitors/", "GET", "/v3/events/{event_ids}/competitors/", False, {"event_ids":"1"}, {}, None, None),
    ("GET /v3/events/{ids}/markets/", "GET", "/v3/events/{event_ids}/markets/", False, {"event_ids":"1"}, {}, None, None),
    ("GET /v3/events/{ids}/markets_count/", "GET", "/v3/events/{event_ids}/markets_count/", False, {"event_ids":"1"}, {}, None, None),
    ("GET /v3/markets/{ids}/contracts/", "GET", "/v3/markets/{market_ids}/contracts/", False, {"market_ids":"1"}, {}, None, None),
    ("GET /v3/markets/{ids}/quotes/", "GET", "/v3/markets/{market_ids}/quotes/", True, {"market_ids":"1"}, {}, None, (50, 60)),
    ("GET /v3/markets/{ids}/last_executed_prices/", "GET", "/v3/markets/{market_ids}/last_executed_prices/", True, {"market_ids":"1"}, {}, None, None),
    ("GET /v3/markets/{ids}/volumes/", "GET", "/v3/markets/{market_ids}/volumes/", True, {"market_ids":"1"}, {}, None, None),
    ("GET /v3/orders/", "GET", "/v3/orders/", True, {}, {"limit": 1}, None, None),
    ("GET /v3/orders/fullcover/", "GET", "/v3/orders/fullcover/", True, {}, {"limit": 1}, None, None),
    ("POST /v3/orders/", "POST", "/v3/orders/", True, {}, {}, None, (10, 1)),
    ("DELETE /v3/orders/", "DELETE", "/v3/orders/", True, {}, {}, None, (1, 60)),
    ("DELETE /v3/orders/{id}/", "DELETE", "/v3/orders/{order_id}/", True, {"order_id":"00000000-0000-0000-0000-000000000000"}, {}, None, (10, 1)),
    ("GET /v3/accounts/", "GET", "/v3/accounts/", True, {}, {}, None, None),
    ("GET /v3/accounts/activity/", "GET", "/v3/accounts/activity/", True, {}, {"limit": 1}, None, None),
    ("GET /v3/account_activity_csv/", "GET", "/v3/account_activity_csv/{start_datetime}/{end_datetime}/", True, {"start_datetime":"2025-01-01T00:00:00Z","end_datetime":"2025-01-01T01:00:00Z"}, {}, None, None),
    ("GET /v3/currencies/{code}/", "GET", "/v3/currencies/{code}/", False, {"code":"EUR"}, {}, None, None),
]

def extract_rl(headers):
    rl = {}
    for k, v in headers.items():
        lk = k.lower()
        if lk == "x-ratelimit-limit": rl["limit"] = v
        elif lk == "x-ratelimit-remaining": rl["remaining"] = v
        elif lk == "x-ratelimit-reset": rl["reset"] = v
    return rl if rl else None

def main():
    p = argparse.ArgumentParser(description="Smarkets API Rate Limit Quick Check")
    p.add_argument("--email")
    p.add_argument("--password")
    args = p.parse_args()

    s = requests.Session()
    s.headers.update({"User-Agent": "SmarketsRateLimitCheck/1.0", "Content-Type": "application/json"})
    token = None

    if args.email and args.password:
        # API requires "username" key (value IS the email address).
        # OpenAPI spec: "username": {"format": "email", "example": "john.doe@company.com"}
        r = s.post(f"{BASE}/v3/sessions/", json={"username": args.email, "password": args.password}, timeout=TIMEOUT)
        if r.status_code == 200:
            token = r.json().get("session_token")
            if token:
                s.headers["Authorization"] = f"Session-Token {token}"
                print("Auth: OK\n")
        else:
            print(f"Auth: FAILED ({r.status_code})\n")

    print(f"{'ENDPOINT':<45} {'STATUS':>6}  {'DOC LIMIT':>14}  {'X-RateLimit HEADERS':>30}")
    print("─" * 100)

    for label, method, path, auth, pp, qp, body, doc in ENDPOINTS:
        url = f"{BASE}{path}"
        for k, v in pp.items():
            url = url.replace(f"{{{k}}}", str(v))

        if auth and not token:
            print(f"{label:<45} {'SKIP':>6}  {'—':>14}  {'no auth':>30}")
            continue

        # Remove auth for public endpoints
        saved = s.headers.pop("Authorization", None) if not auth else None
        try:
            r = s.request(method, url, params=qp or None, json=body, timeout=TIMEOUT)
            rl = extract_rl(dict(r.headers))
            doc_str = f"{doc[0]}/{doc[1]}s" if doc else "—"
            rl_str = str(rl) if rl else "—"
            elapsed = f"{r.elapsed.total_seconds()*1000:.0f}ms"
            print(f"{label:<45} {r.status_code:>6}  {doc_str:>14}  {rl_str:>30}  {elapsed}")
        except Exception as e:
            print(f"{label:<45} {'ERR':>6}  {str(e)[:40]}")
        finally:
            if saved:
                s.headers["Authorization"] = saved

    print("\n" + "─" * 100)
    print(f"Global limit: 1200 RPM across all endpoints (per account)")
    print(f"Full discovery script: ~/smarkets-api-support/scripts/rate_limit_discovery.py")
    print(f"Rate limit docs: references/rate-limits.md")

if __name__ == "__main__":
    main()
