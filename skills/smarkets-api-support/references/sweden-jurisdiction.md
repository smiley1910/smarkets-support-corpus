# Sweden — Jurisdiction Guide

## Summary

Sweden is a **supported jurisdiction** for regular (non-API) accounts. Smarkets holds a wagering licence from Spelinspektionen (the Swedish Gaming Authority), issued under Sweden's regulated market which opened in January 2019.

**API access in Sweden is being DISCONTINUED** (July 2026). See "API Discontinuation" section below.

## API Discontinuation (July 2026)

### Decision
Smarkets is removing API access for all Sweden-based customers due to SGA (Spelinspektionen) regulatory requirements. The underlying technical blocker is RG_ACK_REQUIRED — the per-session responsible gambling acknowledgement cannot be resolved for Swedish API users (see `references/rg-ack-swedish-api-users.md` for internal mechanics). The issue is confirmed unfixable, so a clean jurisdictional exit was chosen over continued troubleshooting.

### Diplomatic Closure Approach
- Frame as a regulatory exit, NOT a technical failure
- Do NOT mention RG_ACK_REQUIRED or any technical details in customer communications
- Offer full £150 setup fee refund to ALL affected users regardless of the 60-day window (diplomatic goodwill, not contractual obligation)
- Note: T&Cs allow Smarkets to withdraw API access at any time without notice, but giving notice is the diplomatic choice
- Closed-loop payments: withdrawals go back to original deposit method
- Unsettled bets remain active and settle normally — customers can monitor via the website

### Closure Email Pattern
The email should: announce the decision, cite regulatory developments (not technical issues), state the effective date, confirm the £150 refund, explain that the account itself remains active for withdrawals and website betting, and provide a contact for questions. See the session transcript for the full draft used in July 2026.

### What NOT to say
- Do NOT mention RG_ACK_REQUIRED or the responsible gambling acknowledgement issue
- Do NOT frame this as a temporary suspension or "under review"
- Do NOT suggest workarounds (session token reuse, etc.) — the issue is unfixable
- Do NOT mention the internal compliance uncertainty

## Evidence

| Source | Finding |
|--------|---------|
| Spelinspektionen licence | Smarkets holds a Swedish wagering licence, enabling legal operation via smarkets.com |
| Swedish Help Centre | Dedicated `/hc/sv` and `/hc/en-se` sections exist, including a Swedish-language API page at `/hc/sv/articles/212727225-API` |
| Supported currencies | SEK (Swedish Krona) is a listed supported currency in the API reference |
| iGB article | Smarkets secured a Swedish betting licence (confirmed by iGB and multiple industry sources) |

## What the Customer May Say

- *"I am resident in Sweden. Can I legally open and operate an account?"*
  - **Answer:** Yes. Smarkets holds a Swedish wagering licence from Spelinspektionen. Swedish residents can legally open and trade on the exchange.

- *"Do you allow API access for Swedish residents?"*
  - **Answer (PRE-JULY 2026):** Yes, the standard API application process applied.
  - **Answer (JULY 2026 ONWARD):** No. API access is being discontinued in Sweden due to SGA regulatory requirements. Existing API users are being notified and offered a full refund of the £150 setup fee. See "API Discontinuation" section above.

- *"Does your API allow automated order placement, cancellation and market-data retrieval?"*
  - **Answer:** Yes. The v3 REST API supports all three:
    - Order placement (limit and market orders)
    - Order cancellation
    - Full market data (quotes, last executed prices, event states, etc.)

- *"I'm getting COUNTRY_BLOCKED from Sweden"*
  - **Answer:** This shouldn't happen if they're actually in Sweden. Possible causes:
    - VPN/proxy: the IP geolocation doesn't match their registered jurisdiction
    - Account registration under a different jurisdiction (e.g. opened before the Swedish licence existed)
    - IP address from a restricted country (shared/VPN exit node)
  - Resolution: contact support@smarkets.com to reconcile the account jurisdiction

## Response Template

> **STALE ANSWER CORRECTED 2026-10-09.** The template below was written before July 2026 and
> previously told customers that API access is available in Sweden, which is no longer true.
> For any Swedish API enquiry from July 2026 onward, question 2 is answered "No" and the API
> Discontinuation closure pattern above applies. Do not send the old question 2 answer, and do
> not offer next steps to apply for API access. The template is kept only for the parts that
> remain true: the licence, SEK, and what the API does for accounts that still have access.

```
Thanks for reaching out.

Answers to your questions:

1. Can you open an account from Sweden?
Yes. Smarkets holds a Swedish wagering licence from Spelinspektionen (the Swedish Gaming
Authority), so Swedish residents can legally register and trade on the exchange. SEK is also
a supported currency.

2. Is API access available for Swedish residents?
No. API access is being discontinued for Sweden-based customers. Existing API users are being
notified and offered a full refund of the GBP150 setup fee. The account itself is not affected:
you keep access to the website for betting and for withdrawals, and any open positions settle
as normal.

3. Does the API support automated trading?
For accounts that still have API access, the v3 REST API supports order placement (limit and
market orders), order cancellation, and market data retrieval.
```


## Pitfalls

- **Don't confuse Swedish licence with UK/Malta/Ireland licences** — Smarkets holds multiple licences; Sweden is one of them, covered by Spelinspektionen
- **The Swedish market is regulated** — there may be Sweden-specific rules (deposit limits, self-exclusion via Spelpaus) that don't apply to other jurisdictions
- **Some Arbusers forums report historical signup issues from Sweden** — these predate the Swedish licence. Since the licence was secured, Swedish users should have a standard experience. If they report issues, suggest they check Spelpaus registration
- **The Swedish Help Centre exists** — `help.smarkets.com/hc/sv` — point to it if the customer prefers Swedish-language support
