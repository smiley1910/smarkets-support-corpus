#!/usr/bin/env python3
"""Paired 36-min test: does cookie/refresh-token participation stop the ~20-min AUTH_REQUIRED death?

CONTROL arm  = header-only, single fixed token (mirrors the customer's failing client).
TREATMENT arm = sends Authorization + Cookie: User-Session-Token; Refresh-Token,
                adopting any new User-Session-Token the server issues (engineers' fix).

Reads creds from ~/smarkets-multiples-tester/.env. Logs fingerprints only, never raw tokens.
"""
import argparse, hashlib, json, os, re, sys, time, traceback
from datetime import datetime, timezone
import requests

ENV = os.path.expanduser("~/smarkets-multiples-tester/.env")
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "run-cookie-refresh.log")
RESULTS = os.path.join(HERE, "run-cookie-refresh-results.json")

ap = argparse.ArgumentParser()
ap.add_argument("--minutes", type=int, default=36)
ap.add_argument("--interval", type=int, default=20)
args = ap.parse_args()

creds = {}
for line in open(ENV):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        creds[k.strip()] = v.strip().strip('"').strip("'")
u, p = creds.get("SMARKETS_EMAIL"), creds.get("SMARKETS_PASSWORD")
BASE = "https://api.smarkets.com"

def fp(s):
    return hashlib.sha256(s.encode()).hexdigest()[:10] if s else None

def now():
    return datetime.now(timezone.utc).strftime("%H:%M:%S")

def log(msg):
    line = f"[{now()}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def login(label):
    r = requests.post(f"{BASE}/v3/sessions/",
                      json={"username": u, "password": p, "remember": True},
                      timeout=20, allow_redirects=False)
    if r.status_code != 201:
        log(f"FATAL {label} login status {r.status_code}: {r.text[:200]}")
        sys.exit(1)
    d = r.json()
    token = d.get("token")
    refresh = d.get("refresh_token")
    try:
        sc = r.raw.headers.getlist("Set-Cookie")
    except Exception:
        sc = []
    ust_cookie = None
    for c in sc:
        m = re.match(r"User-Session-Token=([^;]+)", c)
        if m:
            ust_cookie = m.group(1)
    log(f"{label} login 201 | token fp={fp(token)} | refresh fp={fp(refresh)} | "
        f"cookie User-Session-Token fp={fp(ust_cookie)} | stop={d.get('stop')}")
    return {"token": token, "refresh": refresh, "ust": ust_cookie or token, "stop": d.get("stop")}

def poll(label, headers):
    try:
        r = requests.get(f"{BASE}/v3/orders/", headers=headers, timeout=20, allow_redirects=False)
        sc = []
        try:
            sc = r.raw.headers.getlist("Set-Cookie")
        except Exception:
            pass
        return r.status_code, r.text[:200], sc
    except Exception as e:
        return None, f"EXC:{e}", []

log(f"=== START paired test: {args.minutes} min, {args.interval}s interval ===")
with open(LOG, "a") as f:
    f.write(f"=== START {datetime.now(timezone.utc).isoformat()} ===\n")

ctl = login("CONTROL")
trt = login("TREATMENT")

t0 = time.time()
end = t0 + args.minutes * 60
interval = args.interval
results = {
    "start_utc": datetime.now(timezone.utc).isoformat(),
    "control": {"first_401": None, "last_200": None, "count_200": 0, "count_401": 0, "cookie_updates": []},
    "treatment": {"first_401": None, "last_200": None, "count_200": 0, "count_401": 0, "cookie_updates": []},
}

k = 0
while time.time() < end:
    k += 1
    t_elapsed = int(time.time() - t0)
    mmss = f"{t_elapsed // 60:02d}:{t_elapsed % 60:02d}"

    # control: header only, fixed token
    cs, ct, _ = poll("CONTROL", {"Authorization": f"Session-Token {ctl['token']}"})

    # treatment: header (latest token) + both cookies
    ts, tt, tsc = poll("TREATMENT", {
        "Authorization": f"Session-Token {trt['token']}",
        "Cookie": f"User-Session-Token={trt['ust']}; Refresh-Token={trt['refresh']}",
    })
    treat_note = ""
    for c in tsc:
        m = re.match(r"User-Session-Token=([^;]+)", c)
        if m and m.group(1) != trt["ust"]:
            old = fp(trt["ust"]); new = fp(m.group(1))
            trt["ust"] = m.group(1)
            trt["token"] = m.group(1)  # adopt newest as auth token too
            treat_note += f" UST-UPDATE {old}->{new}"
            results["treatment"]["cookie_updates"].append({"t": mmss, "from": old, "to": new})
        m2 = re.match(r"Refresh-Token=([^;]+)", c)
        if m2 and m2.group(1) != trt["refresh"]:
            old = fp(trt["refresh"]); trt["refresh"] = m2.group(1)
            treat_note += f" REFRESH-UPDATE {old}->{fp(trt['refresh'])}"
    if tsc and not treat_note:
        names = [c.split("=")[0] for c in tsc]
        treat_note += f" sc:{','.join(names)}"

    ctl_note = ""
    if cs == 401:
        if results["control"]["first_401"] is None:
            results["control"]["first_401"] = mmss
        results["control"]["count_401"] += 1
        ctl_note = " AUTH_REQUIRED"
    elif cs == 200:
        results["control"]["count_200"] += 1
        results["control"]["last_200"] = mmss
    if ts == 401:
        if results["treatment"]["first_401"] is None:
            results["treatment"]["first_401"] = mmss
        results["treatment"]["count_401"] += 1
        treat_note += " AUTH_REQUIRED"
    elif ts == 200:
        results["treatment"]["count_200"] += 1
        results["treatment"]["last_200"] = mmss

    log(f"t+{mmss} | CTL {cs}{ctl_note} | TRT {ts}{treat_note}")
    time.sleep(interval)

# summary
def verdict(name):
    r = results[name]
    if r["first_401"] is None:
        return f"{name}: SURVIVED full {args.minutes} min, {r['count_200']}x 200, no 401"
    return (f"{name}: first 401 at t+{r['first_401']} ({r['count_200']}x 200 before), "
            f"last 200 at t+{r['last_200']}")

log("=== SUMMARY ===")
log(verdict("control"))
log(verdict("treatment"))
results["end_utc"] = datetime.now(timezone.utc).isoformat()
results["verdict_control"] = verdict("control")
results["verdict_treatment"] = verdict("treatment")
with open(RESULTS, "w") as f:
    json.dump(results, f, indent=2)
log(f"results saved -> {RESULTS}")
