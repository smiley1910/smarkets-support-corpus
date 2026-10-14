# Competitor API Documentation Analysis

*Research conducted June 2026. Findings compiled from public documentation of Betfair, Betdaq, and Matchbook.*

## Purpose

This file documents how competitor betting exchanges structure their API docs, FAQs, and support materials. Use it when auditing or improving Smarkets' own documentation to identify gaps and best practices.

## Betfair (developer.betfair.com)

Most mature betting exchange API documentation in the industry.

### Documentation Structure
- Getting Started / Overview (what is the API, how to register)
- Authentication (interactive login, non-interactive/certificate-based for bots, keep-alive, session management)
- Exchange API (market data operations, betting operations, market navigation)
- Accounts API (funds, details, statements, currency rates, wallet transfers)
- Streaming API (push-based market/order streaming, image vs delta, resubscription)
- Data Types / Reference (complete data model, enums, price projections)
- Error Handling (error code tables with sub-error codes for granular diagnostics)
- Rate Limits (weighted operation model with examples)
- Developer Tools (API-NG Visualiser — interactive in-browser API tester, Data Extractor for bulk/historical data)
- SDKs (Java, C#, Python, PHP, VBA) with sample code repos on GitHub

### Error Handling
- Error Code (string) + Error Message (human-readable) + Sub-ErrorCode (granularity)
- Multiple errors per response (JSON arrays)
- Well-documented per operation

### Rate Limiting
- **Weighted request model** — each operation has a weight (1-20+)
- Separate buckets: Data Requests (weighted/min), Account Requests (count/min), Transaction Requests (count/hr), Order Placement (count/min)
- Dedicated documentation page explaining how weightings work with examples
- Free vs paid API keys have different limits

### Community
- Dedicated developer forum (forums.developer.betfair.com)
- Betfair Community (community.betfair.com)
- GitHub sample repos
- Stack Overflow tagged `betfair` and `betfair-api`

### Standout Practices Worth Emulating
1. Weighted rate-limit model — transparent, documented with examples
2. Interactive API Visualiser — test calls in-browser without writing code
3. Sub-error codes — granular diagnostics beyond top-level codes
4. Certificate-based non-interactive login for bots — well-documented
5. Dedicated developer forum — community Q&A for API developers
6. Streaming API — push-based reduces polling and rate limit pressure
7. Data Extractor — bulk historical data access
8. Multiple SDKs with sample code repositories

## Betdaq

Less extensively documented than Betfair. Historically SOAP/WSDL-based API.

### Documentation Structure
- API Overview, authentication (credentials-based), read-only operations, write operations
- Data model (types and enums)
- Error handling (SOAP fault codes)
- Rate limiting — less formally documented than Betfair

### Customer FAQ Structure
- Account & Registration
- Deposits & Withdrawals
- Exchange Betting Basics (back/lay, commission, settlement, suspension)
- Technical troubleshooting
- Responsible Gambling

### Standout Practice
- Simpler commission model (flat rate) — easier to explain than Betfair's Premium Charge
- Straightforward FAQ format — less overwhelming than Betfair's extensive docs

## Matchbook

Modern REST/JSON API.

### Documentation Structure
- API Overview (base URLs, auth model)
- Authentication (session-based)
- Sports Data (list sports, events, markets, prices/runners)
- Betting/Offers (place, cancel, update, list current offers, matched bets)
- Account Management (balance, statement, fund transfers)
- Error Handling (HTTP status codes + JSON error body)
- Rate Limiting (per-endpoint, HTTP 429, rate-limit headers)

### Error Handling
- HTTP status code gives category, JSON body gives specifics
- Clean modern REST pattern
- Error format: `{"errors": [{"code": "ERROR_CODE", "message": "..."}]}`

### Standout Practices
1. Clean REST/JSON design — modern, intuitive for developers familiar with REST
2. HTTP status code + JSON error body — follows web standards
3. Rate limit headers (X-RateLimit-Remaining) — developer-friendly
4. Sandbox/test environment — allows safe testing

## Comparative Analysis

| Aspect | Betfair | Betdaq | Matchbook | Smarkets |
|--------|---------|--------|-----------|----------|
| API Type | REST + Streaming | SOAP/WSDL | REST/JSON | REST/JSON |
| Maturity | Very high | Medium | Medium-high | Low |
| Auth | Cert + session | SOAP credentials | Session token | Session-Token header |
| SDKs | Java, C#, Python, PHP, VBA | Limited | Community | None |
| Interactive tester | Yes (Visualiser) | No | Unknown | No |
| Streaming API | Yes | No | Limited | Yes (undocumented) |
| Error detail | Sub-error codes | Basic (SOAP faults) | HTTP + JSON | HTTP + JSON |
| Rate limit docs | Excellent (weighted) | Minimal | Moderate | Per-endpoint (some documented) |
| Community forum | Yes | Minimal | Minimal | None |
| Getting started guide | Yes | Minimal | Yes | No |
| Example requests | Yes | No | Unknown | No |

## Common FAQ Topics All Three Cover (that Smarkets should match)
1. Exchange concept explanation — What is an exchange? Back vs Lay?
2. Commission — How is it calculated? What rate?
3. Account verification — KYC requirements, document uploads
4. Deposits & withdrawals — Methods, timelines, fees
5. Market settlement — How are results determined? Void rules?
6. Market suspension — What happens when markets are paused?
7. Cash Out — How does early settlement work?
8. In-play betting — How does live betting work?
9. Responsible gambling — Limits, self-exclusion, support links
10. Technical troubleshooting — Login issues, browser support

## Gaps in Smarkets Documentation (Red-Team Findings)

The official docs at docs.smarkets.com are bare — just an auto-generated Swagger UI. Key gaps:

1. No getting started guide
2. No authentication walkthrough
3. No example requests/responses
4. No rate limiting documentation in the Swagger
5. No error handling guide
6. No SDKs or client libraries
7. No API visualiser
8. No developer forum/community
9. No streaming API documentation
10. help.smarkets.com articles are Cloudflare-protected (hard to reference)
11. No separate developer portal
12. No changelog or versioning
13. No status page

The customer-facing FAQ (`training/customer_faq.md`) and CS agent KB (`training/confluence_draft_v2.md`) address many of these gaps from a self-service perspective.

## Methodology Note

The competitor research was conducted using a subagent (delegate_task) running parallel to the main audit work. The subagent attempted live browsing but the browser service was unavailable, so findings were compiled from training data knowledge. Specific FAQ question titles, error code strings, and rate limit numbers should be verified against live sites before being used as authoritative references.
