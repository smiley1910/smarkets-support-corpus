# Customer FAQ — Comprehensive Coverage Checklist

Derived from v3 feedback (June 2026) identifying gaps in the Smarkets API FAQ.
Use this as a checklist when writing, auditing, or expanding customer-facing API documentation.
Every area below should have explicit coverage — "partial" is not sufficient for a production FAQ.

---

## 1. API Terms & Conditions Reference

- [ ] Direct link to the full API T&Cs
- [ ] Statement that all API use is governed by the T&Cs
- [ ] Summary of key obligations (not just a link — customers won't read the whole thing)

## 2. Permitted vs Prohibited Uses

- [ ] Clear list of what the API IS for (viewing prices, placing bets, account management, automation)
- [ ] Clear list of what is explicitly prohibited, each with T&C section reference:
  - Odds scraping (Section 2)
  - Concealing API calls (Section 2)
  - Browser impersonation / reverse engineering (Section 2)
  - Data resale / redistribution (Section 5)
  - Benchmarking (Section 5)
  - Data harvesting without trading (Section 6.1)
  - Fee avoidance / multiple accounts (Section 7)
  - Unfair trading strategies — latency arb, court-siding (Section 7)

## 3. Monitoring, Enforcement & Sanctions

- [ ] Statement that Smarkets actively monitors API usage
- [ ] What is monitored (request patterns, data-to-trade ratios, trading behaviour)
- [ ] Escalation path: warning → temporary suspension → permanent removal
- [ ] Note that serious violations may skip steps (immediate removal)
- [ ] Smarkets' right to cancel bets, void transactions, pursue legal action

## 4. Responsible Gambling & Account Restrictions

- [ ] Explicit statement that ALL RG controls apply equally to API users
- [ ] Deposit limits (daily/weekly/monthly, net/gross, cooling-off periods)
- [ ] Self-exclusion and timeouts (durations, account closure, balance return)
- [ ] RG acknowledgement (RG_ACK_REQUIRED)
- [ ] Affordability checks may apply
- [ ] Accounts may be restricted/suspended for RG reasons at any time

## 5. Eligibility & Jurisdiction

- [ ] Who can apply (fully verified account, supported jurisdiction)
- [ ] Who cannot (self-excluded, on timeout, employees/contractors)
- [ ] Smarkets' discretion to refuse/revoke access (Section 1)
- [ ] Jurisdictional restrictions may apply

## 6. Data Usage & Sharing

- [ ] Prohibition on sharing, selling, distributing platform data (Section 5)
- [ ] Includes both automated and manual sharing
- [ ] Written approval required for any third-party data sharing
- [ ] Examples of what constitutes "platform data" (prices, market status, events, business info)

## 7. Incident Handling & Service Availability

- [ ] No guaranteed uptime — planned maintenance, outages possible
- [ ] API may be unavailable during market suspensions, event disruptions, upgrades
- [ ] How to report confirmed outages (api@smarkets.com with timestamps, endpoints, error codes)
- [ ] Smarkets' right to change, suspend, or withdraw API services at any time

## 8. Commercial Terms & Fees

- [ ] Setup fee (£150, deducted from balance on approval)
- [ ] Commission tiers (Standard 2%, Pro 1%, Select 3%)
- [ ] Additional fees may apply for certain use cases (Section 5)
- [ ] Smarkets reserves right to change commercial terms with notice
- [ ] Continued use after changes = acceptance

## 9. Termination & Changes

- [ ] Smarkets can terminate or change API access at any time
- [ ] Grounds for termination (T&C violation, RG, regulatory, account closure, inactivity)
- [ ] What happens to open orders on termination (typically cancelled)
- [ ] Balance return process
- [ ] Continued use constitutes acceptance of updated terms

## 10. Security & Credential Use

- [ ] User is solely responsible for keeping credentials secure
- [ ] Do not share login credentials, embed in client-side code, or commit to repos
- [ ] Account sharing is prohibited — each user must have their own account
- [ ] Compromise response steps (change password, logout all sessions, contact support)
- [ ] Smarkets not liable for losses from compromised credentials

---

## Audit Methodology

When fact-checking API documentation:

1. **Read the source docs** — OpenAPI spec, T&Cs, Commission FAQ, Betting Rules, Help Centre articles
2. **Run spec verification scripts** — Python scripts against the OpenAPI JSON to verify:
   - Endpoint counts, paths, operations
   - Required vs optional fields
   - Security/auth requirements per endpoint
   - Rate limits from descriptions
   - 429 response schemas (RateLimitError vs inline)
   - Presence/absence of features (WebSocket, paper, sandbox, IP whitelisting)
3. **Cross-reference every claim** against primary sources
4. **Categorize findings**: CRITICAL (contradicts spec), HIGH (unverified as fact), MEDIUM (gaps/imprecisions)
5. **Track previous findings** — which are now fixed, which recur
6. **Include verification commands** so findings can be re-checked against the live spec
7. **Document "Claims NOT Verified"** — list removed claims so they don't get re-introduced
