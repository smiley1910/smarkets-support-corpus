# Q1 (Permitted Use) & Q4 (Charges) — Evidence Brief

**Subject:** HedgeDesk pre-sales API enquiry — private single-user Python app, personal pre-match hedging + user-confirmed lay bets on own Smarkets account. No redistribution, no third-party accounts.
**Compiled:** 2026-09-23
**Scope:** Q1 and Q4 only. Multiples/builder markets, technical limits and order mechanics excluded (other workers).
**Canonical source:** `~/.hermes/skills/process/smarkets-api-support/references/api-tcs-full-text.md` (mirror of help.smarkets.com article 34697834941085; help-centre capture of same article is a Cloudflare 403 stub at `~/smarkets-api-support/help-pages/smarkets/en-gb/34697834941085_Smarkets_API_Access_Integration_T_Cs.md`). Second capture of the same T&Cs text at `~/smarkets-api-support/scrape-aug18/help/api-tcs.md` — wording identical on all quoted lines.

---

## Q1_FINDINGS

Format: `{claim, verdict, verbatim_quote (≤30 words), source_path + section}`

**1. Automated interaction (program placing/cancelling orders) is permitted only after application + approval.**
- Verdict: **ALLOWED (conditional on approval)**
- Quote: "Access to the API - and any automated interactions with our platform or services - is permitted only after you have completed our API Request Form" (Section 1)
- Source: `~/.hermes/skills/process/smarkets-api-support/references/api-tcs-full-text.md` §1 API Usage (line 33)

**2. Core permitted scope is viewing market prices and placing bets on the account holder's own account.**
- Verdict: **ALLOWED** (own account only)
- Quote: "The API is designed to allow authorised users to view market prices and place bets on their Smarkets account. All other uses are strictly prohibited" (Section 2)
- Source: `api-tcs-full-text.md` §2 Authorisation (line 39)

**3. Hedging an existing position for risk management is treated as a legitimate trading activity, not "unfair trading".**
- Verdict: **ALLOWED**
- Quote: "The API T&Cs (Section 1) explicitly authorise automated trading, and hedging an existing position for risk management is a legitimate trading activity."
- Source: `~/smarkets-api-support/responses/api-scope-confirmation.txt` Q3 (line 15); rule basis `api-tcs-full-text.md` §7 (line 98)
- Note: this is a prior internal position on an approved customer's hedging setup, not canonical T&Cs wording. Pre-match hedging does not exploit delays, which is the §7 test.

**4. Using the API or its data to benchmark markets, prices, liquidity or systems is not permitted.**
- Verdict: **PROHIBITED**
- Quote: "Additionally, usage of the API or its data to benchmark markets, prices, liquidity or systems is not permitted." (Section 5)
- Source: `api-tcs-full-text.md` §5 Restrictions (line 65); reinforced at §6.1 bullet "Monitor or benchmark our services for competitive purposes" (line 81) and `~/smarkets-api-support/training/confluence_draft_v2.md` lines 895-896, 952-953

**5. Standalone data extraction without commensurate trading volumes is prohibited.**
- Verdict: **PROHIBITED** as standalone use; **ALLOWED** where trading volumes are commensurate
- Quote: "Use the API strictly for data extraction purposes without commensurate trading volumes" (§6.1)
- Source: `api-tcs-full-text.md` §6.1 Fair Usage (line 79) and §7 Data Harvesting (line 94); internal interpretation `responses/api-scope-confirmation.txt` Q6 (line 52): "As long as you're actively trading through the API, storing data for your own reconciliation is fine."

**6. Sharing, selling or distributing platform data to third parties requires written approval.**
- Verdict: **PROHIBITED** without written approval; HedgeDesk's single-user / no-redistribution design sits outside this clause
- Quote: "You may not share, sell or distribute platform data - such as prices, market status, events or business information - with third parties" (Section 5)
- Source: `api-tcs-full-text.md` §5 (line 63)

**7. No read-only or data-only API tier exists.**
- Verdict: **PROHIBITED** (no such product)
- Quote: "No. Smarkets does not offer a read-only or data-only API tier. The API is a single product — full access only"
- Source: `~/smarkets-api-support/training/confluence_draft_v2.md` FAQ "Can I get read-only API access?" (lines 865-866); corroborated `training/customer_faq.md` lines 63-65

**8. Public endpoints are reachable without authentication and support read-only development work.**
- Verdict: **ALLOWED**
- Quote: "For read-only development work, the public endpoints (events, markets, contracts) are available without authentication."
- Source: `responses/api-scope-confirmation.txt` Additional points (line 66); independently verified against `~/smarkets-api-support/openapi/smarkets_openapi.json` — no `security` block on `/v3/currencies/{code}/`, `/v3/events/`, `/v3/events/{event_ids}/competitors/`, `/v3/events/{event_ids}/markets/`, `/v3/events/{event_ids}/markets_count/`, `/v3/events/{event_ids}/states/`, `/v3/markets/{market_ids}/contracts/`; `api_key` required on `/v3/markets/{market_ids}/quotes/`, `/last_executed_prices/`, `/volumes/`, `/v3/accounts/*`, all `/v3/orders/*`. Cross-check: `references/customer-faq-redteam-audit-june-2026.md` lines 351-352.

**9. Odds scraping, concealing API calls, browser impersonation and reverse engineering are strictly prohibited.**
- Verdict: **PROHIBITED**
- Quote: "All other uses are strictly prohibited, including but not limited to, odds scraping, concealing API calls, browser impersonation or reverse engineering." (Section 2)
- Source: `api-tcs-full-text.md` §2 (line 39)

**10. Latency arbitrage and court-siding are prohibited as unfair trading.**
- Verdict: **PROHIBITED** for those strategies; pre-match hedging does not meet the §7 test
- Quote: "Strategies that we view as harmful to the ecosystem, such as latency arbitrage or court-siding, where delays are exploited to disadvantage other customers." (§7)
- Source: `api-tcs-full-text.md` §7 Unfair Trading (line 98)

**11. Usage is restricted to pre-approved events and markets only; the approved list is per-account and unpublished.**
- Verdict: **ALLOWED within scope / RESTRICTION**
- Quote: "Usage is restricted to pre-approved events and markets only." (Section 5)
- Source: `api-tcs-full-text.md` §5 (line 61); `training/confluence_draft_v2.md` FAQ lines 868-869

**12. Operating on third-party accounts, or holding multiple accounts to dodge commission thresholds, is prohibited.**
- Verdict: **PROHIBITED**
- Quote: "Creating or controlling multiple accounts to avoid changing commission thresholds. This is treated as attempted fraud" (§7)
- Source: `api-tcs-full-text.md` §7 Fee Avoidance (line 96); §2 scopes bets to "their Smarkets account" (line 39)

**13. Whether a human confirmation gate changes the classification of an automated order is not addressed in the T&Cs.**
- Verdict: **UNCLEAR** (silent)
- Quote: "The API is designed to allow authorised users to view market prices and place bets on their Smarkets account."
- Source: `api-tcs-full-text.md` §2 (line 39) — no clause distinguishes user-confirmed from unattended order placement; both fall under approved automated interaction (§1)

**14. All API accounts are subject to a compliance review in the first 60 days as a condition of continued trading.**
- Verdict: **ALLOWED (condition)**
- Quote: "All customers will be subject to a compliance review of their account within the first 60 days to remain eligible to continue trading." (Section 2)
- Source: `api-tcs-full-text.md` §2 (line 43); `responses/api-scope-confirmation.txt` (line 68)

**15. No sandbox/test environment exists; order-placement testing uses live funds.**
- Verdict: **ALLOWED (live funds)**
- Quote: "The API doesn't have a dedicated test or sandbox environment, so when you're ready to test order placement, you'll be using live funds."
- Source: `responses/api-scope-confirmation.txt` Additional points (line 66)

**Net Q1 position for HedgeDesk:** the described use (private single-user app, pre-match hedging, user-confirmed lay bets, own account, no redistribution) sits inside §1/§2 permitted scope and outside the §5 benchmarking, §6.1 data-extraction and §7 unfair-trading prohibitions — **subject to (a) prior approval, (b) pre-approved events/markets, (c) trading volumes commensurate with data use, and (d) no price comparison against other operators (§5 benchmarking — the one genuine overlap risk; see OPEN_QUESTIONS 1).**

---

## Q4_FINDINGS

**setup_fee:**
£150 one-time administrative/setup fee, or account currency equivalent, deducted from account balance upon successful registration (i.e. on approval, not at application).
- "A one-time administration of £150 is required for activation" — `api-tcs-full-text.md` Getting Started (line 14)
- "A one-time administrative setup fee of £150, or account currency equivalent, will be deducted from your account balance upon successful registration for API usage." — `api-tcs-full-text.md` §3 (line 47)
- "deducted from your account balance once your application is approved — not at the point of application" — `~/smarkets-api-support/training/customer_faq.md` line 32

**recurring_fees: N** — no recurring or subscription API fee is documented anywhere in the canonical API T&Cs.
- Positive statement of the fee model is limited to "one-time" in §3 (line 47) and Getting Started (line 14).
- Caveat, same section: "API usage may be subject to specific restrictions and/or incur additional fees." — `api-tcs-full-text.md` §5 (line 61). No schedule or trigger for such additional fees is published. Internal guidance flags this as a live caveat: `references/customer-faq-redteam-audit-june-2026.md` line 269 ("'No monthly subscriptions' contradicts T&Cs — FIXED, references Section 5 for additional fees"); `training/confluence_draft_v2.md` lines 958-959.
- Adjacent recurring fee, not API-specific: inactive-account administration fee of €5 (or, for UK residents, €5 or 5% of remaining balance per month, whichever is higher) after 12 months without login, charged monthly up to a 6-month maximum, refundable on request — `~/smarkets-api-support/help-pages/smarkets/en-gb/213469085_Smarkets_Terms_and_Conditions.md` §4.1-4.7 (lines 114-122).
- Do not state "no ongoing cost" to the customer without the §5 caveat attached.

**commission_tiers:** three tiers; API access confers no discount.
- Standard **2%** on net profit per market only — default, automatic, all accounts start here.
- Pro **1%** — opt-in only, via customer service, available once past 80% of either threshold: >1,500 bets placed per calendar month OR >£1M staked per calendar month. Charged per individual matched bet that settles, on profit and on loss.
- Select **3%** — auto-applied when net profit exceeds £25,000 over the previous 12 calendar months. Charged per individual matched bet that settles, on profit and on loss.
- API access does NOT give a lower commission rate; the same tiers apply to website, app and API.
- Sources: `~/smarkets-api-support/training/confluence_draft_v2.md` lines 184-199 (tier table + key facts); `~/smarkets-api-support/help-pages/smarkets/en-gb/212654665_Smarkets_commission_FAQ.md` (tier definitions, 80% opt-in threshold, Pro/Select per-bet charging, worked examples); `api-tcs-full-text.md` §3 line 49 ("All accounts will be subject to standard Customer Commission"); Customer T&Cs §3.8-3.9 at `help-pages/smarkets/en-gb/213469085_Smarkets_Terms_and_Conditions.md` lines 108-109 (commission charged at market settlement, not placement).

**refund_clause (verbatim, §3):**
"Should you choose to permanently withdraw from API usage within the first 60 days, your setup fee will be refunded."
- Source: `api-tcs-full-text.md` §3 Setup Fee and Commission (line 47)
- Supporting: after the 60-day window the fee is non-refundable; withdrawal is actioned via support@smarkets.com — `training/customer_faq.md` lines 40-42
- Independent capture of identical wording: `scrape-aug18/help/api-tcs.md` line 51

**welcome_offer_exclusion (verbatim, §3; repeated verbatim in Getting Started):**
"API customers are ineligible for any affiliate commission offers, as well as the 60 day 0% commission offer for new customers"
- Source: `api-tcs-full-text.md` §3 (line 51) and Getting Started (line 17); `scrape-aug18/help/api-tcs.md` lines 17, 55; `docs/smarkets_api_knowledge_base.md` line 47

**activation_timing: DOCUMENTED.** The 0% offer is deposit-anchored, not signup-anchored, and is independently closed to API/software users by its own terms.
- "Eligible customers will be able to enjoy trading with a commission rate of 0% on all bets that settle within 60 days from the deposit." (clause 4)
- "Once the 60 day period has elapsed the account will be set to the default commission rate." (clause 7)
- "Customers who access Smarkets through any API or trading software will be ineligible for this offer." (clause 8)
- Eligibility conditions: code **COMMFREE** entered in the promo code field during registration (clause 3); minimum first deposit of £10/€10 in a single amount by debit card or instant banking (clause 1); first deposits via Skrill, Neteller, PayPal, Revolut or virtual/prepaid cards (incl. virtual Monzo) do not qualify (clause 2); offer live from 00:00 BST 1 September 2023 (clause 8).
- Source: `~/smarkets-api-support/help-pages/smarkets/en-gb/13242929620893_Trade_with_0_at_Smarkets_for_60_days.md` clauses 1-4, 7-8 (lines 24-31)

---

## DOC_POINTERS

1. **Smarkets API Access & Integration T&Cs** — https://help.smarkets.com/hc/en-gb/articles/34697834941085-Smarkets-API-Access-Integration-T-Cs (local canonical text: `~/.hermes/skills/process/smarkets-api-support/references/api-tcs-full-text.md`; live URL returns 403 to direct fetch)
2. **Smarkets commission FAQ** (tier thresholds, opt-in, per-bet charging) — https://help.smarkets.com/hc/en-gb/articles/212654665-Smarkets-commission-FAQ (local: `~/smarkets-api-support/help-pages/smarkets/en-gb/212654665_Smarkets_commission_FAQ.md`)
3. **0% welcome offer full T&Cs** (deposit-anchored 60 days, COMMFREE code, API/software exclusion clause 8) — https://help.smarkets.com/hc/en-gb/articles/13242929620893-Trade-with-0-at-Smarkets-for-60-days (local: `~/smarkets-api-support/help-pages/smarkets/en-gb/13242929620893_Trade_with_0_at_Smarkets_for_60_days.md`)
4. **API technical documentation / OpenAPI spec** (public vs authenticated endpoints, 21 operations across 18 paths) — https://docs.smarkets.com/ (local spec: `~/smarkets-api-support/openapi/smarkets_openapi.json`; scrape: `~/smarkets-api-support/scrape-aug18/live_trading.json`)
5. **API Request Form** (application route, prerequisite to any automated interaction) — https://support.smarkets.com/p/6MLL-PL7/api-request-form

---

## OPEN_QUESTIONS (require api@smarkets.com confirmation)

1. **Benchmarking overlap (§5).** Does HedgeDesk's hedging logic compare Smarkets prices against any other operator's or bookmaker's prices to size the hedge stake? If yes, this is the exact overlap flagged and deliberately deferred in `responses/api-scope-confirmation.txt` Q8 (lines 60-62) for the cross-exchange arbitrage case — it cannot be answered definitively from the docs and needs an api@smarkets.com ruling on the customer's specific setup. If the hedge is computed solely from the customer's own position and Smarkets' own order book, the §5 benchmarking prohibition is not engaged.
2. **Pre-approved scope.** Confirm the account-specific pre-approved events and markets list for a pre-match hedging use case (§5 line 61; `training/confluence_draft_v2.md` lines 868-869). Not published externally.
3. **"Commensurate trading volumes" (§6.1 / §7).** No volume threshold is documented. What level of trading activity keeps a hedging-oriented strategy clear of the Data Harvesting ground for suspension (§7 line 94)?
4. **Additional fees (§5).** Whether "specific restrictions and/or incur additional fees" (line 61) applies to this use case, and whether a schedule or trigger exists. No published schedule found in any repo doc.
5. **Refund mechanics (§3).** What operationally constitutes "permanently withdraw from API usage", how the 60-day clock is measured (from fee deduction / approval / activation), and whether initiation must be via support@smarkets.com (per `training/customer_faq.md` line 42).
6. **Unauthenticated quotes.** `training/customer_faq.md` line 67 flags that the quotes endpoint description mentions delayed prices without a session token while the spec's security block requires authentication. Confirm whether any unauthenticated delayed-price access is supported for pre-trade development.
7. **0% offer already running.** If the customer's 60-day COMMFREE window is active or was activated before API approval, does API approval terminate the promotional rate immediately, and are bets already settled under it unaffected? §3 makes API customers ineligible and clause 8 independently excludes API/software users, but the interaction with an in-flight promotion is not documented.
8. **Compliance review behaviour.** Whether the first-60-days compliance review (§2 line 43) restricts automated order placement or hedging activity during the review period. `training/customer_faq.md` line 61 says "certain restrictions may apply depending on your account status" without specifying them.
9. **Order origin.** Whether a user-confirmation gate before order submission changes anything from Smarkets' side (§2 is silent; no clause distinguishes user-confirmed from unattended automated orders).

---

## Provenance notes

- Canonical T&Cs: two independent captures agree verbatim on every quoted line (§1, §2, §3, §5, §6.1, §7) — `~/.hermes/skills/process/smarkets-api-support/references/api-tcs-full-text.md` and `~/smarkets-api-support/scrape-aug18/help/api-tcs.md`. The `help-pages/` capture of the same article is a Cloudflare challenge stub and must not be used as a source.
- `responses/api-scope-confirmation.txt` and `api-scope-confirmation.txt` (repo root) are byte-identical duplicates; both are prior internal drafts of a customer-facing reply, not Smarkets policy documents. Treat their hedging and read-only-endpoint statements as internal positions consistent with the T&Cs, not as binding terms.
- Endpoint auth claims in Q1 finding 8 were verified directly against the live OpenAPI spec `security` blocks, not taken on trust from prose docs.
