#!/usr/bin/env python3
"""Reproduce the 2026-10-01 verification of the France vs Italy (event 45342825)
support draft: market existence, contracts, quotes shape, endpoint paths, spec wording.

Read-only unauthenticated GETs. Run: python3 reproduce.py
Note: reruns at a later date will fail the 165/all-open checks as the event moves.
"""
import json, os, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))

def get(url, fn):
    req = urllib.request.Request(url, headers={"User-Agent": "smarkets-support-verify/reproduce"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
    open(os.path.join(BASE, fn), "wb").write(body)
    return json.loads(body)

ev = get("https://api.smarkets.com/v3/events/45342825/", "event_45342825.json")
mk = get("https://api.smarkets.com/v3/events/45342825/markets/", "markets_45342825.json")
ct = get("https://api.smarkets.com/v3/markets/166809918/contracts/", "contracts_166809918.json")
q1 = get("https://api.smarkets.com/v3/markets/166809918/quotes/", "quotes_166809918.json")
get("https://api.smarkets.com/v3/markets/166809839/quotes/", "quotes_166809839.json")
spec = get("https://api.smarkets.com/v0/control/openapi/?tags=trading_api", "openapi_trading_api.json")

fails = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)

e = ev["events"][0]
check("event 45342825 is France vs Italy", str(e["id"]) == "45342825" and e["name"] == "France vs Italy")

ms = mk["markets"]
check("165 markets returned", len(ms) == 165)
check("all 165 marked open", all(m["state"] == "open" for m in ms))

byid = {str(m["id"]): m for m in ms}
check("France O/U ids 166809839-842 present", all(str(i) in byid for i in range(166809839, 166809843)))
check("Italy O/U ids 166809849-852 present", all(str(i) in byid for i in range(166809849, 166809853)))
check("both-halves ids 166809916/26/18/28 present",
      all(str(i) in byid for i in (166809916, 166809926, 166809918, 166809928)))
check("market objects carry id/name/state", all({"id", "name", "state"} <= set(m) for m in ms))

cids = {c["name"]: str(c["id"]) for c in ct["contracts"]}
check("market 166809918 contracts: Yes=460736180 No=460736181",
      cids.get("Yes") == "460736180" and cids.get("No") == "460736181")

check("quotes keyed by contract id", set(q1) == {"460736180", "460736181"})
ok_shape = all(isinstance(v.get("bids"), list) and isinstance(v.get("offers"), list) for v in q1.values())
ok_entries = all(set(b) == {"price", "quantity"} for v in q1.values() for b in v["bids"] + v["offers"])
ok_uncrossed = all(
    max((b["price"] for b in v["bids"]), default=0) < min((o["price"] for o in v["offers"]), default=10000)
    for v in q1.values())
check("quotes items have price+quantity only", ok_shape and ok_entries)
check("books uncrossed (max bid price < min offer price)", ok_uncrossed)

paths = spec["paths"]
for p in ("/v3/events/{event_ids}/markets/", "/v3/markets/{market_ids}/contracts/",
          "/v3/markets/{market_ids}/quotes/"):
    check("spec path exists: " + p, p in paths)

qs = paths["/v3/markets/{market_ids}/quotes/"]["get"]["responses"]["200"]["content"]["application/json"] \
    ["schema"]["additionalProperties"]["properties"]
pdesc = qs["bids"]["items"]["properties"]["price"]["description"]
qdesc = qs["bids"]["items"]["properties"]["quantity"]["description"]
check("spec: decimal odds = 10000/price", "divide 10000 by it" in pdesc)
check("spec: quantity in 1/100 UK penny (500 = 0.05 GBP)",
      "1/100 of a UK penny" in qdesc and "0.05 GBP" in qdesc)

print("\nRESULT:", "ALL CHECKS PASSED" if not fails else f"{len(fails)} FAILURES: {fails}")
