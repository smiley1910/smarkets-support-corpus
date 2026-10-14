# Running Oh-My-Pi (OMP) as an Airgapped Ticket Harness

This repository is self-contained for drafting and verifying Smarkets and SBK customer support tickets using `oh-my-pi` (`omp`).

## Why OMP?

1. **Light & Fast:** Boots instantly with < 1,500 prompt tokens instead of Hermes's 15,000+ base system prompt overhead.
2. **Airgapped:** Keeps customer tickets, bet IDs, and settlement disputes strictly segregated from personal agent data and personal memory stores.
3. **Low Latency:** Sub-second TTFT using your preferred fast model.

## Quick Start

### 1. Install OMP (if not already installed)
```bash
bun install -g @oh-my-pi/pi-coding-agent
```

### 2. Launch OMP in this Repository
```bash
cd ~/smarkets-api-support
omp --system "$(cat omp/system_prompt.md)"
```

Or run with a specific model from your provider:
```bash
omp --model deepseek/deepseek-v4-flash --system "$(cat omp/system_prompt.md)"
```

### 3. Workflow Inside OMP

1. Paste the customer's inquiry or formal complaint.
2. Look up relevant rules in `betting-rules/` or `help-pages/` using fast terminal grep/cat.
3. Draft the response following Voice Core guidelines.
4. Save drafts to `responses/YYYY-MM-DD-<topic>-DRAFT.txt`.
5. Run the deterministic linter:
   ```bash
   python3 scripts/ticket_lint.py responses/YYYY-MM-DD-<topic>-DRAFT.txt
   ```
6. If the linter reports PASS, the draft is ready to send.
