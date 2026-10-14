# Running Oh-My-Pi (OMP) as an Airgapped Ticket Harness

This repository is self-contained for drafting and verifying Smarkets and SBK customer support tickets using `oh-my-pi` (`omp`).

## Why OMP?

1. **Light & Fast:** Boots instantly with < 1,500 prompt tokens instead of Hermes's 15,000+ base system prompt overhead.
2. **Airgapped:** Keeps customer tickets, bet IDs, and settlement disputes strictly segregated from personal agent data and personal memory stores.
3. **Low Latency:** Sub-second TTFT using your preferred fast model.

## Three Dedicated Operational Modes

The harness provides three distinct modes configured for specific ticket classes:

1. **Standard Ticket Writer (`harness/ticket-writer-standard/`):**
   - SBK product questions, SBK vs exchange separation, promo eligibility (exchange exclusion).
   - Closed-loop withdrawals (T&Cs 5.11), net deposit balancing.
   - Verification / Source of Funds (Clause 2.17 vs 2.18, no SLA).
   - Bet cancellation and Clearly Erroneous Bets policy (±15% odds deviation).

2. **API Ticket Helper (`harness/api-ticket-helper/`):**
   - Developer & API technical support.
   - Diagnostic triage: 401 (token TTL & cookie rotation), 403 (Cloudflare edge vs JSON API block), 429 (rate limit discovery).
   - Rate limits: global 1200/60s, quotes 50/60s, login 5/300s.
   - 5-question scope confirmation, REST-only streaming status, £150 setup fee (Section 3 60-day refund).

3. **Complaints Writer (`harness/complaints-writer/`):**
   - Formal complaints, settlement disputes, void/reinstatement (Rules 4.6, 4.7, 5.2, 9.4).
   - Resettlement & cancelled withdrawals (FPTP vs weighed in Rule 13.1.1).
   - Match market 90-min vs To Advance (Rule 12.1 vs 12.5.20).
   - Golf Bet Builder dead heat (Rule 9.6.1).
   - Horse racing reduction factor (Rule 13.3.2 / 13.3.5) and 1.00 floor.
   - Mandatory STAR order, single closing decision sentence, and ADR gate (IBAS / eCOGRA).

## Quick Start

### Option A: Using the Launcher
```bash
cd ~/smarkets-api-support
./run_harness.sh standard     # Standard ticket writer
./run_harness.sh api          # API technical ticket helper
./run_harness.sh complaints   # Formal complaints writer
```

### Option B: Running OMP Directly
```bash
# Standard
omp --system "$(cat harness/ticket-writer-standard/SYSTEM_PROMPT.md)"

# API Helper
omp --system "$(cat harness/api-ticket-helper/SYSTEM_PROMPT.md)"

# Complaints
omp --system "$(cat harness/complaints-writer/SYSTEM_PROMPT.md)"
```

## Post-Draft Validation

Always run the fast deterministic validator before sending:
```bash
python3 scripts/ticket_lint.py responses/YYYY-MM-DD-<topic>-DRAFT.txt
```
The linter verifies straight quotes, zero em dashes, zero hyphenated compound modifiers, negative density <= 3, single decision sentence, and verbatim ADR formatting.
