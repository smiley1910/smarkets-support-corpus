# Rate Limit Discovery Script — Audit Patterns

Reference for building and auditing concurrent API rate limit discovery scripts. Distilled from a 6-pass audit of `rate_limit_discovery.py` (Smarkets API, July 2026).

## Script Location

- **Full script:** `~/smarkets-api-support/scripts/rate_limit_discovery.py`
- **GitHub:** https://github.com/smiley1910/smarkets-rate-limit-discovery
- **Lightweight version:** `~/smarkets-api-support/scripts/rate_limit_quick_check.py`

## 4-Phase Discovery Methodology

1. **Phase 1 — Smoke test:** One request per endpoint, capture status + `X-RateLimit-*` headers. Confirms endpoint reachability and documented limits.
2. **Phase 2 — Per-endpoint probe:** Hammer each safe endpoint with concurrent threads until 429, then wait for reset. Discovers actual per-endpoint limits.
3. **Phase 3 — Shared pool test:** Fire all endpoints concurrently to test if the global limit is truly shared across endpoints.
4. **Phase 4 — Aggregate analysis:** Compare documented vs discovered limits, calculate the 1200 RPM breakdown.

## Critical Pitfalls (All Caused Bugs in The Original Script)

### 1. RFC 2822 Timestamp Parsing

Smarkets returns 429 `expiry` as RFC 2822 (`"Thu, 16 Jul 2026 11:21:18 GMT"`), NOT ISO 8601. `datetime.fromisoformat()` always crashes. Use:

```python
from email.utils import parsedate_to_datetime
expiry_dt = parsedate_to_datetime(error_data["expiry"])
```

This was the root cause of incorrect fallback wait times — every endpoint fell back to a hardcoded 65s instead of using the actual window reset.

### 2. Thread Safety for Shared State

When hammering with concurrent threads, shared mutable state (`first_429`, `error_429_data`, `request_count`, `stop_flag`, `rate_headers_last`) must be guarded by `threading.Lock()`.

**Bug pattern (race condition):** Multiple threads hit 429 simultaneously and overwrite each other's values. Last writer wins instead of first.

**Fix pattern (first-writer-wins):**
```python
with lock:
    if first_429 is None:
        first_429 = time.time()
        error_429_data = r.json()
```

Check `is None` inside the lock — don't check outside and then acquire, that's still a race.

### 3. Falsy Zero Handling in Python

`if disc_rpm:` treats `0` as falsy. When an endpoint has a genuine 0 RPM limit (e.g., rate limited to zero), the table prints "—" instead of "0". Always use:

```python
if disc_rpm is not None:
    # display the value, even if 0
```

### 4. Session Leaks in Hammer Threads

Each thread that creates a `requests.Session()` must close it in a `finally` block:

```python
def hammer_thread(...):
    local_session = requests.Session()
    try:
        # ... hammer logic ...
    finally:
        local_session.close()
```

Without this, long-running hammer phases leak file descriptors and connections.

### 5. Busy-Spin on Persistent Errors

`except Exception: pass` with no sleep causes threads to spin at 100% CPU on persistent errors (DNS failure, SSL error, connection refused). Always add a sleep:

```python
except Exception:
    time.sleep(0.05)
```

### 6. Login Status Code: 201, Not 200

Smarkets returns HTTP 201 (Created) for successful session creation, not 200 OK. Scripts that check `if r.status_code == 200` will silently fail to extract the token and skip all authenticated endpoints.

**Fix:**
```python
if r.status_code in (200, 201):
    data = r.json()
    self.token = data.get("token")
```

### 7. Token Field Name: `token`, Not `session_token`

The login response body contains `"token"`, not `"session_token"`. This caused a silent failure — the script accepted the 201 status (after fix #6) but then failed to find `session_token` in the JSON, falling through to "no token in response."

The actual response shape:
```json
{"token": "BQQBAA...", "refresh_token": "BgIBAA...", "factor": "complete", "stop": "2026-07-16T14:40:02", "verify": false}
```

**Fix:** Use `data.get("token")`, not `data.get("session_token")`.

### 8. Login Rate Limit Burns During Debugging

The 5/300s rate limit on `POST /v3/sessions/` fires per-account, including failed attempts. Running the script 5-6 times during debugging (fixing bugs, re-testing) will trigger 429 on the login endpoint itself, blocking all further testing for ~5 minutes. Build and test the login function separately from the main script, and cache the session token for reuse across phases to avoid repeated logins.

## Security Hardening

- **`allow_redirects=False`** on ALL `requests` calls — prevents silent redirect following that could leak session tokens to unexpected hosts.
- **No credentials in error output** — remove `r.text` from error prints in auth paths; response bodies can contain sensitive data.
- **Env var fallbacks for passwords** — `--password` CLI flag is visible in `ps aux`. Support `SMARKETS_PASSWORD` / `SMARKETS_EMAIL` environment variables as alternatives.
- **Input validation** — reject `--threads < 1`, warn when `--threads > 50` (diminishing returns + connection exhaustion risk).

## Negative Wait Time Clamping

`X-RateLimit-Reset` can return negative values if the window already expired between the response being sent and your code reading it. Always clamp:

```python
wait_time = max(int(rate_headers_last["reset"]) + 3, 5)
```

## Daemon Threads

Hammer threads should be `daemon=True` so Ctrl+C kills the script immediately. Non-daemon threads cause the script to hang waiting for them to finish, even after the main thread has exited.

## What NOT to Test

The discovery script is designed to be safe:
- Does NOT place real orders (uses fake order UUIDs for DELETE tests)
- Does NOT cancel real orders
- Does NOT logout until the very end (preserves session for all phases)
- Phase 2 only hammers "safe" endpoints (GET endpoints, not POST/DELETE on orders)
