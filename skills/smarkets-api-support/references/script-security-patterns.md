# Smarkets API Script Security Patterns

Patterns verified during the July 2026 multi-pass audit of all Python scripts in `~/smarkets-api-support/scripts/`. Apply these when writing or modifying any script that interacts with the Smarkets API.

## Auth Response Field Name

The login endpoint (`POST /v3/sessions/`) returns the session token under the key `"token"`, NOT `"session_token"`.

```python
# CORRECT
token = data.get("token")

# WRONG — returns None, silently fails
token = data.get("session_token")
token = data["session_token"]  # KeyError
```

The auth header format is `Authorization: Session-Token <token>` (NOT `Bearer`). The field name in the response body is `"token"`, but the header name is `Session-Token`. This inconsistency has caused bugs.

## allow_redirects=False (Security Critical)

ALL requests to the Smarkets API must set `allow_redirects=False`. This includes:
- Login (`POST /v3/sessions/`)
- Authenticated GET requests (accounts, orders, events with auth)
- Order placement (`POST /v3/orders/`)
- Public/no-auth endpoints (events, markets, contracts, currencies)

```python
# CORRECT
r = requests.post(f"{BASE_URL}/v3/sessions/", json=body, timeout=10, allow_redirects=False)

# WRONG — default allow_redirects=True can leak session token via redirect
r = requests.post(f"{BASE_URL}/v3/sessions/", json=body, timeout=10)
```

Risk: if the API returns a 3xx redirect, `requests` follows it by default, potentially leaking the `Authorization: Session-Token` header to a different host.

## Login Status Code

Session creation returns `201 Created`, not `200 OK`. Always check for both:

```python
if r.status_code in (200, 201):
    token = r.json().get("token")
```

Checking only `200` will fail on successful logins.

## API Response Field Access

Never use direct dict key access (`["key"]`) on API response fields. Always use `.get()` with a safe default. The API may omit fields, return null values, or change schema between versions.

```python
# CORRECT
total_qty = sum(b.get("quantity", 0) for b in bids)
contract_map = {c.get("id"): c for c in contracts if c.get("id") is not None}

# WRONG — KeyError if field missing
total_qty = sum(b["quantity"] for b in bids)
contract_map = {c["id"]: c for c in contracts}
```

## Exception Handling in Hammer/Loop Patterns

When running concurrent request loops (rate limit discovery, load testing):

1. **Always track error count** — silent `except Exception: time.sleep(0.05)` makes persistent failures invisible
2. **Split ConnectionError from generic exceptions** — ConnectionError needs longer backoff (0.1s vs 0.05s)
3. **Always set `daemon=True` on worker threads** — prevents Ctrl+C hang
4. **Use `threading.Event()` for stop signaling** — not bare boolean flags
5. **Close sessions in `finally`** — `local_session.close()` must run even on exception

```python
except requests.exceptions.ConnectionError:
    with lock:
        total_errors += 1
    time.sleep(0.1)
except Exception:
    with lock:
        total_errors += 1
    time.sleep(0.05)
```

## Credential Handling

Prefer environment variables (`SMARKETS_EMAIL`, `SMARKETS_PASSWORD`) over CLI args. CLI args are visible in `ps` output and shell history.

```python
email = os.environ.get("SMARKETS_EMAIL")
password = os.environ.get("SMARKETS_PASSWORD")
```

If CLI args are needed for testing, add a warning in the help text recommending env vars for production use.

## JSON Decode Safety

Always wrap `r.json()` in try/except. The API may return HTML error pages, empty bodies, or non-JSON responses during maintenance windows or server errors.

```python
try:
    data = r.json()
except (json.JSONDecodeError, ValueError):
    print(f"Response is not JSON: {r.text[:500]}")
    return None
```

## Scripts Audited (July 2026)

| Script | Issues Found | Status |
|--------|-------------|--------|
| `smarkets_api_test.py` | Wrong token key, missing 201 check, missing allow_redirects=False on all requests, no JSON decode handling | Fixed |
| `back_favourite.py` | Bare `except:` clause | Fixed |
| `noauth_live_football.py` | KeyError on dict access (contracts, bids, offers) | Fixed |
| `rate_limit_discovery.py` | Phase 3 silently swallowed all exceptions without tracking | Fixed |
| `test_flash_rag.py` | api_key undefined if .env missing, FileNotFoundError crash | Fixed |
| `parse_smarkets.py` | Hardcoded absolute path, file handle leak | Fixed |
| `verify_live_spec.py` | No network error handling on fetch_live() | Fixed |
| `scrape_help_pages.py` | fetch_url swallowed exceptions without logging | Fixed |
