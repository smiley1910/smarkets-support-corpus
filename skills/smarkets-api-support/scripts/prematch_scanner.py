#!/usr/bin/env python3
"""
Smarkets API — Prematch Football Scanner

Fetches upcoming football events from the Smarkets public API (no auth required),
returns league, date, kickoff time, match-winner odds, and top-of-book liquidity.
Also checks whether coverage_delay appears on prematch events.

Usage:
    python3 prematch_scanner.py [--limit 50] [--today-only]

Price format: basis points out of 10,000 (decimal = 10000/price)
Quantity format: 1/10,000ths of GBP (gbp = qty / 10000)

Rate limit: 50 RPM (1.2s between requests) — respects the documented quotes
endpoint limit of 50 req/60s for API users.

Dependencies: requests (pip install requests)
"""

import requests
import json
import time
import argparse
from datetime import datetime, timezone

BASE_URL = "https://api.smarkets.com"
TIMEOUT = 15
RATE_LIMIT_SECONDS = 1.2  # 50 RPM
DENOM = 10_000
QTY_DENOM = 10_000


def price_to_decimal(price):
    if not price or price == 0:
        return None
    return round(DENOM / price, 2)


def qty_to_gbp(quantity):
    if not quantity:
        return 0
    return round(quantity / QTY_DENOM, 2)


def fmt_gbp(amount):
    if amount >= 1000:
        return f"£{amount/1000:.1f}k"
    return f"£{amount:.0f}"


def get_upcoming_football(limit=50):
    r = requests.get(
        f"{BASE_URL}/v3/events/",
        params={"type": "football_match", "state": "upcoming", "limit": limit},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get("events", [])


def get_markets(event_id):
    r = requests.get(f"{BASE_URL}/v3/events/{event_id}/markets/", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json().get("markets", [])


def get_contracts(market_id):
    r = requests.get(f"{BASE_URL}/v3/markets/{market_id}/contracts/", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json().get("contracts", [])


def get_quotes(market_id):
    r = requests.get(f"{BASE_URL}/v3/markets/{market_id}/quotes/", timeout=TIMEOUT)
    if r.status_code != 200:
        return {}
    return r.json()


def get_event_state(event_id):
    r = requests.get(f"{BASE_URL}/v3/events/{event_id}/states/", timeout=TIMEOUT)
    r.raise_for_status()
    states = r.json().get("event_states", [])
    return states[0] if states else {}


def find_match_winner_market(markets):
    for m in markets:
        mtype = m.get("market_type", {})
        if isinstance(mtype, dict) and mtype.get("name") == "WINNER_3_WAY":
            return m
    for m in markets:
        if "full-time result" in m.get("name", "").lower():
            return m
    return None


def get_league_name(event, events_list):
    parent_id = event.get("parent_id")
    if not parent_id:
        return "Unknown League"
    for e in events_list:
        if e["id"] == parent_id:
            return e.get("name", "Unknown League")
    try:
        r = requests.get(f"{BASE_URL}/v3/events/", params={"id": parent_id}, timeout=TIMEOUT)
        if r.status_code == 200:
            events = r.json().get("events", [])
            if events:
                return events[0].get("name", "Unknown League")
    except:
        pass
    return f"League ID {parent_id}"


def main():
    parser = argparse.ArgumentParser(description="Smarkets prematch football scanner")
    parser.add_argument("--limit", type=int, default=50, help="Max events to fetch")
    parser.add_argument("--today-only", action="store_true", help="Only today's matches")
    parser.add_argument("--num", type=int, default=10, help="Number of matches to display")
    args = parser.parse_args()

    print("=" * 90)
    print("  SMARKETS API — Prematch Football Scanner")
    print("  Rate limit: 50 RPM (1.2s between requests)")
    print("=" * 90)

    events = get_upcoming_football(limit=args.limit)
    print(f"\n[1] Found {len(events)} upcoming matches")

    if args.today_only:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        events = [e for e in events if e.get("start_date") == today]
        print(f"    Today ({today}): {len(events)} matches")

    events = events[:args.num]
    print(f"    Processing first {len(events)} matches")

    results = []
    coverage_delays_found = []

    for i, event in enumerate(events):
        eid = event["id"]
        name = event["name"]
        start = event.get("start_datetime", "")
        league = get_league_name(event, events)

        time.sleep(RATE_LIMIT_SECONDS)
        state = get_event_state(eid)
        info = state.get("info", {})
        cd = info.get("coverage_delay")
        betgenius = info.get("is_betgenius_booked")
        if cd is not None:
            coverage_delays_found.append({
                "event": name, "event_id": eid,
                "coverage_delay": cd, "is_betgenius_booked": betgenius,
                "state": event.get("state"),
            })

        time.sleep(RATE_LIMIT_SECONDS)
        markets = get_markets(eid)
        market = find_match_winner_market(markets)
        if not market:
            print(f"\n  [{i+1}/{len(events)}] {name} — no WINNER_3_WAY market, skipping")
            continue

        mid = market["id"]
        time.sleep(RATE_LIMIT_SECONDS)
        contracts = get_contracts(mid)
        contract_map = {c["id"]: c for c in contracts}

        time.sleep(RATE_LIMIT_SECONDS)
        quotes = get_quotes(mid)

        outcomes = []
        for cid, book in quotes.items():
            contract = contract_map.get(cid, {})
            cname = contract.get("name", cid)
            ctype = contract.get("contract_type", {}).get("name", "")
            bids = book.get("bids", [])
            offers = book.get("offers", [])
            best_bid = bids[0] if bids else None
            best_offer = offers[0] if offers else None
            outcomes.append({
                "name": cname, "type": ctype,
                "back_odds": price_to_decimal(best_offer["price"]) if best_offer else None,
                "back_liq": qty_to_gbp(best_offer["quantity"]) if best_offer else 0,
                "lay_odds": price_to_decimal(best_bid["price"]) if best_bid else None,
                "lay_liq": qty_to_gbp(best_bid["quantity"]) if best_bid else 0,
            })

        type_order = {"HOME": 0, "DRAW": 1, "AWAY": 2}
        outcomes.sort(key=lambda x: type_order.get(x["type"], 99))

        results.append({
            "league": league, "match": name, "kickoff": start,
            "event_id": eid, "market_id": mid, "outcomes": outcomes,
            "coverage_delay": cd, "is_betgenius_booked": betgenius,
        })

        print(f"\n  [{i+1}/{len(events)}] {name}")
        print(f"    League: {league}")
        print(f"    Kickoff: {start}")
        print(f"    coverage_delay: {cd}  |  betgenius: {betgenius}")
        print(f"    {'Outcome':<25} {'Back':>7} {'Back Liq':>10} {'Lay':>7} {'Lay Liq':>10}")
        print(f"    {'─'*25} {'─'*7} {'─'*10} {'─'*7} {'─'*10}")
        for o in outcomes:
            back = f"{o['back_odds']:.2f}" if o["back_odds"] else "  —"
            lay = f"{o['lay_odds']:.2f}" if o["lay_odds"] else "  —"
            bl = fmt_gbp(o["back_liq"]) if o["back_liq"] else "—"
            ll = fmt_gbp(o["lay_liq"]) if o["lay_liq"] else "—"
            print(f"    {o['name']:<25} {back:>7} {bl:>10} {lay:>7} {ll:>10}")

    print(f"\n{'='*90}")
    print(f"  COVERAGE_DELAY ANALYSIS")
    print(f"{'='*90}")
    print(f"\n  Total prematch events checked: {len(events)}")
    print(f"  Events with coverage_delay set: {len(coverage_delays_found)}")
    if coverage_delays_found:
        print(f"\n  ⚠ coverage_delay FOUND on prematch events:")
        for cd in coverage_delays_found:
            print(f"    {cd['event']} | delay={cd['coverage_delay']} | betgenius={cd['is_betgenius_booked']}")
    else:
        print(f"\n  ✅ coverage_delay is NULL/absent on ALL prematch events")

    output = {
        "query_time": datetime.now(timezone.utc).isoformat(),
        "events_checked": len(events),
        "coverage_delay_on_prematch": len(coverage_delays_found),
        "coverage_delay_details": coverage_delays_found,
        "matches": results,
    }
    print(f"\n  {len(results)} matches scanned. JSON output available.")


if __name__ == "__main__":
    main()
