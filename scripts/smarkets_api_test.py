#!/usr/bin/env python3
"""
Smarkets API Quick Test Script
Use this to quickly test API connectivity, auth, and basic endpoints.
Usage: python3 smarkets_api_test.py [--email EMAIL] [--password PASSWORD]
"""

import requests
import json
import sys
import argparse

BASE_URL = "https://api.smarkets.com"

def test_connection():
    """Test basic connectivity to the API"""
    try:
        r = requests.get(f"{BASE_URL}/v3/events/", timeout=10, allow_redirects=False)
        print(f"[OK] API reachable: {r.status_code}")
        return True
    except requests.ConnectionError:
        print("[FAIL] Cannot reach api.smarkets.com - check network/firewall")
        return False
    except Exception as e:
        print(f"[FAIL] Connection test failed: {e}")
        return False


def test_login(email, password):
    """Test authentication"""
    print(f"\n--- Testing Login ---")
    r = requests.post(
        f"{BASE_URL}/v3/sessions/",
        json={"username": email, "password": password},
        timeout=10,
        allow_redirects=False,
    )
    
    if r.status_code in (200, 201):
        try:
            data = r.json()
        except (json.JSONDecodeError, ValueError):
            print(f"[?] Login returned {r.status_code} but response is not JSON")
            print(f"    Response: {r.text[:500]}")
            return None
        token = data.get("token")
        if token:
            print(f"[OK] Login successful. Token received.")
            return token
        else:
            print(f"[?] Login returned {r.status_code} but no token in response")
            print(f"    Response: {json.dumps(data, indent=2)[:500]}")
            return None
    elif r.status_code == 400:
        print(f"[FAIL] Login failed (400): {r.text[:300]}")
        return None
    elif r.status_code == 401:
        print(f"[FAIL] Login failed (401): {r.text[:300]}")
        return None
    else:
        print(f"[FAIL] Login failed ({r.status_code}): {r.text[:300]}")
        return None


def test_auth_endpoints(token):
    """Test authenticated endpoints"""
    if not token:
        return
    
    headers = {"Authorization": f"Session-Token {token}"}
    
    print(f"\n--- Testing Authenticated Endpoints ---")
    
    # Test account
    r = requests.get(f"{BASE_URL}/v3/accounts/", headers=headers, timeout=10, allow_redirects=False)
    if r.status_code == 200:
        acct = r.json().get("account", {})
        print(f"[OK] GET /v3/accounts/")
        print(f"     Account ID: {acct.get('account_id', 'N/A')}")
        print(f"     Balance: {acct.get('balance', 'N/A')} {acct.get('currency', '')}")
        print(f"     Available: {acct.get('available_balance', 'N/A')}")
        print(f"     Exposure: {acct.get('exposure', 'N/A')}")
    else:
        print(f"[FAIL] GET /v3/accounts/: {r.status_code} - {r.text[:200]}")
    
    # Test events
    r = requests.get(f"{BASE_URL}/v3/events/", headers=headers, timeout=10, allow_redirects=False)
    if r.status_code == 200:
        events = r.json().get("events", [])
        print(f"[OK] GET /v3/events/: {len(events)} events returned")
        if events:
            print(f"     First event: {events[0].get('name', 'N/A')} (ID: {events[0].get('id', 'N/A')})")
    else:
        print(f"[FAIL] GET /v3/events/: {r.status_code} - {r.text[:200]}")
    
    # Test orders
    r = requests.get(f"{BASE_URL}/v3/orders/", headers=headers, timeout=10, allow_redirects=False)
    if r.status_code == 200:
        orders = r.json().get("orders", [])
        print(f"[OK] GET /v3/orders/: {len(orders)} orders")
    else:
        print(f"[FAIL] GET /v3/orders/: {r.status_code} - {r.text[:200]}")


def test_public_endpoints():
    """Test endpoints that might work without auth"""
    print(f"\n--- Testing Public-ish Endpoints ---")
    
    # Try events without auth (may or may not work depending on access)
    r = requests.get(f"{BASE_URL}/v3/events/", timeout=10, allow_redirects=False)
    print(f"GET /v3/events/ (no auth): {r.status_code}")
    if r.status_code == 200:
        events = r.json().get("events", [])
        print(f"  {len(events)} events (public access available)")


def main():
    parser = argparse.ArgumentParser(description="Test Smarkets API connectivity")
    parser.add_argument("--email", help="Smarkets account email")
    parser.add_argument("--password", help="Smarkets account password")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Smarkets API - Quick Test")
    print("=" * 60)
    
    if not test_connection():
        sys.exit(1)
    
    test_public_endpoints()
    
    if args.email and args.password:
        token = test_login(args.email, args.password)
        test_auth_endpoints(token)
    else:
        print("\n[S] No credentials provided. Skipping auth tests.")
        print("    Use: python3 smarkets_api_test.py --email user@example.com --password yourpass")
    
    print("\n" + "=" * 60)
    print("  Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
