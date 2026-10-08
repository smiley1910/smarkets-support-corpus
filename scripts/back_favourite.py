#!/usr/bin/env python3
"""
Smarkets Favourite Backer — finds the first horse race, backs the favourite with €0.05.

Usage:
  export SMARKETS_EMAIL="..."
  export SMARKETS_PASSWORD="..."
  python3 back_favourite.py [--dry-run] [--stake 0.05]
"""

import os
import sys
import json
import time
import argparse
import requests

BASE_URL = "https://api.smarkets.com"
TIMEOUT = 15
UA = "SmarketsFavBacker/1.0"


def login(email, password):
    """Login and return session token."""
    r = requests.post(
        f"{BASE_URL}/v3/sessions/",
        json={"username": email, "password": password},
        headers={"User-Agent": UA},
        timeout=TIMEOUT,
        allow_redirects=False,
    )
    if r.status_code in (200, 201):
        data = r.json()
        token = data.get("token")
        if token:
            return token
    print(f"Login failed: {r.status_code} {r.text[:200]}")
    return None


def api_get(path, token, params=None):
    """Authenticated GET request."""
    r = requests.get(
        f"{BASE_URL}{path}",
        params=params,
        headers={
            "Authorization": f"Session-Token {token}",
            "User-Agent": UA,
        },
        timeout=TIMEOUT,
        allow_redirects=False,
    )
    return r


def find_horse_racing_event(token):
    """Find the next upcoming horse racing event using search + event fetch."""
    from datetime import datetime, timezone

    # Step 1: Search for horse racing events
    r = api_get("/v3/search/horse/", token)
    if r.status_code != 200:
        print(f"  Search failed: {r.status_code}")
        return []

    search_ids = r.json().get("search_result_event_ids", [])
    if not search_ids:
        return []

    # Step 2: Fetch event details in batches (max 10 per request)
    all_events = []
    for i in range(0, len(search_ids), 10):
        batch = search_ids[i:i+10]
        r = api_get(f"/v3/events/{','.join(batch)}/", token)
        if r.status_code == 200:
            all_events.extend(r.json().get("events", []))

    # Step 3: Filter for horse_racing_race type and upcoming start time
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    horse_events = [
        e for e in all_events
        if e.get("type") == "horse_racing_race"
        and e.get("start_datetime", "") > now
    ]

    # Sort by start time
    horse_events.sort(key=lambda e: e.get("start_datetime", ""))

    return horse_events


def get_markets_for_event(token, event_id):
    """Get markets for an event."""
    r = api_get(f"/v3/events/{event_id}/markets/", token, params={
        "limit": 10,
    })
    if r.status_code == 200:
        return r.json().get("markets", [])
    return []


def get_contracts_for_market(token, market_id):
    """Get contracts (horses) for a market."""
    r = api_get(f"/v3/markets/{market_id}/contracts/", token)
    if r.status_code == 200:
        return r.json().get("contracts", [])
    return []


def get_quotes(token, market_id):
    """Get quotes for a market — returns back/lay prices per contract."""
    r = api_get(f"/v3/markets/{market_id}/quotes/", token)
    if r.status_code == 200:
        return r.json()
    return {}


def find_favourite(quotes_data, contracts):
    """Find the favourite — the contract with the lowest decimal odds (highest offer price in basis points).

    Quotes structure: {contract_id: {"bids": [...], "offers": [...]}}
    - bids = back orders resting in the book (sorted descending by price)
    - offers = lay orders resting in the book (sorted ascending by price)
    - To BACK, you match the lowest offer (best available back price)
    - Favourite = highest best-offer price = lowest decimal odds
    """
    # Build a lookup of contract_id -> name
    contract_names = {}
    for c in contracts:
        cid = str(c.get("id", ""))
        name = c.get("name", c.get("runner_name", f"Contract {cid}"))
        contract_names[cid] = name

    best_offer_price = None
    best_contract_id = None
    best_contract_name = None

    for contract_id, q_data in quotes_data.items():
        cid = str(contract_id)
        offers = q_data.get("offers", [])
        if not offers:
            continue
        # Offers are sorted ascending — first one is the best (lowest) available to back at
        best_price = offers[0].get("price", 0)
        if best_price and (best_offer_price is None or best_price > best_offer_price):
            best_offer_price = best_price
            best_contract_id = cid
            best_contract_name = contract_names.get(cid, f"Contract {cid}")

    return best_contract_id, best_contract_name, best_offer_price


def place_back_order(token, market_id, contract_id, price, quantity, dry_run=False):
    """Place a back (buy) order on the exchange."""
    order = {
        "market_id": str(market_id),
        "contract_id": str(contract_id),
        "price": int(price),
        "quantity": int(quantity),
        "side": "buy",
        "type": "immediate_or_cancel",
    }

    print(f"\n  Order details:")
    print(f"    Market:     {market_id}")
    print(f"    Contract:   {contract_id}")
    print(f"    Price:      {price} (decimal odds: {10000/price:.2f})")
    print(f"    Quantity:   {quantity}")
    print(f"    Back stake: €{quantity * price / 100000000:.2f}")
    print(f"    Side:       buy (back)")
    print(f"    Type:       immediate_or_cancel")

    if dry_run:
        print(f"    [DRY RUN — no order placed]")
        return None

    r = requests.post(
        f"{BASE_URL}/v3/orders/",
        json=order,
        headers={
            "Authorization": f"Session-Token {token}",
            "User-Agent": UA,
            "Content-Type": "application/json",
        },
        timeout=TIMEOUT,
        allow_redirects=False,
    )

    print(f"\n  Response: {r.status_code}")
    try:
        data = r.json()
        print(f"  Body: {json.dumps(data, indent=2)}")
    except Exception:
        print(f"  Body: {r.text[:500]}")

    return r


def main():
    parser = argparse.ArgumentParser(description="Back the favourite in the first horse race found")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without placing orders")
    parser.add_argument("--stake", type=float, default=0.05, help="Back stake in currency (default: 0.05)")
    args = parser.parse_args()

    email = os.environ.get("SMARKETS_EMAIL")
    password = os.environ.get("SMARKETS_PASSWORD")

    if not email or not password:
        print("Error: Set SMARKETS_EMAIL and SMARKETS_PASSWORD environment variables")
        sys.exit(1)

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║        Smarkets Favourite Backer — €0.05 back bet            ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    # Step 1: Login
    print("\n[1/5] Logging in...")
    token = login(email, password)
    if not token:
        sys.exit(1)
    print(f"  ✓ Logged in (token: {token[:20]}...)")

    # Step 2: Find horse racing events
    print("\n[2/5] Finding horse racing events...")
    events = find_horse_racing_event(token)
    if not events:
        print("  ✗ No upcoming events found")
        sys.exit(1)

    print(f"  Found {len(events)} event(s):")
    for i, e in enumerate(events[:5]):
        name = e.get("name", "Unknown")
        start = e.get("start_datetime", e.get("start", "?"))
        eid = e.get("id", "?")
        print(f"    [{i}] {name} (ID: {eid}, starts: {start})")

    event = events[0]
    event_id = event["id"]
    event_name = event.get("name", "Unknown")
    print(f"\n  → Selected: {event_name} (ID: {event_id})")

    # Step 3: Get markets for the event
    print(f"\n[3/5] Getting markets for event {event_id}...")
    markets = get_markets_for_event(token, event_id)
    if not markets:
        print("  ✗ No markets found")
        sys.exit(1)

    print(f"  Found {len(markets)} market(s):")
    for i, m in enumerate(markets[:5]):
        mname = m.get("name", m.get("market_type", "Unknown"))
        mid = m.get("id", "?")
        print(f"    [{i}] {mname} (ID: {mid})")

    # Find the win market (usually the first one, or named "win")
    market = markets[0]
    market_id = market["id"]
    market_name = market.get("name", market.get("market_type", "Unknown"))
    print(f"\n  → Selected: {market_name} (ID: {market_id})")

    # Step 4: Get contracts and quotes
    print(f"\n[4/5] Getting contracts and quotes for market {market_id}...")
    contracts = get_contracts_for_market(token, market_id)
    print(f"  Found {len(contracts)} contract(s):")
    for c in contracts:
        cid = c.get("id", "?")
        cname = c.get("name", c.get("runner_name", f"Contract {cid}"))
        print(f"    - {cname} (ID: {cid})")

    quotes_data = get_quotes(token, market_id)
    print(f"\n  Raw quotes response:")
    print(f"  {json.dumps(quotes_data, indent=2)[:1000]}")

    # Step 5: Find the favourite and place the bet
    print(f"\n[5/5] Finding favourite and placing bet...")
    contract_id, contract_name, best_back_price = find_favourite(quotes_data, contracts)

    if not contract_id or not best_back_price:
        print("  ✗ Could not determine favourite from quotes")
        print(f"  Quotes data: {json.dumps(quotes_data, indent=2)[:2000]}")
        sys.exit(1)

    decimal_odds = 10000 / best_back_price
    # Calculate quantity for desired back stake
    # back_stake = quantity * price / 100000000
    # quantity = back_stake * 100000000 / price
    quantity = int(args.stake * 100000000 / best_back_price)

    print(f"\n  ★ Favourite: {contract_name}")
    print(f"    Contract ID: {contract_id}")
    print(f"    Back price:  {best_back_price} (decimal odds: {decimal_odds:.2f})")
    print(f"    Stake:       €{args.stake:.2f}")
    print(f"    Quantity:    {quantity}")

    place_back_order(token, market_id, contract_id, best_back_price, quantity, dry_run=args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
