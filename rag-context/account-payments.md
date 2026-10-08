# Account, Payments & Safer Gambling — RAG Context for Support Agents

> **Sources:** Smarkets & SBK Help Centre articles (scraped 2026-06-29) under `help-pages/smarkets/en-gb/` and `help-pages/sbk/en-gb/`.
> **Scope:** Smarkets (exchange) and SBK (sportsbook) — share parent company; many policies identical. Differences noted explicitly.
> **Cross-ref:** API-specific account/KYC in `api-support.md` §8. This file is the comprehensive reference.

---

## 1. ACCOUNT VERIFICATION (KYC)

### Electronic Verification (both)
- Both attempt electronic verification first — signup details run against official databases. Does **NOT** affect credit rating.
- If electronic verification fails, customer uploads photo ID + proof of address via file upload page (Smarkets: `smarkets.com/account/file-upload/`; SBK: in-app).
- Verification **begins after first deposit**. Electronic check completes within minutes; if documents needed, customer is emailed.

### Verification Timeframes
| | Electronic | Document Review Target |
|--|-----------|----------------------|
| **Smarkets** | Minutes | Within 72 hours |
| **SBK** | Minutes | Within 24 hours (verification process time); 72 hours (document guidelines) |

- High-volume periods may cause delays.

### 2FA (both)
- TOTP one-time codes (30-second refresh) via authenticator app.
- **SBK apps:** Authy, Duo Mobile, Google Authenticator. Enable: Account → Sign in details.
- **Smarkets API:** `POST /v3/sessions/verify/` (see api-support.md §1).
- Lost device: email support from registered address with proof of identity to disable 2FA.

---

## 2. DOCUMENTS REQUIRED

### Proof of Identity (both — identical)
Passport · Driving licence (with photo) · National Identity card. **Screenshots NOT accepted** — photo or scan only.

### Proof of Address (both — identical)
- Bank/Building Society/Credit Union statement (within 3 months)
- Utility bill (within 3 months)
- Council tax / local authority tax bill (current year)
- Tax bill (current year)
- Residency certificate from local government (within 3 months)
- Paper and PDF accepted. **Screenshots NOT accepted. Mobile phone bills NOT accepted.**

### Critical Rules
- **Cannot use same document for both ID and address.**
- ID must be fully visible, front-facing, all 4 corners in view, not at an angle.
- **Formats:** Bank statement = PDF/scan/photo of paper; ID = photo/scan.

### Common Rejection Reasons
Incorrect format · Full document not provided (missing pages, corners cut off) · Poor image quality · Expired or outside requested timeframe.

---

## 3. DEPOSITS

### Deposit Limits — Smarkets
| Method | Fee | Time | Min | Max (£/€) |
|--------|-----|------|-----|-----------|
| Instant Bank Transfer | Free | Instant | 10 | 10,000 |
| Visa Debit | Free | Instant | 10 | 3,500 |
| Solo / Maestro | Free | Instant | 10 | 3,500 |
| MasterCard / Eurocard | Free | Instant | 10 | 3,500 |
| Trustly | Free | Instant | 10 | 10,000 |
| Neteller | Free | Instant | 10 | 3,000 (5k daily) |
| Skrill | Free | Instant | 10 | 3,000 (5k daily) |
| Bank Transfer | Free | 5–10 business days | 10 | 10,000 |
| PayPal | Free | Instant | 25 | 250 |

### Deposit Limits — SBK
Same as Smarkets, **plus Apple Pay / Google Pay**: Free, Instant, £/€10 min, £/€3,500 max.

### Notes (both)
- Deposits only accepted in the account's designated currency.
- No Smarkets transaction fees (but customer's bank/e-wallet may charge).
- **Visa Debit recommended** for instant free deposits and unlimited withdrawals.
- **SBK-only:** Apple Pay / Google Pay available (not on Smarkets).

---

## 4. WITHDRAWALS

### Withdrawal Limits — Smarkets
| Method | Fee | Time | Min | Max |
|--------|-----|------|-----|-----|
| Instant Bank Transfer | Free | 12 hours | 10 | — |
| Visa Debit | Free | 1–6 business days | 10 | — |
| Solo / Maestro | Free | 1–6 business days | 10 | Some cards limited to deposit amount |
| MasterCard / Eurocard | Free | 1–6 business days | 10 | Some cards limited to deposit amount |
| Trustly | Free | 1–2 business days | 10 | — |
| Neteller | Free | 1–2 business days | 10 | — |
| Skrill | Free | 1–2 business days | 10 | — |
| Bank Transfer | Free | 5–10 business days | 20 | — |
| PayPal | Free | 1–2 business days | 10 | £/€5,500 max |

### Withdrawal Limits — SBK
Same as Smarkets, **plus Apple Pay / Google Pay**: Free, 1–6 business days, £/€10 min. PayPal max £5,500.

### E-Wallet Rule (both)
- If withdrawing **more than 4 times in 7 days** from an e-wallet, the 4th and subsequent withdrawals take **24 hours** to process.

### Bank Transfer Withdrawal (both — specific rules)
- **Last resort:** only processed when all other withdrawal options exhausted.
- **Min:** £20 / €20 / 250 SEK. No max. **Cannot transact in NOK.**
- Bank details required: UK (account no. + sort code) · USA (account no. + routing no.) · SEPA (IBAN + BIC/SWIFT) · Other (account no. + sort code/equivalent).
- Must upload bank statement showing name + details. Account must be fully verified.
- **Currency must match** account currency.

### "Why Can't I Make a Withdrawal?" — Common Causes
- Balance below minimum withdrawal
- Deposited via a now-removed payment method (contact support)
- Withdrawing from a different country to card registration
- Billing address differs from registered address
- Card used too many times in last 12 hours
- If closed loop satisfied and still stuck: add a new payment method (deposit min via Instant Bank Transfer) or request bank transfer via support.

### Pay to Bank (SBK only)
- Uses **TrueLayer** open banking. Allows instant withdrawal to bank account even if originally deposited by card.
- Verifies bank account matches original card deposit account. Maintains closed loop.
- If verification fails, standard card withdrawal remains available.
- Funds arrive **instantly** (vs 1–6 days for card withdrawals).

### Instant Bank Transfer (SBK — detail)
- Open Banking technology. **GBP only in UK; EUR only in Ireland.**
- Deposits instant. Withdrawals: within 12 hours (UK); up to 24 hours (non-Revolut Ireland).
- **24-hour hold** after first deposit with a new bank account (except Revolut — immediate).
- Limits: £/€10,000 deposit / £/€100,000 withdrawal per transaction.

---

## 5. CLOSED LOOP SYSTEM

Both operate a **closed loop** for AML compliance: funds must be withdrawn to the **same payment method** used to deposit.

### Net Deposits
```
Net Deposits (per method) = Total Deposits − Total Withdrawals
```
- Must balance (reduce to £0) all **positive net deposits** on each method before withdrawing excess to a preferred method.
- **Example:** Deposit £100 Visa + £50 MasterCard. To withdraw £150 to MasterCard, must first withdraw £100 to Visa (balancing it to £0).

### Mastercard / Maestro Restriction
- Certain cards: withdrawals limited to **net deposit amount** from that card. Profit must be withdrawn via a different method.

### Removing a Card No Longer in Use
- **Smarkets:** Manage Payments page (`smarkets.com/account/manage`). If unable, contact support. Replacement card: deposit with new card, then contact support to remove old card.
- **SBK:** Funds tab. If can't remove due to outstanding net deposits:
  - **Expired/replaced (same bank):** deposit with new card, then remove old from Funds page.
  - **Lost/stolen/closed:** contact support. May require PDF bank statements (old + new methods, showing name, address, sort code, account no., Smarkets deposit) + card photo (first 6 + last 4 digits, name, expiry; hide middle digits).

---

## 6. PAYMENT METHODS — KEY DETAIL

### Trustly (both)
- Direct bank deposit. No app/signup/card numbers needed.
- **Available:** UK* and Sweden only. GBP and SEK only. (*Excluding Isle of Man, Guernsey, Jersey.)
- Deposits: instant, £/€10 min, £/€10,000 daily max. Withdrawals: 1–2 business days, £/€10 min, £/€100,000 max.

### Skrill / Neteller (both)
- E-wallets. One account per Smarkets/SBK account.
- Deposits: within minutes, £/€10 min, £/€3,000 max. Withdrawals: 1–2 business days, £/€10 min.
- Can only withdraw after first depositing via that e-wallet. Subject to closed loop.

### Funds Protection (both)
- TLS/SSL encryption on all transactions.
- UK customer funds held by **Smarkets (Clients) Limited** under Trust Deed — **high level of protection** per UKGC rating.
- Non-UK funds in dedicated ring-fenced accounts.

### Currencies
- **SBK:** GBP, EUR only.
- **Smarkets:** AUD, BRL, CAD, CHF, CZK, DKK, EUR, GBP, HKD, HUF, JPY, NOK, PLN, SEK, USD.

---

## 7. BONUS & PROMOTIONS

### Smarkets — Welcome Bonus (0% Commission, 60 Days)
- **Code:** `COMMFREE` at registration. Min £10/€10 first deposit by **Debit Card or Instant Banking**.
- **NOT eligible:** Skrill, Neteller, PayPal, Revolut, virtual/prepaid cards (incl. virtual Monzo).
- 0% commission on all bets settling within 60 days of first deposit. After: reverts to 2%.
- **Ineligible:** API users, existing SBK users, bonus-ineligible customers.
- One per individual/family/household/email/payment account/IP/shared computer.

### Smarkets — Matched Betting Promo (OddsMonkey/Outplayed/Matched Betting Blog)
- 0% commission for premium members. Must **opt in first**, then place qualifying integrated bet every 30 days.
- Activated within 15 mins. **Skrill/Neteller/Trustly/PayPal made unavailable** during promo.
- Non-OddsMonkey/Outplayed/MBB API users ineligible. Not available in Sweden.

### SBK — UK Welcome Bonus (Bet £20, Get £50 in Free Bets)
- Min £20 first deposit by **Debit Card, Bank Transfer, or Trustly**. Place single £20 bet at min odds **3.0 (2/1)**.
- **NOT eligible:** PayPal, Skrill, Neteller, Paysafe, Revolut, virtual/prepaid cards.
- **Distribution:** £5 Bet Builder + £5 Multiple on settlement → £10 Free Bet + £5 Bet Builder (24h) → £10 Free Bet + £5 Bet Builder + 2×£5 Multiple (48h).
- Free bets require **min 3 legs**. Not on full cover bets. Stakes **not returned** on wins.
- Unused free bets **expire 5 days** after credit. Non-withdrawable. Cashed-out bets don't qualify.

### SBK — Ireland & Malta Welcome (Bet €10, Get €50)
- Min €10 deposit. Same exclusions. Qualifying bet €10 at min odds 3.0.

### SBK — Weekly Offer (Bet £/€50, Get £/€10)
- Opt-in. Place £50 of bets at min odds 3.0 (Mon 08:00–Sun 23:59 BST).
- Reward: £5 Horse Racing Multiple + £5 Football Bet Builder (both min 5 legs). Expire 7 days. UK/IE/Malta.

### SBK — US Offer (Bet $100, Get $20)
- Indiana only. 21+. Opt-in. $100 bets at min odds +100. Reward: $10 Parlay + $10 SGP (min 3 legs). Expire 7 days.

### Bonus Removed/Not Received — Common Causes
- Didn't enter promo code (Smarkets: `COMMFREE`).
- First deposit below minimum or via ineligible method (e-wallet/prepaid).
- Another person at same address already claimed.
- Customer notified as bonus-ineligible via email.

---

## 8. SAFER GAMBLING

### Policy (both — identical)
Only accepts members **18+** (21+ US). May suspend accounts, impose time-outs or limits if problem gambling signs identified.

### Timeouts (both — identical)
- **Durations:** 1, 7, 31, 42 days.
- Completely blocks account access (incl. withdrawals via cashier). **Cannot be reversed.**
- Account **automatically reopens** at end. To withdraw during timeout, contact support.
- **Smarkets:** Settings → Limits → SET TIMEOUT. **SBK:** Account → My limits → Time out.

### Self-Exclusion (both — identical)
- **Durations:** 6 months, 1 year, 5 years, or forever (permanent).
- Access **NOT reinstated** during exclusion. Balance returned **within 48 hours** (or contact support for faster).
- **Permanent exclusion** cannot be reversed under any circumstances.
- After exclusion ends, account does **NOT** auto-reopen — must **contact support** to reinstate.
- **Smarkets:** Settings → Limits → SET EXCLUSION. **SBK:** Account → My limits → Self-exclusion (above 5 years/permanent: contact support).
- **GAMSTOP:** Free UK service for multi-operator exclusion (6 months–5 years), also blocks marketing.

### Deposit & Loss Limits

**SBK (detailed):**
- **Deposit limits:** Daily, weekly, monthly. **NET** (deposits − withdrawals) and/or **GROSS** (total deposits) options.
  - Lower limit: immediate. Increase: mandatory **7-day cooling-off**.
  - Reset: daily at 00:00 UK; weekly/monthly/yearly every 7/30/365 days from set date.
- **Loss limits:** Daily, weekly, monthly, yearly. Net limit (winnings added back, losses deducted at settlement). Increase/removal subject to cooling-off.
- **UK defaults:** Registered after 28 Feb 2023 → £4,999.99 monthly net deposit. After 28 Mar 2023 → + £1,000 daily net deposit. Increase may require proof of income.

**Smarkets:** Offers deposit, loss, and stake limits (Settings → Limits).

### Gambling Blocks (both — identical)
- **Gambling-specific:** GamBlock (Win/Android/iOS), BetBlocker (Win/macOS/Linux/iOS/Android/Fire OS).
- **General:** Netnanny (Win/iOS/Android).
- **GAMSTOP** for all GB-licensed operators. **Bank gambling blocks** (see Gambling Commission website).

### Support Organisations (both)
Gamblers Anonymous · GamCare · GambleAware · NHS · National Problem Gambling Clinic · Gambling Therapy (Gordon Moody). US: ncpgambling.org / 1-800-GAMBLER.

---

## 9. ACCOUNT RESTRICTIONS

### Verification-Related (both — identical)
If verification not completed within required timeframe:
- **Deposit block:** Cannot deposit until verification complete.
- **Bet block:** Cannot place/alter bets until verification complete.
- **Temporary suspension:** Cannot log in until verification complete.

### Source of Funds Non-Compliance
- Customers **not obligated** to provide requested info, but account **will be restricted/suspended** if verification can't be completed.
- If documents provided later, account reviewed again.

### AML (both)
All transactions may be checked. Suspicious transactions reported to authorities.

---

## 10. SOURCE OF FUNDS & WEALTH

### Definitions (both — identical)
- **Source of Funds (SoF):** Origin of funds deposited in a specific transaction/set of transactions (e.g., deposit method).
- **Source of Wealth (SoW):** Origin of overall wealth (employment, inheritance, property, investments).
- **Affordability Check:** Safer gambling check assessing current financial situation. Different purpose from SoF but may overlap in documents requested.

### Why Checks Are Performed
- Ensure account holder is in control. Protect from fraud. Comply with AML laws in all jurisdictions. Required regardless of customer location.

### What May Be Requested
- Occupation and income (or main income source if not working).
- **Proof of income:** Payslips, P60, SA302 self-assessment, employment summary.
- **Proof of payment method:** Card image, bank statements showing deposits.
- **Proof of savings:** Savings/investment account statement.
- **Property sale:** Confirmation from solicitor/lawyer.

### Key Points
- **NEVER contact the customer's employer.**
- Not all customers require this. Contacted via email if needed.
- Aims to be frictionless via electronic verification, but documents may still be required.

### GDPR & Data Privacy (both — identical)
- Data used per T&Cs/privacy policy. Not kept longer than necessary (except legal/licensing obligations).
- Stringent technical/organisational measures. Data deleted after a period if service stopped (dependent on country/licence).

---

## QUICK REFERENCE — KEY DIFFERENCES

| Feature | Smarkets | SBK |
|---------|----------|-----|
| Product | Exchange | Sportsbook (app) |
| Apple Pay / Google Pay | ❌ | ✅ |
| Pay to Bank (TrueLayer instant) | ❌ | ✅ |
| Currencies | 15 (incl. NOK, SEK, JPY…) | GBP, EUR only |
| Welcome bonus | 0% commission 60 days (`COMMFREE`) | £50 free bets (Bet £20 @ 3.0) |
| Bonus type | Commission discount | Free bet tokens |
| Deposit limits | Deposit/loss/stake | Net + Gross + loss limits, UK default caps |
| Doc review target | 72 hours | 24 hours |
| Support email | support@smarkets.com | support@getsbk.com |
| Closed loop | ✅ | ✅ (detailed article with examples) |

**Support address (both):** 1 Commodity Quay, St Katharine Docks, London, E1W 1AZ, UK.
**API technical:** api@smarkets.com.
