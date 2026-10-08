#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_multiples_fullcover.py — SAFE dry-run harness PLAN for Smarkets
"multiples" and "full cover" order testing at max £0.05 liability.

Purpose
-------
Plan and validate four order-test cases on Smarkets, each capped at £0.05
worst-case liability:
    1. BUY  multiple    (side=buy)
    2. SELL multiple    (side=sell)
    3. BUY  fullcover   (side=buy)
    4. SELL fullcover   (side=sell)
...plus the cashout endpoint set (see CASHOUT_ENDPOINTS).

STATUS: PLAN / DRY-RUN ONLY. This file places NO live orders. The live POST
blocks at the bottom are commented out on purpose and are additionally
blocked in code by LIVE_ENABLED=False.

HARD SAFETY RULES (do not remove)
---------------------------------
* No live order is ever placed by default.
* Live placement requires ALL of:
    (a) spec-worker confirmation of the exact endpoint + payload per case,
    (b) the 4 explicit human-gate confirmations (market, side, stake, liability),
    (c) a passing dry-run with computed liability <= £0.05.
* Credentials come only from env vars SMARKETS_EMAIL / SMARKETS_PASSWORD
  (or ~/.hermes/.env fallback). Passwords are never printed or written.

LIABILITY MATH (verified against live spec field descriptions)
--------------------------------------------------------------
price          integer basis points of 1; decimal odds D = 10000 / price
               (example: price 5000 -> 50% -> decimal 2.0)
quantity       integer in units of 1/10000 GBP; pot = quantity / 10000
back stake     back_stake = quantity * price / 100000000
quantity       quantity   = stake * 100000000 / price
pot            pot = back_stake * D = quantity / 10000

Risk (what you can lose):
  BUY  (back)  risk = stake                    # the back stake is at risk
  SELL (lay)   risk = stake * (D - 1)          # liability = pot - back stake
  SELL multiple: D_total = combined price of the multiple (10000/price);
                 conservative risk = stake * (D_total - 1).  For a
                 fullcover, exposure is modelled per line — maximum-line
                 risk only; total exposure across lines must be confirmed
                 by the spec worker.

Minimum stake: "The minimum stake is £0.05 or currency equivalent" — verbatim
in the `quantity` field description on the live order schemas. The schema
minimum for `quantity` is 0, so £0.05 is a BUSINESS RULE enforced at
validation: below it the order is rejected (candidate error
ORDER_INVALID_INVALID_QUANTITY; exact code to be confirmed).

Worked examples (deterministic, exact Decimal arithmetic):
  £0.05 stake @ price 2000 (D=5.0): quantity = 2500, pot = £0.25
  £0.05 stake @ price 5000 (D=2.0): quantity = 1000, pot = £0.10
  0.05c/£0.0005 @ price 5000      : quantity = 10  -> 100x below minimum -> reject

Usage
-----
  python3 test_multiples_fullcover.py --math        # deterministic math tables
  python3 test_multiples_fullcover.py --dry-run     # default: validate payloads offline
  python3 test_multiples_fullcover.py --dry-run --read-only-live   # + login/balance/discovery (GETs only)
  python3 test_multiples_fullcover.py --gate-preview  # show the 4 human-gate confirmations
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

try:  # optional; harness falls back to urllib
    import requests as _requests
except Exception:  # pragma: no cover
    _requests = None

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://api.smarkets.com"
API_PREFIX = "/v3"

MIN_STAKE_GBP = Decimal("0.05")       # spec: "The minimum stake is £0.05 or currency equivalent"
MAX_LIABILITY_GBP = Decimal("0.05")   # this test round's hard cap

QUANTITY_PER_GBP = Decimal("10000")        # quantity units per £1 (pot units)
BACK_STAKE_DIVISOR = Decimal("100000000")  # 1e8

# Absolute kill switch. NEVER flip without spec-worker sign-off + human gate.
LIVE_ENABLED = False

DEFAULT_STAKE = Decimal("0.05")
DEFAULT_PRICE = 5000  # decimal 2.0 — the only price where buy risk == sell risk == stake

# Candidate placement endpoints extracted from the unfiltered live OpenAPI doc
# (https://api.smarkets.com/v0/control/openapi/, 2026-09-24). The public
# trading_api tag view exposes only 18 paths and does NOT include these.
# >>> Every one of these MUST be confirmed by the spec worker before live use.
CANDIDATE_ENDPOINTS = {
    "buy_multiple":    "POST /v3/multiples_orders/",
    "sell_multiple":   "POST /v3/multiples_orders/",
    "buy_fullcover":   "POST /v3/fullcover/",
    "sell_fullcover":  "POST /v3/fullcover/",
}

# Cashout endpoint candidates (same provenance / same confirmation requirement).
CASHOUT_ENDPOINTS = {
    "fullcover_cashout":     ("POST", "/v3/fullcover/cashout/",
                              ["reference_id", "trade_out_reference_id", "cashout_value"]),
    "multiple_cashout":      ("POST", "/v3/multiples_orders/cashout/",
                              ["contract_ids", "price", "quantity", "side", "reference_id"]),
    "multi_tick_cashout":    ("POST", "/v3/multi_tick_orders/cashout/",
                              ["contract_id", "price", "quantity", "reference_id"]),
    "market_cashout":        ("POST", "/v3/markets/{market_id}/cash_outs/",
                              ["amount"]),  # integer in *decimals*, e.g. 400 = £4.00
    "fullcover_cashout_px":  ("GET",  "/v3/fullcover/cashout/prices/", []),
    "multiple_cashout_px":   ("GET",  "/v3/multiples/cashout/{contract_ids}/prices/", []),
}

SPEC_WORKER_QUESTIONS = [
    "Confirm POST /v3/multiples_orders/ is enabled for this account (path exists in the "
    "unfiltered spec but not in the public trading_api tag view).",
    "Confirm POST /v3/fullcover/ availability + the allowed values of `fullcover_type`.",
    "Confirm `stake` semantics on both routes (total across lines, or per line?).",
    "Confirm `stake_multiplier` semantics on /v3/fullcover/ (required field; example=3).",
    "Confirm `reference_id` type per route (string on /v3/fullcover/, integer on /v3/multiples_orders/).",
    "Confirm sell-side risk model: is `stake` the back-stake equivalent (risk = stake*(D-1)) "
    "or the direct amount at risk?",
    "Confirm fullcover exposure across lines (max line vs sum of lines) and its effect on the £0.05 cap.",
    "Confirm the min-stake rule applies to the stake (not the pot): e.g. quantity 500 at price 5000 "
    "= £0.025 back stake — would that be rejected?",
    "Confirm the error code returned for a below-minimum stake (candidate: ORDER_INVALID_INVALID_QUANTITY).",
    "Confirm valid price ticks (spec only says 'valid tick'; tick table is help-centre only).",
]


# ---------------------------------------------------------------------------
# Exact money math (Decimal; deterministic)
# ---------------------------------------------------------------------------

def dec(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def decimal_odds(price: int) -> Decimal:
    """D = 10000 / price."""
    return (Decimal(10000) / dec(price)).quantize(Decimal("0.000001"))


def quantity_from_stake(stake_gbp, price: int) -> int:
    """quantity = stake * 100000000 / price (rounded half-up to an integer)."""
    return int((dec(stake_gbp) * BACK_STAKE_DIVISOR / dec(price)).to_integral_value(rounding=ROUND_HALF_UP))


def back_stake_from_quantity(quantity: int, price: int) -> Decimal:
    """back_stake = quantity * price / 100000000."""
    return (dec(quantity) * dec(price) / BACK_STAKE_DIVISOR).quantize(Decimal("0.000001"))


def pot_from_quantity(quantity: int) -> Decimal:
    """pot = quantity / 10000."""
    return (dec(quantity) / QUANTITY_PER_GBP).quantize(Decimal("0.000001"))


def buy_liability_gbp(stake_gbp) -> Decimal:
    """Back: the stake is the amount at risk."""
    return dec(stake_gbp).quantize(Decimal("0.000001"))


def sell_liability_gbp(stake_gbp, price: int) -> Decimal:
    """Lay, conservative model: risk = stake * (D - 1) = stake * (10000-price)/price."""
    stake = dec(stake_gbp)
    return (stake * (Decimal(10000) - dec(price)) / dec(price)).quantize(Decimal("0.000001"))


def lay_liability_from_quantity(quantity: int, price: int) -> Decimal:
    """Lay risk in quantity terms: quantity * (10000 - price) / 100000000."""
    return (dec(quantity) * (Decimal(10000) - dec(price)) / BACK_STAKE_DIVISOR).quantize(Decimal("0.000001"))


def money(x) -> str:
    return f"£{dec(x).quantize(Decimal('0.0001'))}"


def price_at_max_sell_liability(stake_gbp, cap=MAX_LIABILITY_GBP) -> int:
    """Lowest price (shortest odds) at which stake*(D-1) <= cap still holds."""
    stake = dec(stake_gbp)
    d_max = cap / stake + 1
    return int((Decimal(10000) / d_max).to_integral_value(rounding=ROUND_HALF_UP))


# ---------------------------------------------------------------------------
# Stage 0 — deterministic math report
# ---------------------------------------------------------------------------

EXAMPLES = [
    (Decimal("0.05"), 2000),
    (Decimal("0.05"), 5000),
    (Decimal("0.0005"), 5000),  # the "0.05c" case
]


def run_math_report() -> int:
    print("=" * 78)
    print("LIABILITY MATH — deterministic (exact Decimal arithmetic)")
    print("=" * 78)
    print("Formulas:")
    print("  decimal_odds D   = 10000 / price")
    print("  back_stake       = quantity * price / 100000000")
    print("  quantity         = stake * 100000000 / price")
    print("  pot              = quantity / 10000")
    print()
    hdr = f"{'stake':>10} {'price':>6} {'D':>8} {'quantity':>9} {'pot':>9} {'back_stake':>11} {'buy_risk':>9} {'sell_risk':>10}"
    print(hdr)
    print("-" * len(hdr))
    for stake, price in EXAMPLES:
        q = quantity_from_stake(stake, price)
        print(f"{money(stake):>10} {price:>6} {decimal_odds(price):>8} {q:>9} "
              f"{money(pot_from_quantity(q)):>9} {money(back_stake_from_quantity(q, price)):>11} "
              f"{money(buy_liability_gbp(stake)):>9} {money(sell_liability_gbp(stake, price)):>10}")

    print()
    print("Sanity checks (spec's own worked example): quantity 100000 @ price 5000")
    q = 100000
    print(f"  -> back_stake = {money(back_stake_from_quantity(q, 5000))}  (spec says £5.00)  pot = {money(pot_from_quantity(q))}")
    print()
    print("WHY '0.05c' (£0.0005) IS REJECTED:")
    for price in (2000, 5000):
        q = quantity_from_stake(Decimal("0.0005"), price)
        print(f"  stake £0.0005 @ price {price}: quantity={q}, pot={money(pot_from_quantity(q))}, "
              f"back_stake={money(back_stake_from_quantity(q, price))}")
    print("  - £0.0005 is 1/100th of the £0.05 minimum stake -> below minimum.")
    print("  - quantity 10 @ any price is also below 500 units (=£0.05 pot) under the most")
    print("    lenient reading of the minimum; under the stake reading the floor is 1000 units")
    print("    at price 5000 and 2500 units at price 2000. Rejected on either reading.")
    print("  - Expected rejection: HTTP 400 with ORDER_INVALID_INVALID_QUANTITY (candidate; confirm).")
    print("  - If the user meant £0.05 (not 0.05 pence), that is EXACTLY the minimum and passes.")
    print()
    print(f"Sell-side safety floor: at stake £0.05 the sell liability is £0.05 only when")
    print(f"  D <= 2.0 i.e. price >= {price_at_max_sell_liability(Decimal('0.05'))}. Below that price,")
    print("  a sell order at £0.05 stake EXCEEDS the £0.05 liability cap and must be aborted.")
    return 0


# ---------------------------------------------------------------------------
# Minimal HTTP client (requests if available, else urllib)
# ---------------------------------------------------------------------------

class SafetyBlocked(RuntimeError):
    pass


class _Resp:
    def __init__(self, status, text, headers):
        self.status_code = status
        self.text = text
        self.headers = headers

    def json(self):
        return json.loads(self.text)


class Client:
    """Read-only by default. place_order() is hard-blocked unless LIVE_ENABLED."""

    def __init__(self, base_url=BASE_URL, timeout=15):
        self.base = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method, path, token=None, json_body=None, params=None):
        url = self.base + path
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Session-Token {token}"
        if json_body is not None:
            headers["Content-Type"] = "application/json"
        if _requests is not None:
            r = _requests.request(method, url, headers=headers, json=json_body,
                                  params=params, timeout=self.timeout,
                                  allow_redirects=False)
            return _Resp(r.status_code, r.text, dict(r.headers))
        # urllib fallback
        data = json.dumps(json_body).encode() if json_body is not None else None
        if params:
            url = url + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return _Resp(resp.status, resp.read().decode("utf-8", "replace"), dict(resp.headers))
        except urllib.error.HTTPError as e:
            return _Resp(e.code, e.read().decode("utf-8", "replace"), dict(e.headers))

    def get(self, path, token=None, params=None):
        return self._request("GET", path, token=token, params=params)

    def post_order(self, path, payload, token=None):
        """LIVE ORDER PLACEMENT — hard-blocked in this harness."""
        if not LIVE_ENABLED:
            raise SafetyBlocked(
                "LIVE_ENABLED is False. Live placement is blocked. "
                "All four human-gate confirmations AND spec-worker sign-off are required first.")
        return self._request("POST", path, token=token, json_body=payload)


# ---------------------------------------------------------------------------
# Stage 1 — credentials (env vars only; never logged)
# ---------------------------------------------------------------------------

ENV_PATH = Path.home() / ".hermes" / ".env"


def _parse_env_file(path: Path) -> dict:
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip("'\"")
    return out


def load_credentials():
    """Return (email, password, source) or (None, None, reason). No values printed."""
    email = os.environ.get("SMARKETS_EMAIL")
    password = os.environ.get("SMARKETS_PASSWORD")
    if email and password:
        return email, password, "environment"
    file_env = _parse_env_file(ENV_PATH)
    email = email or file_env.get("SMARKETS_EMAIL")
    password = password or file_env.get("SMARKETS_PASSWORD")
    if email and password:
        return email, password, f"{ENV_PATH} (fallback)"
    missing = [k for k, v in (("SMARKETS_EMAIL", email), ("SMARKETS_PASSWORD", password)) if not v]
    return None, None, "missing: " + ", ".join(missing)


# ---------------------------------------------------------------------------
# Stage 2 — login (201 check) and Stage 3 — balance
# ---------------------------------------------------------------------------

def stage_login(client: Client, email, password):
    print("\n[2] LOGIN  POST /v3/sessions/")
    r = client._request("POST", f"{API_PREFIX}/sessions/",
                        json_body={"username": email, "password": password})
    if r.status_code != 201:
        print(f"    FAIL — expected 201, got {r.status_code}. Body: {r.text[:300]}")
        hints = {401: "bad credentials / MFA / DEVICE_NOT_TRUSTED",
                 403: "forbidden (jurisdiction, SOURCE_BLOCKED, IP_NOT_TRUSTED, or Cloudflare HTML block)",
                 429: "rate limit — login is 5 requests / 300s",
                 451: "jurisdiction block"}
        if r.status_code in hints:
            print(f"    hint: {hints[r.status_code]}")
        return None
    body = r.json()
    token = body.get("token")
    if not token:
        print(f"    FAIL — 201 but no token field. Keys: {sorted(body.keys())}")
        return None
    print("    OK — 201, token received (value not printed). TTL 30 min, sliding renewal.")
    return token


def stage_balance(client: Client, token):
    print("\n[3] BALANCE  GET /v3/balance/  (+ /v3/accounts/ for exposure)")
    r = client.get(f"{API_PREFIX}/balance/", token=token)
    if r.status_code == 200:
        print(f"    balance: {r.json().get('balance')}")
    else:
        print(f"    FAIL — {r.status_code}: {r.text[:200]}")
    r2 = client.get(f"{API_PREFIX}/accounts/", token=token)
    if r2.status_code == 200:
        acct = (r2.json() or {}).get("account", {})
        print(f"    available_balance: {acct.get('available_balance')}  exposure: {acct.get('exposure')} "
              f"currency: {acct.get('currency')}")
    else:
        print(f"    /v3/accounts/ -> {r2.status_code}: {r2.text[:200]}")
    return r.status_code == 200


# ---------------------------------------------------------------------------
# Stage 4 — market discovery (read-only GETs)
# ---------------------------------------------------------------------------

def stage_discovery(client: Client, token, max_events=20, top_n=5):
    print("\n[4] MARKET DISCOVERY (read-only) — looking for a liquid test market")
    r = client.get(f"{API_PREFIX}/events/", token=token, params={"limit": max_events})
    if r.status_code != 200:
        print(f"    FAIL — GET /v3/events/ -> {r.status_code}: {r.text[:200]}")
        return []
    events = (r.json() or {}).get("events", [])
    print(f"    events: {len(events)}")
    if not events:
        return []
    event_ids = [str(e["id"]) for e in events if e.get("id")][:20]
    r = client.get(f"{API_PREFIX}/events/{','.join(event_ids)}/markets/", token=token,
                   params={"limit_by_event": 5, "popular": True})
    if r.status_code != 200:
        print(f"    FAIL — markets -> {r.status_code}: {r.text[:200]}")
        return []
    markets = (r.json() or {}).get("markets", [])
    print(f"    markets: {len(markets)}")
    if not markets:
        return []
    market_ids = [str(m["id"]) for m in markets if m.get("id")][:100]
    vol_by_id = {}
    r = client.get(f"{API_PREFIX}/markets/{','.join(market_ids)}/volumes/", token=token)
    if r.status_code == 200:
        for v in (r.json() or {}).get("volumes", []):
            vol_by_id[str(v.get("market_id"))] = v.get("double_stake_volume") or v.get("volume") or 0
    ranked = sorted(market_ids, key=lambda mid: vol_by_id.get(mid, 0), reverse=True)[:top_n]
    print(f"    top {len(ranked)} markets by traded volume:")
    m_by_id = {str(m["id"]): m for m in markets}
    for mid in ranked:
        m = m_by_id.get(mid, {})
        print(f"      market {mid:>8}  vol~{vol_by_id.get(mid, '?'):>10}  cashout_enabled={m.get('cashout_enabled')}  {str(m.get('name'))[:60]}")
    r = client.get(f"{API_PREFIX}/markets/{','.join(ranked)}/quotes/", token=token)
    if r.status_code == 200:
        print(f"    quotes fetched for top markets (shape: market_id -> contract_id -> bids/offers)")
    else:
        print(f"    quotes -> {r.status_code}: {r.text[:200]}")
    print("    NOTE: pick legs whose combined price keeps sell risk <= £0.05 (see --math).")
    return ranked


# ---------------------------------------------------------------------------
# Stage 5 — draft payloads (candidate shapes; spec worker must confirm)
# ---------------------------------------------------------------------------

PLACEHOLDER_LEG_1 = "<PLACEHOLDER-leg-1-contract_id>"
PLACEHOLDER_LEG_2 = "<PLACEHOLDER-leg-2-contract_id>"


def build_payload(case: str, leg_1=PLACEHOLDER_LEG_1, leg_2=PLACEHOLDER_LEG_2,
                  price=DEFAULT_PRICE, stake=DEFAULT_STAKE) -> dict:
    """Draft payload per case. CANDIDATE SHAPES — confirm with the spec worker."""
    stake_f = float(stake)
    if case in ("buy_multiple", "sell_multiple"):
        return {
            "contract_ids": [leg_1, leg_2],   # multiple = >=2 legs (parlay)
            "price": price,                    # combined price of the multiple
            "stake": stake_f,                  # £0.05
            "reference_id": 2026092401,        # integer on this route (confirm)
            "side": "buy" if case == "buy_multiple" else "sell",
            "granular_errors": True,           # spec: "Always pass True, unless you are mammoth"
        }
    if case in ("buy_fullcover", "sell_fullcover"):
        return {
            "fullcover_type": "doubles",       # confirm allowed values
            "contract_ids": [leg_1, leg_2],    # 2 selections / doubles == exactly 1 line
            "price": price,
            "stake": stake_f,
            "reference_id": "2026092403",      # STRING on this route (confirm)
            "stake_multiplier": 1,             # REQUIRED field; semantics unconfirmed (spec example=3)
            "side": "buy" if case == "buy_fullcover" else "sell",
            "granular_errors": True,
        }
    raise ValueError(f"unknown case: {case}")


REQUIRED_FIELDS = {
    "buy_multiple": ["contract_ids", "price", "stake", "reference_id"],
    "sell_multiple": ["contract_ids", "price", "stake", "reference_id"],
    "buy_fullcover": ["fullcover_type", "contract_ids", "price", "stake", "reference_id", "stake_multiplier"],
    "sell_fullcover": ["fullcover_type", "contract_ids", "price", "stake", "reference_id", "stake_multiplier"],
}

ALLOWED_FIELDS = {
    "buy_multiple": {"contract_ids", "price", "stake", "reference_id", "side", "granular_errors",
                     "bet_token_id", "free_bet_token_id", "promotion_id", "bonus_bet", "is_retry"},
    "sell_multiple": {"contract_ids", "price", "stake", "reference_id", "side", "granular_errors",
                      "bet_token_id", "free_bet_token_id", "promotion_id", "bonus_bet", "is_retry"},
    "buy_fullcover": {"fullcover_type", "contract_ids", "price", "stake", "reference_id", "stake_multiplier",
                      "side", "granular_errors", "cover_depth", "ew_contract_ids", "ew_price",
                      "bet_token_id", "free_bet_token_id", "promotion_id"},
    "sell_fullcover": {"fullcover_type", "contract_ids", "price", "stake", "reference_id", "stake_multiplier",
                       "side", "granular_errors", "cover_depth", "ew_contract_ids", "ew_price",
                       "bet_token_id", "free_bet_token_id", "promotion_id"},
}


# ---------------------------------------------------------------------------
# Stage 6 — dry-run validation: schema, min stake, liability cap
# ---------------------------------------------------------------------------

def validate_case(case: str, payload: dict, number_of_lines: int = 1) -> dict:
    """Validate one draft payload. Returns a report dict; 'ok' False = ABORT that case."""
    notes = []
    ok = True

    # --- schema check ------------------------------------------------------
    required = REQUIRED_FIELDS[case]
    missing = [f for f in required if f not in payload]
    unknown = [f for f in payload if f not in ALLOWED_FIELDS[case]]
    if missing:
        ok = False
        notes.append(f"missing required fields: {missing}")
    if unknown:
        ok = False
        notes.append(f"unknown fields (not in live schema): {unknown}")
    if not isinstance(payload.get("contract_ids", []), list) or len(payload.get("contract_ids", [])) < 2:
        ok = False
        notes.append("contract_ids must list >=2 legs for a multiple/fullcover")
    price = payload.get("price")
    if not isinstance(price, int) or not (1 <= price <= 9999):
        ok = False
        notes.append(f"price must be int in 1..9999, got {price!r}")

    # --- min-stake check ---------------------------------------------------
    stake = dec(payload.get("stake", 0))
    if stake < MIN_STAKE_GBP:
        ok = False
        notes.append(f"stake {money(stake)} below minimum {money(MIN_STAKE_GBP)} -> would be REJECTED")

    # --- liability check (conservative model) ------------------------------
    side = payload.get("side", "buy")
    if side == "buy":
        per_line = buy_liability_gbp(stake)
    else:
        per_line = sell_liability_gbp(stake, price)
    # Conservative total: assume `stake` is PER LINE until the spec worker confirms otherwise.
    total = (per_line * number_of_lines).quantize(Decimal("0.000001"))
    if total > MAX_LIABILITY_GBP:
        ok = False
        notes.append(f"liability {money(total)} > cap {money(MAX_LIABILITY_GBP)} -> ABORT")

    return {
        "case": case,
        "endpoint": CANDIDATE_ENDPOINTS[case] + "   [CANDIDATE — confirm with spec worker]",
        "payload": payload,
        "side": side,
        "per_line_risk_gbp": str(per_line),
        "lines": number_of_lines,
        "total_risk_gbp": str(total),
        "min_stake_ok": stake >= MIN_STAKE_GBP,
        "cap_ok": total <= MAX_LIABILITY_GBP,
        "ok": ok,
        "notes": notes,
    }


def run_dry_run(read_only_live=False) -> int:
    print("=" * 78)
    print("DRY-RUN VALIDATION — no orders are placed in any mode")
    print("=" * 78)

    client = Client()

    email, password, src = load_credentials()
    token = None
    if read_only_live:
        if not email or not password:
            print(f"[1] ENV — credentials not available ({src}); skipping read-only live stages.")
            print("    Set SMARKETS_EMAIL / SMARKETS_PASSWORD to run login/balance/discovery (GETs only).")
        else:
            print(f"[1] ENV — credentials loaded from {src} (values not printed)")
            token = stage_login(client, email, password)
            if token:
                stage_balance(client, token)
                stage_discovery(client, token)
            else:
                print("    login failed -> discovery skipped")
    else:
        print("[1] ENV — offline dry-run (pass --read-only-live to include login/balance/discovery)")

    print("\n[5] DRAFT PAYLOADS + [6] VALIDATION (schema, min-stake, liability cap £0.05)")
    cases = [
        ("buy_multiple", 1),
        ("sell_multiple", 1),
        ("buy_fullcover", 1),   # 2 selections, doubles -> exactly 1 line
        ("sell_fullcover", 1),
    ]
    reports, failures = [], 0
    for case, lines in cases:
        payload = build_payload(case)
        rep = validate_case(case, payload, number_of_lines=lines)
        reports.append(rep)
        flag = "PASS" if rep["ok"] else "ABORT"
        if not rep["ok"]:
            failures += 1
        print(f"\n  [{flag}] {case}")
        print(f"        endpoint : {rep['endpoint']}")
        print(f"        payload  : {json.dumps(payload)}")
        print(f"        risk     : per-line {money(rep['per_line_risk_gbp'])} x {rep['lines']} line(s) "
              f"= {money(rep['total_risk_gbp'])} (cap {money(MAX_LIABILITY_GBP)})")
        for n in rep["notes"]:
            print(f"        note     : {n}")

    print("\n[6b] GUARD SELF-TEST (proves the aborts actually fire)")
    demos = [
        ("sell_multiple", build_payload("sell_multiple", price=2000), 1,
         "sell @ price 2000 (D=5.0): risk would be £0.20 > £0.05 cap"),
        ("buy_multiple", build_payload("buy_multiple", price=5000, stake=Decimal("0.0005")), 1,
         "stake 0.0005 ('0.05c'): below the £0.05 minimum"),
        ("buy_fullcover", build_payload("buy_fullcover", price=5000, stake=Decimal("0.05")), 3,
         "fullcover doubles on 3 selections (3 lines): £0.15 total > £0.05 cap"),
    ]
    for case, payload, lines, why in demos:
        rep = validate_case(case, payload, number_of_lines=lines)
        if rep["ok"]:
            print(f"    [!! GUARD DID NOT FIRE] {why}")
            failures += 1
            continue
        print(f"    [ABORT fired as expected] {why}")
        for n in rep["notes"]:
            print(f"        -> {n}")

    print("\n[6c] SPEC-WORKER CONFIRMATION QUEUE (blocking before any live call):")
    for i, q in enumerate(SPEC_WORKER_QUESTIONS, 1):
        print(f"    {i:>2}. {q}")

    print("\n[7] LIVE POST BLOCKS: commented out at the bottom of this file AND hard-blocked")
    print("    by LIVE_ENABLED=False in Client.post_order(). Uncomment only after sign-off.")

    if failures:
        print(f"\nRESULT: {failures} case(s) FAILED validation -> live placement is blocked.")
        return 1
    print("\nRESULT: all cases pass the offline validation gates. Nothing was submitted.")
    return 0


# ---------------------------------------------------------------------------
# Human gate — 4 explicit confirmations required before ANY live placement
# ---------------------------------------------------------------------------

def confirm_human_gate(case: str, market_id: str, contract_ids, side: str, stake, price: int) -> bool:
    """Interactive gate. ALL four confirmations must be typed exactly. Any miss = abort."""
    stake = dec(stake)
    liability = buy_liability_gbp(stake) if side == "buy" else sell_liability_gbp(stake, price)
    print(f"\nHUMAN GATE for case '{case}' — type each confirmation EXACTLY as shown.")
    print("All four are required; anything else aborts.")
    asks = [
        ("1/4 MARKET    ", f"CONFIRM MARKET {market_id} {','.join(map(str, contract_ids))}"),
        ("2/4 SIDE      ", f"CONFIRM SIDE {side}"),
        ("3/4 STAKE     ", f"CONFIRM STAKE {stake}"),
        ("4/4 LIABILITY ", f"CONFIRM LIABILITY {money(liability)}"),
    ]
    for label, expected in asks:
        try:
            answer = input(f"  {label} -> type: {expected}\n  > ").strip()
        except EOFError:
            print("  no input available -> ABORT")
            return False
        if answer != expected:
            print(f"  mismatch (got {answer!r}) -> ABORT. No order placed.")
            return False
    if liability > MAX_LIABILITY_GBP:
        print(f"  computed liability {money(liability)} exceeds cap -> ABORT.")
        return False
    print("  all confirmations matched — clear to proceed to the (still commented-out) POST block.")
    return True


def run_gate_preview() -> int:
    print("HUMAN GATE — required before ANY live placement (4 explicit confirmations)")
    print("=" * 78)
    print("  1/4 MARKET    : market_id + every leg contract_id verified by a human against the")
    print("                  live market page (not just copied from a script).")
    print("  2/4 SIDE      : buy/sell matches the intended test case.")
    print("  3/4 STAKE     : stake value confirmed (and for fullcover: total vs per-line confirmed).")
    print("  4/4 LIABILITY : worst-case liability confirmed <= £0.05 for the confirmed semantics.")
    print()
    print("Plus a 5th, non-interactive prerequisite: spec-worker sign-off on the endpoint +")
    print("payload shape for that case (see the confirmation queue in --dry-run).")
    print("\nExample transcript (case buy_multiple):")
    print("  > CONFIRM MARKET 123456 7891,7892")
    print("  > CONFIRM SIDE buy")
    print("  > CONFIRM STAKE 0.05")
    print("  > CONFIRM LIABILITY £0.0500")
    return 0


# ---------------------------------------------------------------------------
# LIVE PLACEMENT BLOCKS — COMMENTED OUT BY DESIGN
# ---------------------------------------------------------------------------
# Preconditions before uncommenting ANY block:
#   [ ] spec worker confirmed the endpoint + payload for that case
#   [ ] --dry-run passes (schema + min stake + liability <= £0.05)
#   [ ] all 4 human-gate confirmations typed
#   [ ] LIVE_ENABLED flipped to True (separate, deliberate edit)
#   [ ] market selected from --read-only-live discovery, price >= 5000 for sell cases
#
# --- CASE 1: BUY MULTIPLE ---------------------------------------------------
# token = stage_login(client, *load_credentials()[:2])                 # 201 check
# assert stage_balance(client, token)                                  # funds present
# payload = build_payload("buy_multiple", leg_1="<live_leg_1>", leg_2="<live_leg_2>",
#                         price=<confirmed_combined_price>, stake=Decimal("0.05"))
# rep = validate_case("buy_multiple", payload, number_of_lines=1)
# assert rep["ok"], rep["notes"]
# if confirm_human_gate("buy_multiple", "<market_id>", payload["contract_ids"], "buy", payload["stake"], payload["price"]):
#     resp = client.post_order("/v3/multiples_orders/", payload, token=token)   # CANDIDATE ENDPOINT
#     print(resp.status_code, resp.text)
#
# --- CASE 2: SELL MULTIPLE --------------------------------------------------
# payload = build_payload("sell_multiple", leg_1=..., leg_2=..., price=<price >= 5000>, stake=Decimal("0.05"))
# rep = validate_case("sell_multiple", payload, number_of_lines=1)
# assert rep["ok"], rep["notes"]        # sell risk = stake*(D-1) must stay <= £0.05
# if confirm_human_gate("sell_multiple", "<market_id>", payload["contract_ids"], "sell", payload["stake"], payload["price"]):
#     resp = client.post_order("/v3/multiples_orders/", payload, token=token)   # CANDIDATE ENDPOINT
#     print(resp.status_code, resp.text)
#
# --- CASE 3: BUY FULLCOVER --------------------------------------------------
# payload = build_payload("buy_fullcover", leg_1=..., leg_2=..., price=..., stake=Decimal("0.05"))
# rep = validate_case("buy_fullcover", payload, number_of_lines=1)   # 2 selections + doubles = 1 line
# assert rep["ok"], rep["notes"]        # do NOT add a 3rd leg until stake semantics are confirmed
# if confirm_human_gate("buy_fullcover", "<market_id>", payload["contract_ids"], "buy", payload["stake"], payload["price"]):
#     resp = client.post_order("/v3/fullcover/", payload, token=token)          # CANDIDATE ENDPOINT
#     print(resp.status_code, resp.text)
#
# --- CASE 4: SELL FULLCOVER -------------------------------------------------
# payload = build_payload("sell_fullcover", leg_1=..., leg_2=..., price=<price >= 5000>, stake=Decimal("0.05"))
# rep = validate_case("sell_fullcover", payload, number_of_lines=1)
# assert rep["ok"], rep["notes"]
# if confirm_human_gate("sell_fullcover", "<market_id>", payload["contract_ids"], "sell", payload["stake"], payload["price"]):
#     resp = client.post_order("/v3/fullcover/", payload, token=token)          # CANDIDATE ENDPOINT
#     print(resp.status_code, resp.text)
#
# --- CASHOUT (after a position exists; candidate shapes) ---------------------
# fullcover:  client.post_order("/v3/fullcover/cashout/",
#               {"reference_id": "..", "trade_out_reference_id": "..", "cashout_value": <number>}, token=token)
# multiple:   client.post_order("/v3/multiples_orders/cashout/",
#               {"contract_ids": [...], "price": <int>, "quantity": <int>, "side": "buy|sell",
#                "reference_id": <int>}, token=token)
# market:     client.post_order("/v3/markets/<market_id>/cash_outs/", {"amount": <int, decimals>}, token=token)
# quote only: GET /v3/fullcover/cashout/prices/?trade_out_reference_id=..   (read-only)
#             GET /v3/multiples/cashout/<contract_ids>/prices/?side=..&traded_out_order_id=..  (read-only)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="SAFE dry-run harness plan: Smarkets multiples + fullcover at £0.05 cap")
    ap.add_argument("--math", action="store_true", help="print deterministic liability math tables and exit")
    ap.add_argument("--dry-run", action="store_true", help="validate draft payloads offline (default)")
    ap.add_argument("--read-only-live", action="store_true",
                    help="also run login (201 check) + balance + market discovery — GET/POST-session only, no orders")
    ap.add_argument("--gate-preview", action="store_true", help="show the 4 human-gate confirmations")
    args = ap.parse_args(argv)

    if args.math:
        return run_math_report()
    if args.gate_preview:
        return run_gate_preview()
    # default / --dry-run
    return run_dry_run(read_only_live=args.read_only_live)


if __name__ == "__main__":
    sys.exit(main())
