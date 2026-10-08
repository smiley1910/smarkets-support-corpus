#!/usr/bin/env python3
"""Probe: compare default login vs use_auth_v2 login for cookie/refresh flow.
Reads creds from ~/smarkets-multiples-tester/.env. Prints fingerprints only, never raw tokens."""
import json, hashlib, re, os
import requests

ENV = os.path.expanduser("~/smarkets-multiples-tester/.env")
creds = {}
for line in open(ENV):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        creds[k.strip()] = v.strip().strip('"').strip("'")
u = creds.get("SMARKETS_EMAIL"); p = creds.get("SMARKETS_PASSWORD")

def fp(s):
    return hashlib.sha256(s.encode()).hexdigest()[:10] if s else None

BASE = "https://api.smarkets.com"

def attempt(label, body):
    print(f"\n=== {label} ===")
    r = requests.post(f"{BASE}/v3/sessions/", json=body, timeout=20, allow_redirects=False)
    print("STATUS:", r.status_code)
    tok = None
    try:
        d = r.json()
        print("BODY KEYS:", sorted(d.keys()))
        for k, v in d.items():
            if isinstance(v, str) and len(v) > 20:
                print(f"  {k}: len={len(v)} fp={fp(v)}")
            else:
                print(f"  {k}: {v}")
        tok = d.get("token")
    except Exception:
        print("BODY (first 300):", r.text[:300])
    # raw set-cookie list (urllib3 may keep multiple headers)
    try:
        sc_list = r.raw.headers.getlist("Set-Cookie")
    except Exception:
        sc_list = []
    if not sc_list and r.headers.get("Set-Cookie"):
        sc_list = [r.headers.get("Set-Cookie")]
    print("SET-COOKIE headers:", len(sc_list))
    for sc in sc_list:
        names = re.findall(r"([A-Za-z0-9_\-]+)=", sc.split(";")[0] + ";" + sc)
        # get cookie name(s) from first token pair
        first = sc.split(";")[0]
        print("   cookie:", first.split("=")[0], "| attrs:", "; ".join(sc.split(";")[1:])[:120])
    # logout
    if tok:
        o = requests.delete(f"{BASE}/v3/sessions/", headers={"Authorization": f"Session-Token {tok}"}, timeout=20, allow_redirects=False)
        print("LOGOUT:", o.status_code)
    return r

attempt("A: default login (remember=true)", {"username": u, "password": p, "remember": True})
attempt("B: use_auth_v2=true login (remember=true)", {"username": u, "password": p, "remember": True, "use_auth_v2": True})
