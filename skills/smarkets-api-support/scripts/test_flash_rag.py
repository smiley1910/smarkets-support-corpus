#!/usr/bin/env python3
"""Test umans-flash (Qwen3.6-35B-A3B-FP8) with full RAG context.

5 nuance tests covering: auth format, auth-required endpoints, reduction factor
calculation, order type on suspension, and escalation boundary.

Usage:
    python3 ~/.hermes/skills/process/smarkets-api-support/scripts/test_flash_rag.py

Requirements:
    - UMANS_API_KEY in ~/.hermes/.env (may have single quotes — stripped automatically)
    - ~/smarkets-api-support/rag-context/api-support.md and betting-rules.md must exist

June 2026: All 5 tests passed with pre-built RAG context chunks.
"""
import json, os, urllib.request

# Get API key (strip single quotes from .env)
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if line.startswith("UMANS_API_KEY"):
            api_key = line.split("=", 1)[1].strip().strip("'\"")
            break

# Read RAG context chunks
rag_path = os.path.expanduser("~/smarkets-api-support/rag-context")
with open(os.path.join(rag_path, "api-support.md")) as f:
    api_rag = f.read()
with open(os.path.join(rag_path, "betting-rules.md")) as f:
    rules_rag = f.read()

SYSTEM_PROMPT = """You are a Smarkets/SBK API support assistant. Use ONLY the provided context to answer.
If the answer is not in the context, say 'I don't have this information — please contact api@smarkets.com for technical queries or support@smarkets.com for general queries.'
Never invent endpoints, error codes, or auth formats.
The auth header format is 'Authorization: Session-Token <token>' — NOT Bearer."""

TESTS = [
    {
        "name": "TEST 1: 401 Auth Query (should say Session-Token, not Bearer)",
        "context": api_rag,
        "query": "I keep getting a 401 error when calling the Smarkets API. I am using 'Authorization: Bearer <token>' in my header. What am I doing wrong?"
    },
    {
        "name": "TEST 2: Volumes Endpoint Auth (should say auth REQUIRED, not public)",
        "context": api_rag,
        "query": "I'm trying to get market volumes without logging in. The volumes endpoint should be public since it's under markets, right? But I get a 401."
    },
    {
        "name": "TEST 3: Betting Rules - Non-Runner Reduction Factor",
        "context": rules_rag,
        "query": "My horse racing bet at odds of 4.0 was adjusted to 3.0 after a non-runner. Why was my bet changed and how is this calculated?"
    },
    {
        "name": "TEST 4: Market Suspension - Order Behaviour (should distinguish KIP vs GTH)",
        "context": api_rag,
        "query": "The market was suspended during a football match and my order was cancelled. I thought my orders stayed in the book during suspensions? I was using the default order type."
    },
    {
        "name": "TEST 5: Escalation Test - Should say 'I don't have this information'",
        "context": api_rag,
        "query": "Can you tell me what the specific rate limit is for the events endpoint? How many requests per minute am I allowed?"
    },
]

def call_flash(system_prompt, context, query):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context + "\n\n\nCUSTOMER QUERY: " + query}
    ]

    payload = json.dumps({
        "model": "umans-flash",
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.1
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.code.umans.ai/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )

    try:
        resp = urllib.request.urlopen(req, timeout=120)
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR: {e}"

for test in TESTS:
    print(f"\n{'='*60}")
    print(f"{test['name']}")
    print(f"{'='*60}")
    response = call_flash(SYSTEM_PROMPT, test["context"], test["query"])
    print(response)
    print(f"\n--- Response length: {len(response)} chars ---")
