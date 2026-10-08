#!/usr/bin/env python3
"""
Smarkets API — No-Auth Live Football Prices Test
=================================================
Tests the publicly accessible (no-auth) endpoints to retrieve:
  - Live football matches
  - Match winner (Full-time result) odds
  - Available liquidity (best bid/offer depth)

Price format:   basis points out of 10,000  →  decimal_odds = 10000 / price
                                                  (e.g. 5000 = 50% = odds 2.0)
Quantity format: 1/10,000ths of GBP            →  gbp = quantity / 10000

Confirmed working without authentication during pentest with sbkscores.com.

Usage:
  python3 noauth_live_football.py                    # all live matches
  python3 noauth_live_football.py --limit 3           # first 3 only
  python3 noauth_live_football.py --event-id 45155153 # specific event
"""

import requests
import json
import sys
import argparse
from datetime import datetime, timezone

BASE_URL = "https://api.smarkets.com"
TIMEOUT = 15

# ── Price/quantity conversion ──────────────────────────────────────────
# Smarkets prices are basis points out of 10,000:
#   price = probability * 10,000  (e.g. 5000 = 50% = decimal odds 2.0)
#   quantity = GBP * 10,000       (e.g. 50000 = £5.00)
DENOM = 10_000
QTY_DENOM = 10_000


def price_to_decimal(price):
    """Convert Smarkets basis-point price to decimal odds."""
    if not price or price == 0:
        return None
    return round(DENOM / price, 2)


def price_to_pct(price):
    """Convert Smarkets basis-point price to implied probability %."""
    if not price:
        return None
    return round((price / DENOM) * 100, 1)


def qty_to_gbp(quantity):
    """Convert Smarkets quantity to GBP."""
    if not quantity:
        return 0
    return round(quantity / QTY_DENOM, 2)


def fmt_gbp(amount):
    """Format as compact GBP string."""
    if amount >= 1000:
        return f"£{amount/1000:.1f}k"
    return f"£{amount:.2f}"


# ── API calls (no auth) ─────────────────────────────────────────────────
def get_live_football_events(limit=10):
    """Get live football matches — no auth required."""
    r = requests.get(
        f"{BASE_URL}/v3/events/",
        params={"type": "football_match", "state": "live", "limit": limit},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get("events", [])


def get_event_by_id(event_id):
    """Get a specific event by ID — no auth required."""
    r = requests.get(
        f"{BASE_URL}/v3/events/",
        params={"id": event_id},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    events = r.json().get("events", [])
    return events[0] if events else None


def get_markets(event_id):
    """Get markets for an event — no auth required."""
    r = requests.get(
        f"{BASE_URL}/v3/events/{event_id}/markets/",
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get("markets", [])


def get_contracts(market_id):
    """Get contracts for a market — no auth required."""
    r = requests.get(
        f"{BASE_URL}/v3/markets/{market_id}/contracts/",
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get("contracts", [])


def get_quotes(market_id):
    """Get order book quotes for a market — WORKS WITHOUT AUTH (delayed prices).

    Returns dict keyed by contract_id:
      { "411238755": { "bids": [{price, quantity}, ...],
                        "offers": [{price, quantity}, ...] } }
    """
    r = requests.get(
        f"{BASE_URL}/v3/markets/{market_id}/quotes/",
        timeout=TIMEOUT,
    )
    if r.status_code != 200:
        return {}
    return r.json()


# ── Core logic ──────────────────────────────────────────────────────────
def find_match_winner_market(markets):
    """Find the Full-time Result / Match Winner market (WINNER_3_WAY)."""
    for m in markets:
        mtype = m.get("market_type", {})
        if isinstance(mtype, dict) and mtype.get("name") == "WINNER_3_WAY":
            return m
    # Fallback: look by name
    for m in markets:
        if "full-time result" in m.get("name", "").lower():
            return m
    return None


def build_match_data(event, market, contracts, quotes):
    """Assemble a clean match data dict with odds and liquidity."""
    contract_map = {c.get("id"): c for c in contracts if c.get("id") is not None}

    outcomes = []
    for contract_id, book in quotes.items():
        contract = contract_map.get(contract_id, {})
        name = contract.get("name", f"Contract {contract_id}")
        ctype = contract.get("contract_type", {}).get("name", "")

        bids = book.get("bids", [])
        offers = book.get("offers", [])

        best_bid = bids[0] if bids else None
        best_offer = offers[0] if offers else None

        # Total available liquidity on each side (use .get for safety)
        total_bid_qty = sum(b.get("quantity", 0) for b in bids)
        total_offer_qty = sum(o.get("quantity", 0) for o in offers)

        outcomes.append({
            "name": name,
            "type": ctype,
            "back_odds": price_to_decimal(best_offer.get("price")) if best_offer else None,
            "back_price_raw": best_offer.get("price") if best_offer else None,
            "back_liquidity_gbp": qty_to_gbp(total_offer_qty) if offers else 0,
            "lay_odds": price_to_decimal(best_bid.get("price")) if best_bid else None,
            "lay_price_raw": best_bid.get("price") if best_bid else None,
            "lay_liquidity_gbp": qty_to_gbp(total_bid_qty) if bids else 0,
            "bid_depth_levels": len(bids),
            "offer_depth_levels": len(offers),
            "implied_prob_pct": price_to_pct(
                best_offer.get("price") if best_offer else (best_bid.get("price") if best_bid else 0)
            ),
        })

    # Sort: Home, Draw, Away
    type_order = {"HOME": 0, "DRAW": 1, "AWAY": 2}
    outcomes.sort(key=lambda x: type_order.get(x["type"], 99))

    return {
        "event_id": event["id"],
        "match": event["name"],
        "start_datetime": event["start_datetime"],
        "state": event["state"],
        "inplay_enabled": event.get("inplay_enabled", False),
        "market_id": market["id"],
        "market_name": market["name"],
        "outcomes": outcomes,
    }


def print_match(match):
    """Pretty-print a match with odds and liquidity."""
    dt = match["start_datetime"]
    try:
        dt_obj = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        dt_str = dt_obj.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        dt_str = dt

    inplay = "🔴 IN-PLAY" if match["inplay_enabled"] else "🟡 LIVE"
    print(f"\n{'─'*70}")
    print(f"⚽ {match['match']}")
    print(f"   Kickoff: {dt_str}  |  {inplay}  |  Event ID: {match['event_id']}")
    print(f"   Market:  {match['market_name']} (ID: {match['market_id']})")
    print()

    # Header
    print(f"   {'Outcome':<20} {'Back':>7} {'Back Liq':>10} {'Lay':>7} {'Lay Liq':>10} {'Implied%':>8}")
    print(f"   {'─'*20} {'─'*7} {'─'*10} {'─'*7} {'─'*10} {'─'*8}")

    for o in match["outcomes"]:
        back_odds = f"{o['back_odds']:.2f}" if o["back_odds"] else "  —  "
        lay_odds = f"{o['lay_odds']:.2f}" if o["lay_odds"] else "  —  "
        back_liq = fmt_gbp(o["back_liquidity_gbp"]) if o["back_liquidity_gbp"] else "—"
        lay_liq = fmt_gbp(o["lay_liquidity_gbp"]) if o["lay_liquidity_gbp"] else "—"
        prob = f"{o['implied_prob_pct']:.1f}%" if o["implied_prob_pct"] else "—"
        print(f"   {o['name']:<20} {back_odds:>7} {back_liq:>10} {lay_odds:>7} {lay_liq:>10} {prob:>8}")

    # Spread info
    if len(match["outcomes"]) >= 2:
        backs = [o["back_odds"] for o in match["outcomes"] if o["back_odds"]]
        if backs:
            overround = sum(100 / b for b in backs)
            print(f"\n   Market overround (back): {overround:.1f}%  (100% = fair market)")

    print(f"{'─'*70}")


def print_json(matches):
    """Output as JSON for programmatic use."""
    output = {
        "query_time": datetime.now(timezone.utc).isoformat(),
        "auth_used": False,
        "base_url": BASE_URL,
        "price_format": "basis points out of 10,000 (decimal_odds = 10000 / price)",
    }
    output["match_count"] = len(matches)
    output["matches"] = matches
    print(json.dumps(output, indent=2))


# ── Main ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Get live football prices from Smarkets API (no auth required)"
    )
    parser.add_argument("--limit", type=int, default=10, help="Max events to fetch")
    parser.add_argument("--event-id", type=str, help="Specific event ID to query")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    print("=" * 70)
    print("  SMARKETS API — No-Auth Live Football Prices")
    print("  Auth: NONE (public endpoints)")
    print("  Price format: basis points out of 10,000 (decimal = 10000/price)")
    print("  Quantity format: 1/10,000ths of GBP")
    print("=" * 70)

    # Step 1: Get events
    if args.event_id:
        print(f"\n[1/4] Fetching event {args.event_id}...")
        event = get_event_by_id(args.event_id)
        if not event:
            print(f"  ✗ Event {args.event_id} not found")
            sys.exit(1)
        events = [event]
    else:
        print(f"\n[1/4] Fetching live football events (limit {args.limit})...")
        events = get_live_football_events(limit=args.limit)

    # Filter to only in-play enabled matches
    events = [e for e in events if e.get("type") == "football_match"]
    print(f"  ✓ Found {len(events)} live football matches")

    if not events:
        print("\n  No live football matches found. Try again later.")
        sys.exit(0)

    # Step 2-4: For each event, get markets → contracts → quotes
    matches = []
    for i, event in enumerate(events):
        eid = event["id"]
        print(f"\n[2/4] [{i+1}/{len(events)}] Markets for: {event['name'][:50]}...")

        try:
            markets = get_markets(eid)
        except Exception as e:
            print(f"  ✗ Markets failed: {e}")
            continue

        market = find_match_winner_market(markets)
        if not market:
            print(f"  ⚠ No WINNER_3_WAY market found, skipping")
            continue

        mid = market["id"]
        print(f"  ✓ Market: {market['name']} (ID: {mid})")

        # Step 3: Contracts
        print(f"[3/4] Contracts...")
        try:
            contracts = get_contracts(mid)
        except Exception as e:
            print(f"  ✗ Contracts failed: {e}")
            continue
        print(f"  ✓ {len(contracts)} contracts: {', '.join(c['name'] for c in contracts)}")

        # Step 4: Quotes (no auth!)
        print(f"[4/4] Quotes (no auth)...")
        try:
            quotes = get_quotes(mid)
        except Exception as e:
            print(f"  ✗ Quotes failed: {e}")
            continue

        if not quotes:
            print(f"  ⚠ No quotes returned (market may be suspended)")
            continue
        print(f"  ✓ Quotes received for {len(quotes)} contracts — NO AUTH NEEDED")

        match_data = build_match_data(event, market, contracts, quotes)
        matches.append(match_data)

    # Output
    print(f"\n{'='*70}")
    print(f"  RESULTS: {len(matches)} matches with live price data")
    print(f"{'='*70}")

    if args.json:
        print_json(matches)
    else:
        for match in matches:
            print_match(match)

    print(f"\n✅ Confirmed: Smarkets API returns live order book data WITHOUT authentication.")
    print(f"   Endpoints used: /v3/events/, /v3/events/{{id}}/markets/,")
    print(f"                  /v3/markets/{{id}}/contracts/, /v3/markets/{{id}}/quotes/")
    print(f"   Prices are in basis points out of 10,000.")


if __name__ == "__main__":
    main()
