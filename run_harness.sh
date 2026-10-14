#!/usr/bin/env bash
# Quick launcher for Smarkets / SBK ticket harnesses via Oh-My-Pi (OMP)
set -e

MODE="${1:-}"

case "$MODE" in
  standard)
    echo "Launching Standard Ticket Writer (SBK & Exchange)..."
    exec omp --system "$(cat harness/ticket-writer-standard/SYSTEM_PROMPT.md)"
    ;;
  api)
    echo "Launching API Ticket Helper..."
    exec omp --system "$(cat harness/api-ticket-helper/SYSTEM_PROMPT.md)"
    ;;
  complaints)
    echo "Launching Complaints Writer (STAR & ADR)..."
    exec omp --system "$(cat harness/complaints-writer/SYSTEM_PROMPT.md)"
    ;;
  *)
    echo "Usage: ./run_harness.sh [standard | api | complaints]"
    echo ""
    echo "Modes:"
    echo "  standard   - Standard Ticket Writer: SBK product, promos, closed loop, SoW, bet cancels"
    echo "  api        - API Ticket Helper: Sessions auth, rate limits, 401/403/429 triage, order execution"
    echo "  complaints - Complaints Writer: Formal complaints, resettlement, void/unvoid, 90-min, golf 9.6.1, IBAS"
    exit 1
    ;;
esac
