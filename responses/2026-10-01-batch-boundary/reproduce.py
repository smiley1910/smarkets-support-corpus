#!/usr/bin/env python3
"""Reproduce the 2026-10-01 batch-boundary test:
quotes 200 OK / 201+ 404; volumes 300 OK / 301+ 404. Public routes, no auth."""
import json, time, urllib.request, urllib.error
from datetime import datetime, timezone

BASE = "https://api.smarkets.com"
UA = {"User-Agent": "smarkets-boundary-probe/1.0", "Accept": "application/json"}

def get(path, timeout=30):
    req = urllib.request.Request(BASE + path, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
s, b = get(f"/v3/events/?type=football_match&state=upcoming&limit=50&start_datetime_min={now}&with_new_type=False&include_hidden=False")
events = json.loads(b).get("events", [])
market_ids, seen = [], set()
for ev in events:
    if len(market_ids) >= 310:
        break
    s, b = get(f"/v3/events/{ev.get('id')}/markets/")
    if s != 200:
        continue
    for m in json.loads(b).get("markets", []):
        _id = str(m.get("id"))
        if _id not in seen:
            seen.add(_id)
            market_ids.append(_id)
print(f"collected {len(market_ids)} live market ids")

for n in (200, 201):
    s, b = get("/v3/markets/" + ",".join(market_ids[:n]) + "/quotes/")
    print(f"quotes  n={n:>3}  status={s}  bytes={len(b):>7}  {b[:90].decode('utf-8','ignore')}")
    time.sleep(1.5)
for n in (300, 301):
    s, b = get("/v3/markets/" + ",".join(market_ids[:n]) + "/volumes/")
    print(f"volumes n={n:>3}  status={s}  bytes={len(b):>7}  {b[:90].decode('utf-8','ignore')}")
    time.sleep(1.5)
