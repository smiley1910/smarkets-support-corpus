# CFTC Prediction Market Regulatory Landscape — June 2026

## Key Dates

| Date | Event |
|---|---|
| March 9, 2026 | **Smarkets files for CFTC DCM license** |
| March 12, 2026 | CFTC takes two formal actions on prediction market regulation |
| June 10, 2026 | **CFTC publishes NPRM** (Notice of Proposed Rulemaking) — 267-page proposal |
| ~June 11, 2026 | **ProphetX receives CFTC DCM + Clearing Organization approval** |
| June 16, 2026 | **Novig receives CFTC DCM approval** — operates across all 50 states |
| ~July 25, 2026 | 45-day comment period closes |
| ~Late 2026/early 2027 | Final rules expected |

## The Precedent: Novig & ProphetX

Two sports prediction market exchanges were approved within one week of each other (June 11-16, 2026):

**Novig:**
- DCM license — same type Smarkets is applying for
- Peer-to-peer exchange model (identical to Smarkets)
- Operates across all 50 states under single federal framework
- ~$5B+ cumulative volume, $8B+ annualized
- Applied: January 2026 → Approved: June 16, 2026 (~5 months)
- *"Among the fastest DCM designations in CFTC history"*

**ProphetX:**
- DCM + Clearing Organization status
- Sports betting exchange model
- Applied: January 2026 → Approved: ~June 11, 2026

## What This Means for Smarkets

1. **The regulatory path is proven** — two sports exchanges with the same business model as Smarkets have been approved. The CFTC is actively approving sports prediction market DCMs.

2. **Timeline visibility** — Novig applied in January, approved in June (~5 months). Smarkets filed March 9. If same timeline, approval by ~August 2026. If slower, 2027 is realistic.

3. **All 50 states** — CFTC DCM designation preempts state-by-state sportsbook licensing. This is the federal bypass traditional sportsbooks (DraftKings, FanDuel) can't access.

4. **17 applications pending** — the pipeline is full, but the CFTC is processing them. 2 approved in one week shows momentum.

5. **Chair Selig (Trump appointee) is supportive** — *"protect the integrity of our regulated markets without standing in the way of responsible innovation."*

## Market Context

- Combined prediction market volume: **<$5B/month (Sep 2025) → ~$24B/month (Apr 2026)**
- Kalshi: $25M annualized revenue (Dec 2024) → **$2B+ (June 2026)** → $22B valuation
- World Cup 2026 (June/July) is generating massive volume
- *"Prediction market supercycle"* — industry press term
- CFTC Chair Selig views prediction markets as fundamentally different from sportsbooks

## Sources

- Axios (June 10, 2026): *"Feds move to formally allow sports trading on prediction markets"*
- CFTC Press Release 9249-26 (June 10, 2026): NPRM publication
- Yahoo Finance (June 16, 2026): *"CFTC Approves Novig DCM Application"*
- Action Network (June 16, 2026): *"Novig Wins CFTC Approval for National Sports Exchange"*
- Pew Research Center (May 27, 2026): *"Trading volume on prediction markets has soared"*

## Related: Technical Infrastructure Findings (July 2026)

Analysis of Smarkets' public frontend JavaScript revealed that the CFTC product
infrastructure is already deployed. See
`references/streaming-infrastructure-and-cftc-product.md` for:
- CFTC-specific streaming endpoints (cftc-sio-live.smarkets.com — live, accepting connections)
- US legal entities (Smarkets USA Op Co. — Colorado license #90034372 since April 2020;
  Smarkets Holdings USA Inc — Indiana Gaming Commission)
- Product branding ("Smarkets Predictions" — positioned as trading, not gambling)
- Jurisdiction system (CDG, IGC, CFTC grouped separately from EU gambling jurisdictions)
- Infrastructure status (endpoints live, routes exist but pages render 404 — late-stage dev)
