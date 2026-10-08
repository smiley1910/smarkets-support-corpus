#!/usr/bin/env python3
"""Authenticated example probe for Smarkets ticket verification (read-only).

Reuses the greyhound bot's login-once session (login-once, file cache,
verify-before-use, shared 5/300s floor) as a READER. Default spends no
login: with --allow-login absent, resolve(fresh_login=False) uses the env
token or live cache only and fails closed otherwise, so a ticket probe can
never steal the live loop's budget or invalidate its token.

Saves raw JSON evidence under responses/<stamp>-auth-probe/ and prints only
metadata (names, ids, counts, best touch). The session token is NEVER
printed, logged, or written to disk by this script.

Usage:
  python3 auth_example_probe.py --event-id 45342825 --market-ids 166809918
  python3 auth_example_probe.py --event-id 45342825   # all markets (caps: quotes 200/call)
  python3 auth_example_probe.py --event-id 45342825 --market-ids 166809918 --allow-login
"""

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://api.smarkets.com"
UA = "smarkets-api-support/auth-probe"
BOT_SRC = os.path.expanduser("~/greyhound-api-bot-dev/src")
DEFAULT_CACHE = os.path.expanduser("~/greyhound-api-bot-dev/.smarkets_session")
DEFAULT_RESP = os.path.expanduser("~/smarkets-api-support/responses")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _get(token, path):
    req = urllib.request.Request(
        BASE + path,
        headers={"Authorization": "Session-Token " + token,
                 "User-Agent": UA, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.build_opener(_NoRedirect).open(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")[:300]
        except Exception:
            body = ""
        return e.code, {"_http_error": e.code, "_body": body}


def _touch(book):
    bids = book.get("bids") or []
    offers = book.get("offers") or []
    best_bid = max((l.get("price", 0) for l in bids), default=None)
    best_offer = min((l.get("price", 0) for l in offers), default=None)
    dec = lambda p: round(10000 / p, 3) if p else None
    return best_bid, dec(best_bid), best_offer, dec(best_offer)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event-id", required=True)
    ap.add_argument("--market-ids", default="")
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--allow-login", action="store_true")
    ap.add_argument("--cache-path", default=DEFAULT_CACHE)
    a = ap.parse_args()

    sys.path.insert(0, BOT_SRC)
    from market.session import SmarketsSession  # read-only import; bot files untouched

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d-auth-probe")
    out = a.out_dir or os.path.join(DEFAULT_RESP, stamp)
    os.makedirs(out, exist_ok=True)

    sess = SmarketsSession(cache_path=a.cache_path)
    try:
        token = sess.resolve(fresh_login=a.allow_login)
    except Exception as e:
        print("WARNING: unverified example — authenticated resolve refused "
              "(%s: %s). No login spent." % (type(e).__name__, str(e)[:150]))
        return 2
    print("auth: OK source=%s token_len=%d" % (sess.source, len(token)))

    def save(name, status, payload):
        with open(os.path.join(out, name), "w") as f:
            json.dump({"status": status, "body": payload}, f)
        return status

    st, ev = _get(token, "/v3/events/%s/" % a.event_id)
    save("event_%s.json" % a.event_id, st, ev)
    events = (ev.get("events") if isinstance(ev, dict) else None) or []
    print("event: status=%s name=%s" % (st, events[0].get("name") if events else "?"))
    if st != 200:
        return 1

    st, mk = _get(token, "/v3/events/%s/markets/" % a.event_id)
    save("markets_%s.json" % a.event_id, st, mk)
    markets = (mk.get("markets") if isinstance(mk, dict) else None) or []
    print("markets: status=%s count=%d" % (st, len(markets)))
    if st != 200:
        return 1

    want = [m.strip() for m in a.market_ids.split(",") if m.strip()]
    if not want:
        want = [m.get("id") for m in markets[:200]]
    by_id = {m.get("id"): m for m in markets}
    for mid in want:
        m = by_id.get(mid, {})
        print("market: %s id=%s state=%s" % (m.get("name", "?"), mid, m.get("state", "?")))

    for i in range(0, len(want), 100):
        chunk = ",".join(want[i:i + 100])
        st, co = _get(token, "/v3/markets/%s/contracts/" % chunk)
        save("contracts_%d.json" % (i // 100), st, co)
        n = len(co.get("contracts", [])) if isinstance(co, dict) else 0
        print("contracts: status=%s chunk=%d count=%d" % (st, i // 100, n))

    for i in range(0, len(want), 200):
        chunk = ",".join(want[i:i + 200])
        st, qu = _get(token, "/v3/markets/%s/quotes/" % chunk)
        save("quotes_%d.json" % (i // 200), st, qu)
        keys = [k for k in qu.keys() if not k.startswith("_")] if isinstance(qu, dict) else []
        print("quotes: status=%s chunk=%d contract_keys=%d" % (st, i // 200, len(keys)))
        for cid, book in (qu.items() if isinstance(qu, dict) else []):
            if cid.startswith("_") or not isinstance(book, dict):
                continue
            bb, bb_d, bo, bo_d = _touch(book)
            print("  contract %s best_bid=%s (%s) best_offer=%s (%s)" % (cid, bb, bb_d, bo, bo_d))
    print("evidence: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
