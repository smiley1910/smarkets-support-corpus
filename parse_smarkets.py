#!/usr/bin/env python3
"""Parse the Smarkets OpenAPI spec for endpoint details."""
import json
from pathlib import Path

spec_path = Path.home() / "smarkets-api-support" / "openapi" / "smarkets_openapi.json"
with open(spec_path) as f:
    d = json.load(f)

print("=" * 80)
print("POST /v3/sessions/ (create_session) - LOGIN")
print("=" * 80)
ep = d['paths']['/v3/sessions/']['post']
print("Description:", ep['description'])
rb = ep['requestBody']['content']['application/json']['schema']
print("\nRequest body title:", rb.get('title'))
print("Required fields:", rb.get('required'))
print("Properties:")
for k, v in rb.get('properties', {}).items():
    print(f"  {k}: type={v.get('type')}, format={v.get('format','')}, desc={v.get('description','')[:120]}, example={v.get('example','')}")

resp = ep['responses']['201']['content']['application/json']['schema']
print("\n201 Response oneOf:")
for s in resp.get('oneOf', []):
    print(f"  title={s.get('title')}, required={s.get('required')}")
    for k, v in s.get('properties', {}).items():
        print(f"    {k}: desc={v.get('description','')[:120]}")

print("\n" + "=" * 80)
print("DELETE /v3/sessions/ (delete_current_session) - LOGOUT")
print("=" * 80)
ep = d['paths']['/v3/sessions/']['delete']
print("Description:", ep['description'])

print("\n" + "=" * 80)
print("DELETE /v3/orders/ (cancel_orders) - CANCEL ALL")
print("=" * 80)
ep = d['paths']['/v3/orders/']['delete']
print("Description:", ep.get('description', 'N/A'))

print("\n" + "=" * 80)
print("DELETE /v3/orders/{order_id}/ (cancel_order) - CANCEL INDIVIDUAL")
print("=" * 80)
ep = d['paths']['/v3/orders/{order_id}/']['delete']
print("Description:", ep.get('description', 'N/A'))

print("\n" + "=" * 80)
print("GET /v3/markets/{market_ids}/quotes/ (get_quotes)")
print("=" * 80)
ep = d['paths']['/v3/markets/{market_ids}/quotes/']['get']
print("Description:", ep.get('description', 'N/A')[:500])
print("Parameters:")
for p in ep.get('parameters', []):
    print(f"  name={p['name']}, in={p['in']}, required={p.get('required',False)}")

print("\n" + "=" * 80)
print("POST /v3/orders/ (create_order) - PLACE ORDER")
print("=" * 80)
ep = d['paths']['/v3/orders/']['post']
print("Description:", ep.get('description', 'N/A')[:1500])
rb = ep['requestBody']['content']['application/json']['schema']
print("\nRequest body title:", rb.get('title'))
print("Required:", rb.get('required'))
print("Properties:")
for k, v in rb.get('properties', {}).items():
    desc = v.get('description', '')
    if len(desc) > 200:
        desc = desc[:200] + '...'
    print(f"  {k}: type={v.get('type','')}, enum={v.get('enum','')}, default={v.get('default','')}, desc={desc}")
