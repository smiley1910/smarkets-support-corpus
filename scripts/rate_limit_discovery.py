#!/usr/bin/env python3
"""
Smarkets API — Rate Limit Discovery Tool
=========================================
Discovers the per-endpoint and global rate limits for all 21 documented
endpoints in the Smarkets HTTP Trading API.

The docs (docs.smarkets.com OpenAPI spec) state:

  "All API users are subject to a default rate limit of 1200 requests per
   60 seconds across all endpoints, applied per account. Individual endpoints
   may have additional stricter limits as documented on each route below."

  Rate limit headers:
    X-RateLimit-Limit     — max requests in current window
    X-RateLimit-Remaining  — remaining in current window
    X-RateLimit-Reset     — seconds until window resets

  429 response body:
    {"error_type": "RATE_LIMIT_EXCEEDED",
     "data": {"count": N, "limit": N, "expiry": "ISO_TIMESTAMP"}}

This script:
  Phase 1 — Smoke test every endpoint (1 request each), capture headers + status
  Phase 2 — Probe each SAFE endpoint concurrently to discover its actual
             per-endpoint limit by sending requests until 429
  Phase 3 — Fire all endpoints simultaneously to test whether 1200 is a
             truly shared pool
  Phase 4 — Aggregate analysis: documented vs discovered, prints rate per
             endpoint, and how 1200 breaks down

Safety:
  - Does NOT place orders (POST /v3/orders/) — only reads
  - Does NOT cancel real orders (DELETE /v3/orders/{id}/) — uses fake UUID
  - Does NOT logout (DELETE /v3/sessions/) until the very end
  - Respects rate limit windows — waits for reset between probes
  - Uses public/no-auth endpoints for discovery where possible

Usage:
  python3 rate_limit_discovery.py --email USER@example.com --password PASS
  python3 rate_limit_discovery.py --email USER@example.com --password PASS --phase 1
  python3 rate_limit_discovery.py --email USER@example.com --password PASS --phase 2
  python3 rate_limit_discovery.py --email USER@example.com --password PASS --phase 3
  python3 rate_limit_discovery.py --email USER@example.com --password PASS --phase 4
  python3 rate_limit_discovery.py --dry-run

Requirements:
  pip install requests

Author: Michael Smyth
"""

import requests
import json
import os
import sys
import time
import argparse
import threading
from email.utils import parsedate_to_datetime
from collections import defaultdict
from datetime import datetime, timezone

BASE_URL = "https://api.smarkets.com"
TIMEOUT = 15
GLOBAL_LIMIT_RPM = 1200  # documented global limit
WINDOW_SECONDS = 60       # rate limit window

# Number of concurrent workers for Phase 2 hammering
HAMMER_THREADS = 10

# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────
# Each endpoint is defined with:
#   id: short identifier
#   method: HTTP method
#   path: path template (with {params})
#   auth: whether Session-Token is required
#   documented_limit: (requests, window_seconds) or None if not documented
#   safe_to_probe: whether we can hammer it without side effects
#   path_params: dict of param_name -> value to substitute
#   query_params: dict of query params
#   category: for grouping in output

ENDPOINTS = [
    # ── SESSIONS ───────────────────────────────────────────────────────────
    {
        "id": "POST_sessions",
        "method": "POST",
        "path": "/v3/sessions/",
        "auth": False,
        "documented_limit": (5, 300),       # 5 per 300 seconds
        "safe_to_probe": True,              # login attempts with bad creds, no side effects
        "path_params": {},
        "query_params": {},
        "body": {"username": "rate@test.invalid", "password": "INVALID"},
        "category": "Sessions",
    },
    {
        "id": "POST_sessions_verify",
        "method": "POST",
        "path": "/v3/sessions/verify/",
        "auth": True,
        "documented_limit": None,
        "safe_to_probe": True,              # will fail, no side effect
        "path_params": {},
        "query_params": {},
        "body": {"token": "invalid", "code": "000000"},
        "category": "Sessions",
    },
    {
        "id": "DELETE_sessions",
        "method": "DELETE",
        "path": "/v3/sessions/",
        "auth": True,
        "documented_limit": (30, 60),       # 30 per 60 seconds
        "safe_to_probe": False,             # would logout the session
        "path_params": {},
        "query_params": {},
        "body": None,
        "category": "Sessions",
    },

    # ── EVENTS (public, no auth) ───────────────────────────────────────────
    {
        "id": "GET_events",
        "method": "GET",
        "path": "/v3/events/",
        "auth": False,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {},
        "query_params": {"limit": 1},
        "body": None,
        "category": "Events",
    },
    {
        "id": "GET_events_states",
        "method": "GET",
        "path": "/v3/events/{event_ids}/states/",
        "auth": False,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {"event_ids": "1"},
        "query_params": {},
        "body": None,
        "category": "Events",
    },
    {
        "id": "GET_events_competitors",
        "method": "GET",
        "path": "/v3/events/{event_ids}/competitors/",
        "auth": False,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {"event_ids": "1"},
        "query_params": {},
        "body": None,
        "category": "Events",
    },
    {
        "id": "GET_events_markets",
        "method": "GET",
        "path": "/v3/events/{event_ids}/markets/",
        "auth": False,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {"event_ids": "1"},
        "query_params": {},
        "body": None,
        "category": "Events",
    },
    {
        "id": "GET_events_markets_count",
        "method": "GET",
        "path": "/v3/events/{event_ids}/markets_count/",
        "auth": False,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {"event_ids": "1"},
        "query_params": {},
        "body": None,
        "category": "Events",
    },

    # ── MARKETS ────────────────────────────────────────────────────────────
    {
        "id": "GET_markets_contracts",
        "method": "GET",
        "path": "/v3/markets/{market_ids}/contracts/",
        "auth": False,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {"market_ids": "1"},
        "query_params": {},
        "body": None,
        "category": "Markets",
    },
    {
        "id": "GET_markets_quotes",
        "method": "GET",
        "path": "/v3/markets/{market_ids}/quotes/",
        "auth": True,
        "documented_limit": (50, 60),       # 50 per 60 seconds
        "safe_to_probe": True,
        "path_params": {"market_ids": "1"},
        "query_params": {},
        "body": None,
        "category": "Prices",
    },
    {
        "id": "GET_markets_last_executed_prices",
        "method": "GET",
        "path": "/v3/markets/{market_ids}/last_executed_prices/",
        "auth": True,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {"market_ids": "1"},
        "query_params": {},
        "body": None,
        "category": "Prices",
    },
    {
        "id": "GET_markets_volumes",
        "method": "GET",
        "path": "/v3/markets/{market_ids}/volumes/",
        "auth": True,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {"market_ids": "1"},
        "query_params": {},
        "body": None,
        "category": "Markets",
    },

    # ── ORDERS (auth required) ─────────────────────────────────────────────
    {
        "id": "GET_orders",
        "method": "GET",
        "path": "/v3/orders/",
        "auth": True,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {},
        "query_params": {"limit": 1},
        "body": None,
        "category": "Orders",
    },
    {
        "id": "GET_orders_fullcover",
        "method": "GET",
        "path": "/v3/orders/fullcover/",
        "auth": True,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {},
        "query_params": {"limit": 1},
        "body": None,
        "category": "Orders",
    },
    {
        "id": "POST_orders",
        "method": "POST",
        "path": "/v3/orders/",
        "auth": True,
        "documented_limit": (10, 1),        # 10 per second (600 per 60s)
        "safe_to_probe": False,             # would place real orders
        "path_params": {},
        "query_params": {},
        "body": None,
        "category": "Orders",
    },
    {
        "id": "DELETE_orders_all",
        "method": "DELETE",
        "path": "/v3/orders/",
        "auth": True,
        "documented_limit": (1, 60),        # 1 per 60 seconds
        "safe_to_probe": False,             # would cancel real orders
        "path_params": {},
        "query_params": {},
        "body": None,
        "category": "Orders",
    },
    {
        "id": "DELETE_orders_single",
        "method": "DELETE",
        "path": "/v3/orders/{order_id}/",
        "auth": True,
        "documented_limit": (10, 1),        # 10 per second (600 per 60s)
        "safe_to_probe": True,              # fake UUID, will 404 but still hits rate limiter
        "path_params": {"order_id": "00000000-0000-0000-0000-000000000000"},
        "query_params": {},
        "body": None,
        "category": "Orders",
    },

    # ── ACCOUNTS (auth required) ───────────────────────────────────────────
    {
        "id": "GET_accounts",
        "method": "GET",
        "path": "/v3/accounts/",
        "auth": True,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {},
        "query_params": {},
        "body": None,
        "category": "Accounts",
    },
    {
        "id": "GET_accounts_activity",
        "method": "GET",
        "path": "/v3/accounts/activity/",
        "auth": True,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {},
        "query_params": {"limit": 1},
        "body": None,
        "category": "Accounts",
    },
    {
        "id": "GET_account_activity_csv",
        "method": "GET",
        "path": "/v3/account_activity_csv/{start_datetime}/{end_datetime}/",
        "auth": True,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {
            "start_datetime": "2025-01-01T00:00:00Z",
            "end_datetime": "2025-01-01T01:00:00Z",
        },
        "query_params": {},
        "body": None,
        "category": "Accounts",
    },

    # ── CURRENCIES (public) ────────────────────────────────────────────────
    {
        "id": "GET_currencies",
        "method": "GET",
        "path": "/v3/currencies/{code}/",
        "auth": False,
        "documented_limit": None,
        "safe_to_probe": True,
        "path_params": {"code": "EUR"},
        "query_params": {},
        "body": None,
        "category": "Currencies",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def doc_limit_to_rpm(doc_limit):
    """Convert a (count, window_seconds) tuple to RPM."""
    if not doc_limit:
        return None
    count, window = doc_limit
    return count * (60.0 / window)


def doc_limit_str(doc_limit):
    """Format a documented limit for display."""
    if not doc_limit:
        return "—"
    count, window = doc_limit
    rpm = doc_limit_to_rpm(doc_limit)
    if window == 1:
        return f"{count}/s ({rpm:.0f}rpm)"
    elif window == 60:
        return f"{count}/min ({rpm:.0f}rpm)"
    else:
        return f"{count}/{window}s ({rpm:.0f}rpm)"


def build_url(endpoint):
    """Build URL from endpoint template + path params."""
    path = endpoint["path"]
    for key, val in endpoint.get("path_params", {}).items():
        path = path.replace(f"{{{key}}}", str(val))
    return f"{BASE_URL}{path}"


def extract_rate_headers(headers):
    """Extract X-RateLimit-* headers (case-insensitive)."""
    result = {}
    for key, val in headers.items():
        lk = key.lower()
        if lk == "x-ratelimit-limit":
            result["limit"] = val
        elif lk == "x-ratelimit-remaining":
            result["remaining"] = val
        elif lk == "x-ratelimit-reset":
            result["reset"] = val
    return result if result else None


def make_single_request(endpoint, token=None, session=None):
    """Make a single HTTP request. Returns (status, headers_dict, body_str, elapsed_ms).

    Uses the provided requests.Session if given, otherwise creates a new one.
    This is thread-safe when each thread passes its own session.
    """
    url = build_url(endpoint)
    method = endpoint["method"]
    params = endpoint.get("query_params") or None
    body = endpoint.get("body") if method in ("POST", "PUT", "PATCH") else None

    s = session or requests.Session()
    headers = {}
    if endpoint.get("auth") and token:
        headers["Authorization"] = f"Session-Token {token}"
    headers["User-Agent"] = "SmarketsRateLimitDiscovery/1.0"
    if body is not None:
        headers["Content-Type"] = "application/json"

    r = s.request(method, url, params=params, json=body, headers=headers,
                  timeout=TIMEOUT, allow_redirects=False)
    elapsed_ms = round(r.elapsed.total_seconds() * 1000, 1)
    return r.status_code, dict(r.headers), r.text[:500], elapsed_ms


# ─────────────────────────────────────────────────────────────────────────────
# CORE CLIENT (for auth + Phase 1)
# ─────────────────────────────────────────────────────────────────────────────

class SmarketsClient:
    """Handles auth and single requests for Phase 1."""

    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password
        self.token = None

    def login(self):
        """Authenticate and get session token."""
        try:
            r = requests.post(
                f"{BASE_URL}/v3/sessions/",
                json={"username": self.email, "password": self.password},
                headers={"User-Agent": "SmarketsRateLimitDiscovery/1.0"},
                timeout=TIMEOUT,
                allow_redirects=False,
            )
        except requests.exceptions.RequestException as e:
            print(f"  Login failed: network error — {e}")
            return False
        if r.status_code in (200, 201):
            try:
                data = r.json()
            except (json.JSONDecodeError, ValueError):
                print(f"  Login failed: {r.status_code} but response is not JSON")
                return False
            self.token = data.get("token")
            if self.token:
                return True
            print(f"  Login failed: {r.status_code} but no token in response")
            return False
        print(f"  Login failed: {r.status_code}")
        return False

    def make_request(self, endpoint):
        """Make a single request using the client's token."""
        return make_single_request(endpoint, token=self.token)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1: SMOKE TEST — single request to each endpoint
# ─────────────────────────────────────────────────────────────────────────────

def phase1_smoke_test(client, dry_run=False):
    """Hit every endpoint once, capture status + rate limit headers."""
    print("\n" + "=" * 78)
    print("  PHASE 1: SMOKE TEST — one request per endpoint")
    print("=" * 78)

    results = []
    for ep in ENDPOINTS:
        print(f"\n  [{ep['id']}] {ep['method']} {ep['path']}")

        # Show documented limit
        doc = ep.get("documented_limit")
        if doc:
            print(f"    Documented limit: {doc_limit_str(doc)}")
        else:
            print(f"    Documented limit: NONE")

        if ep.get("auth") and not client.token:
            print(f"    SKIP: auth required, no token")
            results.append({
                "endpoint": ep["id"], "method": ep["method"], "path": ep["path"],
                "status": "SKIPPED_NO_AUTH",
                "documented_limit": doc,
                "documented_rpm": doc_limit_to_rpm(doc),
                "rate_headers": None,
            })
            continue

        if dry_run:
            url = build_url(ep)
            print(f"    DRY RUN: would {ep['method']} {url}")
            results.append({
                "endpoint": ep["id"], "method": ep["method"], "path": ep["path"],
                "status": "DRY_RUN",
                "documented_limit": doc,
                "documented_rpm": doc_limit_to_rpm(doc),
                "rate_headers": None,
            })
            continue

        try:
            status, headers, body, elapsed = client.make_request(ep)
            rate_hdrs = extract_rate_headers(headers)
            print(f"    → {status} ({elapsed}ms)")
            if rate_hdrs:
                print(f"    RateLimit headers: limit={rate_hdrs.get('limit')} "
                      f"remaining={rate_hdrs.get('remaining')} "
                      f"reset={rate_hdrs.get('reset')}s")
            else:
                print(f"    RateLimit headers: none returned")
            if status == 429:
                print(f"    ⚠️  ALREADY RATE LIMITED")
                try:
                    err = json.loads(body)
                    print(f"    Error data: {json.dumps(err, indent=2)}")
                except Exception:
                    pass
            results.append({
                "endpoint": ep["id"],
                "method": ep["method"],
                "path": ep["path"],
                "status": status,
                "elapsed_ms": elapsed,
                "rate_headers": rate_hdrs,
                "auth_required": ep.get("auth", False),
                "documented_limit": doc,
                "documented_rpm": doc_limit_to_rpm(doc),
                "body_preview": body[:200],
            })
        except Exception as e:
            print(f"    ✗ ERROR: {e}")
            results.append({
                "endpoint": ep["id"], "method": ep["method"], "path": ep["path"],
                "status": "ERROR", "error": str(e),
                "documented_limit": doc,
                "documented_rpm": doc_limit_to_rpm(doc),
                "rate_headers": None,
            })

    return results


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2: PER-ENDPOINT PROBE — concurrent hammer until 429
# ─────────────────────────────────────────────────────────────────────────────

def phase2_probe_endpoints(client, dry_run=False):
    """For each safe-to-probe endpoint, fire concurrent requests until 429."""
    print("\n" + "=" * 78)
    print(f"  PHASE 2: PER-ENDPOINT PROBE — concurrent discovery ({HAMMER_THREADS} threads)")
    print("  Strategy: hammer each safe endpoint until 429, then wait for reset")
    print("=" * 78)

    results = []
    safe_endpoints = [e for e in ENDPOINTS if e.get("safe_to_probe")]

    for ep in safe_endpoints:
        ep_id = ep["id"]
        doc_limit = ep.get("documented_limit")

        print(f"\n  ── Probing: {ep_id} ──")
        print(f"     {ep['method']} {ep['path']}")
        print(f"     Documented: {doc_limit_str(doc_limit)}")
        print(f"     Auth: {'yes' if ep.get('auth') else 'no'}")

        if dry_run:
            print(f"     DRY RUN: would hammer with {HAMMER_THREADS} threads until 429")
            results.append({
                "endpoint": ep_id,
                "method": ep["method"],
                "path": ep["path"],
                "documented_limit": doc_limit,
                "documented_rpm": doc_limit_to_rpm(doc_limit),
                "discovered_limit": None,
                "status": "DRY_RUN",
            })
            continue

        if ep.get("auth") and not client.token:
            print(f"     SKIP: auth required, no token")
            results.append({
                "endpoint": ep_id,
                "method": ep["method"],
                "path": ep["path"],
                "documented_limit": doc_limit,
                "documented_rpm": doc_limit_to_rpm(doc_limit),
                "status": "SKIPPED_NO_AUTH",
            })
            continue

        # ── Concurrent hammer ──────────────────────────────────────────────
        request_count = 0
        success_count = 0
        error_count = 0
        first_429 = None
        rate_headers_last = None
        error_429_data = None
        max_requests = 1300  # safety cap: 1200 + buffer
        start_time = time.time()

        lock = threading.Lock()
        stop_flag = threading.Event()

        def hammer():
            nonlocal request_count, success_count, error_count
            nonlocal first_429, rate_headers_last, error_429_data
            # Each thread gets its own session (thread-safe)
            local_session = requests.Session()
            try:
                while not stop_flag.is_set():
                    with lock:
                        if request_count >= max_requests:
                            return
                        if first_429 is not None:
                            return
                    try:
                        status, headers, body, elapsed = make_single_request(
                            ep, token=client.token, session=local_session
                        )
                        with lock:
                            request_count += 1
                            rh = extract_rate_headers(headers)
                            if rh:
                                rate_headers_last = rh
                            if status == 429:
                                if first_429 is None:
                                    first_429 = request_count
                                if error_429_data is None:
                                    try:
                                        err = json.loads(body)
                                        error_429_data = err.get("data", err)
                                    except Exception:
                                        error_429_data = {"raw": body[:200]}
                                stop_flag.set()
                                return
                            elif status in (200, 404, 400, 401, 403):
                                success_count += 1
                            else:
                                error_count += 1
                    except requests.exceptions.ConnectionError:
                        with lock:
                            error_count += 1
                        time.sleep(0.1)
                    except Exception:
                        with lock:
                            error_count += 1
                        time.sleep(0.05)
            finally:
                local_session.close()

        threads = [threading.Thread(target=hammer, daemon=True) for _ in range(HAMMER_THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=120)

        stop_flag.set()
        elapsed_total = time.time() - start_time
        discovered_rpm = round(request_count / (elapsed_total / 60), 0) if elapsed_total > 0 else None

        result = {
            "endpoint": ep_id,
            "method": ep["method"],
            "path": ep["path"],
            "documented_limit": doc_limit,
            "documented_rpm": doc_limit_to_rpm(doc_limit),
            "requests_sent": request_count,
            "successful_requests": success_count,
            "error_requests": error_count,
            "first_429_at": first_429,
            "error_429_data": error_429_data,
            "last_rate_headers": rate_headers_last,
            "elapsed_seconds": round(elapsed_total, 2),
            "discovered_rpm": discovered_rpm,
        }
        results.append(result)

        print(f"     Requests: {request_count} in {elapsed_total:.1f}s"
              f"{' (' + format(discovered_rpm, '.0f') + ' rpm effective)' if discovered_rpm is not None else ''}")
        if first_429:
            print(f"     First 429 at: request #{first_429}")
            if error_429_data:
                print(f"     429 data: {json.dumps(error_429_data)}")
            if rate_headers_last:
                print(f"     Last rate headers: {rate_headers_last}")
        else:
            print(f"     No 429 (hit safety cap of {max_requests})")
            if rate_headers_last:
                print(f"     Rate headers: {rate_headers_last}")

        # ── Wait for rate limit window reset ───────────────────────────────
        wait_time = 5  # default short pause
        if first_429:
            # Use X-RateLimit-Reset header if available
            if rate_headers_last and rate_headers_last.get("reset"):
                try:
                    wait_time = max(int(rate_headers_last["reset"]) + 3, 5)
                except (ValueError, TypeError):
                    wait_time = 65
            # Use 429 error expiry if available
            elif error_429_data and isinstance(error_429_data, dict):
                expiry = error_429_data.get("expiry")
                if expiry:
                    try:
                        # expiry is RFC 2822 format (e.g. "Thu, 16 Jul 2026 11:21:18 GMT")
                        exp_dt = parsedate_to_datetime(expiry)
                        now_dt = datetime.now(timezone.utc)
                        wait_time = max(int((exp_dt - now_dt).total_seconds()) + 3, 5)
                    except Exception:
                        wait_time = 65
                else:
                    limit_val = error_429_data.get("limit")
                    if limit_val and doc_limit:
                        # Use documented window as fallback
                        wait_time = doc_limit[1] + 3
                    else:
                        wait_time = 65
            else:
                # Use documented window as fallback
                if doc_limit:
                    wait_time = doc_limit[1] + 3
                else:
                    wait_time = 65

        if wait_time > 3:
            print(f"     Waiting {wait_time}s for rate limit window reset...")
            time.sleep(wait_time)
        else:
            time.sleep(wait_time)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3: SHARED POOL TEST — fire all endpoints simultaneously
# ─────────────────────────────────────────────────────────────────────────────

def phase3_shared_pool_test(client, dry_run=False):
    """Test whether the 1200 RPM is a truly shared pool by hitting all endpoints concurrently."""
    print("\n" + "=" * 78)
    print("  PHASE 3: SHARED POOL TEST — concurrent requests across all endpoints")
    print("  Goal: determine if 1200 RPM is shared or per-endpoint")
    print("=" * 78)

    test_endpoints = [
        e for e in ENDPOINTS
        if e.get("safe_to_probe")
        and e["id"] not in ("DELETE_sessions", "POST_sessions", "POST_sessions_verify")
        and (not e.get("auth") or client.token)
    ]

    print(f"\n  Endpoints in concurrent test: {len(test_endpoints)}")
    for ep in test_endpoints:
        print(f"    • {ep['id']}")

    if dry_run:
        print(f"\n  DRY RUN: would fire all endpoints concurrently")
        return None

    total_requests = 0
    total_429 = 0
    total_errors = 0
    per_endpoint_counts = defaultdict(lambda: {"sent": 0, "ok": 0, "rate_limited": 0, "errors": 0})
    global_429_at = None
    last_rate_headers = None
    start = time.time()

    lock = threading.Lock()
    stop_flag = threading.Event()
    max_total = 1300

    def hammer_endpoint(ep):
        nonlocal total_requests, total_429, total_errors, global_429_at, last_rate_headers
        ep_id = ep["id"]
        # Each thread gets its own session (thread-safe)
        local_session = requests.Session()
        try:
            while not stop_flag.is_set():
                with lock:
                    if per_endpoint_counts[ep_id]["sent"] >= 500:
                        return
                try:
                    status, headers, body, elapsed = make_single_request(
                        ep, token=client.token, session=local_session
                    )
                    with lock:
                        total_requests += 1
                        per_endpoint_counts[ep_id]["sent"] += 1

                        rh = extract_rate_headers(headers)
                        if rh:
                            last_rate_headers = rh

                        if status == 429:
                            total_429 += 1
                            per_endpoint_counts[ep_id]["rate_limited"] += 1
                            if global_429_at is None:
                                global_429_at = total_requests
                            try:
                                err = json.loads(body)
                                if "data" in err:
                                    print(f"\n  [{ep_id}] 429 — "
                                          f"count={err['data'].get('count')} "
                                          f"limit={err['data'].get('limit')} "
                                          f"expiry={err['data'].get('expiry')}")
                            except Exception:
                                pass
                        elif status in (200, 404, 400, 403):
                            per_endpoint_counts[ep_id]["ok"] += 1

                        if total_requests >= max_total:
                            stop_flag.set()
                            return
                except requests.exceptions.ConnectionError:
                    with lock:
                        total_errors += 1
                        per_endpoint_counts[ep_id]["errors"] += 1
                    time.sleep(0.1)
                except Exception:
                    with lock:
                        total_errors += 1
                        per_endpoint_counts[ep_id]["errors"] += 1
                    time.sleep(0.05)
        finally:
            local_session.close()

    threads = []
    for ep in test_endpoints:
        t = threading.Thread(target=hammer_endpoint, args=(ep,), daemon=True)
        threads.append(t)
        t.start()

    deadline = time.time() + 70
    while time.time() < deadline and not stop_flag.is_set():
        time.sleep(1)

    stop_flag.set()
    for t in threads:
        t.join(timeout=5)

    elapsed = time.time() - start

    print(f"\n  ── Shared Pool Test Results ──")
    print(f"  Total requests sent: {total_requests}")
    print(f"  Total 429s: {total_429}")
    print(f"  Total errors: {total_errors}")
    print(f"  First 429 at request: #{global_429_at}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"  Effective rate: {total_requests / elapsed * 60:.0f} rpm" if elapsed > 0 else "")
    if last_rate_headers:
        print(f"  Last rate headers: {last_rate_headers}")
    print(f"\n  Per-endpoint breakdown:")
    for ep_id, counts in sorted(per_endpoint_counts.items()):
        print(f"    {ep_id:45s} sent={counts['sent']:4d}  ok={counts['ok']:4d}  "
              f"429={counts['rate_limited']:4d}  err={counts['errors']:4d}")

    return {
        "total_requests": total_requests,
        "total_429s": total_429,
        "total_errors": total_errors,
        "first_429_at": global_429_at,
        "elapsed_seconds": round(elapsed, 1),
        "per_endpoint": dict(per_endpoint_counts),
        "last_rate_headers": last_rate_headers,
    }


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4: AGGREGATE ANALYSIS — prints rate per endpoint
# ─────────────────────────────────────────────────────────────────────────────

def phase4_analysis(phase1_results, phase2_results, phase3_results=None):
    """Compile all findings into a summary showing how 1200 RPM breaks down."""
    print("\n" + "=" * 78)
    print("  PHASE 4: AGGREGATE ANALYSIS")
    print("=" * 78)

    print(f"\n  Documented global limit: {GLOBAL_LIMIT_RPM} RPM (per account)")

    # Build lookups
    p1_lookup = {r["endpoint"]: r for r in phase1_results if isinstance(r, dict) and "endpoint" in r}
    p2_lookup = {r["endpoint"]: r for r in phase2_results if isinstance(r, dict) and "endpoint" in r}

    # ── Per-endpoint rate summary table ───────────────────────────────────
    print(f"\n  ┌{'─'*100}┐")
    print(f"  │ {'ENDPOINT':<40} {'AUTH':>4} {'DOC LIMIT':>16} {'DOC RPM':>7} {'DISCOVERED':>11} {'DISC RPM':>8} {'HEADERS':>7} │")
    print(f"  ├{'─'*100}┤")

    total_documented_rpm = 0
    endpoints_with_headers = 0
    endpoints_probed = 0

    for ep in ENDPOINTS:
        ep_id = ep["id"]
        doc = ep.get("documented_limit")
        doc_rpm = doc_limit_to_rpm(doc)
        if doc_rpm:
            total_documented_rpm += doc_rpm

        auth_str = "yes" if ep.get("auth") else "no"
        doc_str = doc_limit_str(doc)
        doc_rpm_str = f"{doc_rpm:.0f}" if doc_rpm is not None else "—"

        # Discovered info from Phase 2
        p2 = p2_lookup.get(ep_id, {})
        p1 = p1_lookup.get(ep_id, {})

        if p2.get("first_429_at"):
            disc_str = f"429@#{p2['first_429_at']}"
            disc_rpm = p2.get("discovered_rpm")
            disc_rpm_str = f"{disc_rpm:.0f}" if disc_rpm is not None else "—"
            endpoints_probed += 1
        elif p2.get("requests_sent"):
            disc_str = f"no 429 ({p2['requests_sent']})"
            disc_rpm = p2.get("discovered_rpm")
            disc_rpm_str = f"{disc_rpm:.0f}" if disc_rpm is not None else "—"
            endpoints_probed += 1
        elif p2.get("status") == "SKIPPED_NO_AUTH":
            disc_str = "no auth"
            disc_rpm_str = "—"
        elif p2.get("status") == "DRY_RUN":
            disc_str = "dry run"
            disc_rpm_str = "—"
        elif not ep.get("safe_to_probe"):
            disc_str = "unsafe"
            disc_rpm_str = "—"
        else:
            disc_str = "—"
            disc_rpm_str = "—"

        # Rate headers
        rh = p2.get("last_rate_headers") or p1.get("rate_headers")
        hdr_str = "yes" if rh else "no"
        if rh:
            endpoints_with_headers += 1

        print(f"  │ {ep_id:<40} {auth_str:>4} {doc_str:>16} {doc_rpm_str:>7} {disc_str:>11} {disc_rpm_str:>8} {hdr_str:>7} │")

    print(f"  ├{'─'*100}┤")
    print(f"  │ {'SUMMARY':<40} {'':>4} {'':>16} {total_documented_rpm:>7.0f} {'':>11} {'':>8} {endpoints_with_headers:>7} │")
    print(f"  │ {'Endpoints probed:':<40} {endpoints_probed:>4} {'':>16} {'':>7} {'':>11} {'':>8} {'':>7} │")
    print(f"  │ {'Endpoints with per-endpoint limit:':<40} {len([e for e in ENDPOINTS if e.get('documented_limit')]):>4} {'':>16} {'':>7} {'':>11} {'':>8} {'':>7} │")
    print(f"  │ {'Endpoints WITHOUT per-endpoint limit:':<40} {len([e for e in ENDPOINTS if not e.get('documented_limit')]):>4} {'':>16} {'':>7} {'':>11} {'':>8} {'':>7} │")
    print(f"  └{'─'*100}┘")

    # ── Rate header details ────────────────────────────────────────────────
    print(f"\n  ── Rate Limit Headers Detail ──")
    any_headers = False
    for ep in ENDPOINTS:
        ep_id = ep["id"]
        p2 = p2_lookup.get(ep_id, {})
        p1 = p1_lookup.get(ep_id, {})
        rh = p2.get("last_rate_headers") or p1.get("rate_headers")
        if rh:
            any_headers = True
            print(f"    {ep_id}: limit={rh.get('limit')} remaining={rh.get('remaining')} reset={rh.get('reset')}s")
    if not any_headers:
        print(f"    No X-RateLimit-* headers observed on any endpoint.")
        print(f"    Public endpoints (no auth) do not return rate limit headers.")
        print(f"    Authenticated endpoints may only return them when approaching limits.")

    # ── Documented vs global analysis ─────────────────────────────────────
    print(f"\n  ── Documented Limits vs Global Pool ──")
    print(f"    Sum of documented per-endpoint limits: {total_documented_rpm:.0f} rpm")
    print(f"    Global pool limit:                     {GLOBAL_LIMIT_RPM} rpm")

    documented = [e for e in ENDPOINTS if e.get("documented_limit")]
    undocumented = [e for e in ENDPOINTS if not e.get("documented_limit")]

    print(f"    Endpoints with per-endpoint limits:    {len(documented)}")
    print(f"    Endpoints without per-endpoint limits: {len(undocumented)}")

    if total_documented_rpm > GLOBAL_LIMIT_RPM:
        print(f"\n    ⚠️  Documented per-endpoint limits ({total_documented_rpm:.0f}) EXCEED global pool ({GLOBAL_LIMIT_RPM})")
        print(f"       Per-endpoint limits are concurrent caps, not additive allocations.")
        print(f"       The 1200 global pool is the true ceiling; per-endpoint limits")
        print(f"       are additional restrictions that fire BEFORE the global limit.")
        print(f"       You cannot max out all per-endpoint limits simultaneously.")
    else:
        remaining = GLOBAL_LIMIT_RPM - total_documented_rpm
        print(f"\n    Remaining in global pool for undocumented endpoints: {remaining:.0f} rpm")
        if undocumented:
            per_undoc = remaining / len(undocumented)
            print(f"    If evenly split across {len(undocumented)} undocumented endpoints: ~{per_undoc:.0f} rpm each")

    # ── Phase 3 shared pool analysis ───────────────────────────────────────
    if phase3_results and isinstance(phase3_results, dict):
        print(f"\n  ── Shared Pool Test (Phase 3) ──")
        first_429 = phase3_results.get("first_429_at")
        total_req = phase3_results.get("total_requests", 0)
        elapsed = phase3_results.get("elapsed_seconds", 0)
        print(f"    Total concurrent requests: {total_req} in {elapsed}s")
        print(f"    First 429 at request: #{first_429}" if first_429 else "    No 429 received")
        if first_429 and first_429 < GLOBAL_LIMIT_RPM:
            print(f"    ⚠️  Hit 429 at {first_429} — BELOW documented {GLOBAL_LIMIT_RPM}")
            print(f"       Per-endpoint limits fired before global pool exhausted.")
        elif first_429 and first_429 >= GLOBAL_LIMIT_RPM:
            print(f"    ✓  Hit 429 at {first_429} — AT or ABOVE documented {GLOBAL_LIMIT_RPM}")
            print(f"       Confirms 1200 RPM is a shared global pool.")

    # ── Final per-endpoint rate list ───────────────────────────────────────
    print(f"\n  ── Per-Endpoint Rate Summary ──")
    for ep in ENDPOINTS:
        ep_id = ep["id"]
        doc = ep.get("documented_limit")
        doc_rpm = doc_limit_to_rpm(doc)
        p2 = p2_lookup.get(ep_id, {})
        disc_rpm = p2.get("discovered_rpm")
        first_429 = p2.get("first_429_at")
        auth = "auth" if ep.get("auth") else "public"

        parts = [f"{ep['method']:6s} {ep['path']}"]
        parts.append(f"[{auth}]")
        if doc_rpm:
            parts.append(f"doc: {doc_rpm:.0f} rpm")
        else:
            parts.append(f"doc: none")
        if disc_rpm is not None:
            parts.append(f"discovered: {disc_rpm:.0f} rpm")
        if first_429:
            parts.append(f"429@#{first_429}")
        elif p2.get("status") == "SKIPPED_NO_AUTH":
            parts.append("skipped (no auth)")
        elif not ep.get("safe_to_probe"):
            parts.append("not probed (unsafe)")

        print(f"    {' | '.join(parts)}")


# ─────────────────────────────────────────────────────────────────────────────
# REPORT GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def save_report(phase1, phase2, phase3, filename=None):
    """Save all results as JSON."""
    if not filename:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"rate_limit_report_{ts}.json"

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "global_limit_rpm": GLOBAL_LIMIT_RPM,
        "total_endpoints": len(ENDPOINTS),
        "phase1_smoke_test": phase1,
        "phase2_endpoint_probes": phase2,
        "phase3_shared_pool_test": phase3,
    }

    with open(filename, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n  Report saved: {filename}")
    return filename


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    global HAMMER_THREADS

    parser = argparse.ArgumentParser(
        description="Smarkets API Rate Limit Discovery Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full run (all phases)
  python3 rate_limit_discovery.py --email user@example.com --password secret

  # Phase 1 only (quick smoke test, no hammering)
  python3 rate_limit_discovery.py --email user@example.com --password secret --phase 1

  # Phase 2 only (per-endpoint probing)
  python3 rate_limit_discovery.py --email user@example.com --password secret --phase 2

  # Dry run (no requests sent)
  python3 rate_limit_discovery.py --dry-run
        """,
    )
    parser.add_argument("--email", help="Smarkets account email (used as username). Set SMARKETS_EMAIL env var instead to avoid exposing in process list.")
    parser.add_argument("--password", help="Smarkets account password. Set SMARKETS_PASSWORD env var instead to avoid exposing in process list.")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4],
                        help="Run specific phase only (default: all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be done without making requests")
    parser.add_argument("--no-report", action="store_true",
                        help="Skip saving JSON report")
    parser.add_argument("--threads", type=int, default=HAMMER_THREADS,
                        help=f"Number of concurrent hammer threads (default: {HAMMER_THREADS})")
    args = parser.parse_args()

    # Validate threads
    if args.threads < 1:
        print("  Error: --threads must be at least 1")
        sys.exit(1)
    if args.threads > 50:
        print("  Warning: --threads > 50 may overwhelm the API or local system")
    HAMMER_THREADS = args.threads

    # Support SMARKETS_PASSWORD env var as fallback
    if not args.password and not args.dry_run:
        args.password = os.environ.get("SMARKETS_PASSWORD")
    if not args.email and not args.dry_run:
        args.email = os.environ.get("SMARKETS_EMAIL")

    print("╔" + "═" * 76 + "╗")
    print("║" + "  Smarkets API — Rate Limit Discovery Tool".center(76) + "║")
    print("║" + f"  Global limit: {GLOBAL_LIMIT_RPM} RPM across all endpoints (per account)".center(76) + "║")
    print("║" + f"  Endpoints: {len(ENDPOINTS)} documented in OpenAPI spec".center(76) + "║")
    print("║" + f"  Hammer threads: {HAMMER_THREADS}".center(76) + "║")
    print("╚" + "═" * 76 + "╝")

    run_phase = args.phase or 0  # 0 = all phases

    # ── Check prerequisites ───────────────────────────────────────────────
    if not args.dry_run:
        try:
            import requests
        except ImportError:
            print("\n  Error: 'requests' library not installed. Run: pip install requests")
            sys.exit(1)

    client = SmarketsClient(email=args.email, password=args.password)

    # ── Auth ──────────────────────────────────────────────────────────────
    needs_auth = any(ep.get("auth") for ep in ENDPOINTS)
    if needs_auth and not args.dry_run and args.email and args.password:
        print("\n  Authenticating...")
        if not client.login():
            print("  ⚠️  Login failed. Authenticated endpoints will be skipped.")
            print("     You can still test public endpoints with --phase 1")
    elif not args.dry_run:
        print("\n  No credentials provided. Authenticated endpoints will be skipped.")
        print("  Public endpoints (events, currencies, contracts, markets) will still work.")

    # ── Execute phases ─────────────────────────────────────────────────────
    phase1_results = []
    phase2_results = []
    phase3_results = None

    if run_phase == 0 or run_phase == 1:
        phase1_results = phase1_smoke_test(client, dry_run=args.dry_run)

    if run_phase == 0 or run_phase == 2:
        phase2_results = phase2_probe_endpoints(client, dry_run=args.dry_run)

    if run_phase == 0 or run_phase == 3:
        phase3_results = phase3_shared_pool_test(client, dry_run=args.dry_run)

    if run_phase == 0 or run_phase == 4:
        phase4_analysis(phase1_results, phase2_results, phase3_results)

    # ── Save report ────────────────────────────────────────────────────────
    if not args.no_report and not args.dry_run:
        save_report(phase1_results, phase2_results, phase3_results)

    print("\n" + "=" * 78)
    print("  Done.")
    print("=" * 78)


if __name__ == "__main__":
    main()
