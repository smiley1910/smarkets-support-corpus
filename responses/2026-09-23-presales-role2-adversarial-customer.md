# Role 2 — Adversarial customer perspective (council pass)
# Smarkets API presales draft — Betfair algo operator, ~£100k/month volume

**Compiled:** 2026-09-23
**Basis:** the draft's described coverage (verified account + request form + £150 fee with 60 day refund; quotes and market endpoints; place and cancel, amend via cancel + replace; pre-approved scope; Standard 2% at 100k, Pro 1% path; no market maker rates; global 1200/60s + quotes 50/60s + orders 10/s; English only, all prose).
The literal draft text was not on disk at audit time. The coverage map and the irritation list are keyed to the described coverage and should be re-checked line by line against the literal text before send.

**Ground truth used:** API T&Cs full text (Sections 1-8), Smarkets commission FAQ (help.smarkets.com 212654665), live trading spec fetched 2026-09-23 (`/private/tmp/smk_live_spec.json`), rate-limits.md, fok-ioc-orders.md, VOICE_CORE_PINNED.md.

---

## 1. Coverage map (customer question -> full / partial / missing)

**Q1. How to apply — PARTIAL.**
Has: verified account, request form, £150 fee, 60 day refund.
Missing (all material to a presales buyer):
- the actual form URL (support.smarkets.com/p/6MLL-PL7/api-request-form) and docs portal (docs.smarkets.com);
- approval is discretionary ("Smarkets retains full discretion to refuse access");
- the sequence: review -> on approval the fee is deducted from balance -> access activated;
- T&Cs Section 4: applicant must provide technical setup and intended use details, and keep them updated;
- the 60 day compliance review ("All customers will be subject to a compliance review of their account within the first 60 days to remain eligible to continue trading");
- API accounts are ineligible for the 60 day 0% commission offer and affiliate offers (two different 60 day things; conflation risk).

**Q2. Market discovery + live data — PARTIAL.**
Has: quotes and market endpoints.
Missing:
- the endpoint set: GET /v3/events/ (600/60s), /v3/events/{ids}/markets/, /markets_count/, /markets/{ids}/contracts/, /last_executed_prices/, /volumes/;
- the decisive fact: **no streaming feed** — REST polling only (no equivalent of Betfair's streaming API);
- quotes returns the P2P order book only and can be thin in play; quotes cap 50/60s is the binding poll budget (how many markets can be watched in near real time);
- in-play delays 4s horse/darts, else 8s, and market halts affect live data.

**Q3. Place / amend / cancel — FULL.**
Correct: place, cancel, cancel all, and amend only via cancel + replace (no amend endpoint exists in the trading API).
One-line additions worth making (pre-empt obvious follow-ups, not gaps): replacement = new order ID, loses queue priority, costs two calls; order types default `good_til_halted`, cancelled on market halt and reduction factor (`keep_in_play` survives halt); cancel all 1/60s; min stake £0.05 / max £99,999.99.

**Q4. Fees at £100k — PARTIAL (most material gap).**
Has: Standard 2%, Pro 1% path.
Missing:
- **Pro charges 1% on losing matched bets too** (commission FAQ: "either on the profit if it wins or the losses if it loses") — at algo volume this can cost more than Standard, so "Pro 1% path" without this reads as a discount when it may not be;
- Pro is opt-in only after 80% of 1,500 bets placed OR £1m staked in a calendar month; 3 month minimum before opting back out; permanently forfeits any commission promotion;
- Select 3% applies automatically above £25,000 net profit over 12 months;
- no API-specific discount: tiers are volume and profit based, same as website users;
- API ineligibility for the 60 day 0% offer.

**Q5. Market maker deals — FULL as a decline, CONDITIONAL.**
Condition: the decline must be the flat approved line ("The Market Maker commission tier isn't available for your account"), must NOT mention Sweden or any percentage, and must pair with the Pro alternative (Pro removes the 1,500 bet / £1m staked limits that usually trigger the ask). If the draft only says "no market maker rates" and stops, it reads as "we don't want your flow".

**Q6. Rate limits + restrictions — PARTIAL.**
Has: 1200/60s global, quotes 50/60s, orders 10/s; pre-approved scope.
Missing:
- cancel one order 10/s, cancel all 1/60s, GET /v3/events/ 600/60s, login 5/300s;
- per-endpoint caps sit on top of the 1200 global, they are not extra allocations;
- increases are at Smarkets' discretion, requested via api@smarkets.com, not guaranteed;
- 429 handling: error_type RATE_LIMIT_EXCEEDED, count/limit/expiry (RFC 2822 expiry), quotes 429 has no structured body;
- restrictions detail: no latency arbitrage or court-siding, no benchmarking our markets or prices against other operators, no sharing or redistributing platform data, no data extraction without commensurate trading volumes, access can be withdrawn at any time.

---

## 2. Top 3 objections the trader will reply with

**1. "50 quote calls a minute is not a live feed. My Betfair algo watches hundreds of markets in real time off the streaming API, and here you're telling me to poll with a 50 a minute cap. Is there a streaming option, and can the cap be raised for an account doing £100k a month?"**
Defused by: stating plainly there is no streaming feed; polling only; increases at discretion via api@smarkets.com; the 429 mechanics so he can engineer to the cap.

**2. "Your fee answer is doing a lot of work with the word 'path'. 1% on losing bets as well as winning ones is not cheaper than 2% on net winnings, and you say I can be forced onto it at 1,500 bets a month. What do I actually pay at £100k a month, and is Pro opt-in or mandatory?"**
Defused by: the Pro loss-charging mechanic, the 1,500 bet / £1m staked thresholds, the 80% opt-in trigger, and Select at £25k / 12 months, all stated in the fees paragraph.

**3. "You can withdraw access at any time, review my account in the first 60 days, restrict me to pre-approved markets you won't list, and prohibit benchmarking, and you want £150 up front. Which markets will I be approved for, and what happens to my £150 if the review goes the other way?"**
Defused by: pre-approval is per account, decided during application review, not published, confirmed via api@smarkets.com; the £150 is refunded if he permanently withdraws within the first 60 days; access is discretionary and stated as such.

---

## 3. Sentences likely to confuse or irritate

- "amend via cancel plus replace" with no consequences stated: reads as a workaround. Add new order ID / queue priority / two calls against limits.
- "Pro 1 percent path": "path" implies cheaper. At his volume this is the line that turns into a later complaint. Must carry the loss-charging mechanic.
- "150 fee with 60 day refund" sitting anywhere near a mention of the 0% offer, or without the ineligibility line: he has seen "60 days 0% commission" on the website and will ask why he does not get it.
- "verified account" undefined: he will ask verified how, and how long.
- "pre-approved scope" / "pre-approved events and markets" without "per account, decided during review, not published, confirmed via api@smarkets.com": reads as a trap, and it is the thing he most needs before paying £150.
- "no market maker rates" without the adjacent Pro alternative: reads as disinterest.
- Any softening on limits ("we may be able to increase"): state defaults and that increases are discretionary, in one flat line.
- Any competitor comparison (he runs Betfair): do not engage, per standing rule.

---

## 4. Minimal fixes (drop-in lines, no full rewrite)

1. **Apply:** add "The form is at support.smarkets.com/p/6MLL-PL7/api-request-form and the documentation is at docs.smarkets.com. Approval is at Smarkets' discretion, and once approved the £150 is deducted from your balance and your API access is activated. You'll be asked for details of your technical setup and intended use, and to keep them updated. Your account will be reviewed for compliance within the first 60 days to remain eligible to continue trading, and the £150 is refunded if you permanently withdraw within the first 60 days."
2. **Live data:** add "There is no streaming feed. The API is REST only, so live prices come from polling GET /v3/markets/{market_ids}/quotes/, which is capped at 50 requests per 60 seconds for API users. Market discovery is via GET /v3/events/ and GET /v3/events/{event_ids}/markets/, with contracts, last executed prices and volumes on the market endpoints. The quotes endpoint shows the P2P order book, which can be thin in play."
3. **Amend:** add "A replacement is a new order with a new order ID, so it loses its place in the queue, and the cancel and the placement each count against your limits."
4. **Fees (mandatory):** add "The Pro tier charges 1% on each matched bet that settles, on the winnings if it wins and on the losses if it loses, and it is an opt-in once you pass 80% of 1,500 bets placed or £1m staked in a calendar month. The Select tier applies 3% automatically above £25,000 net profit over 12 months. API accounts are not eligible for the 60 day 0% commission offer or affiliate offers."
5. **Rate limits:** add "Order placement and single order cancellation are each capped at 10 requests per second, cancel all orders at 1 request per 60 seconds, and GET /v3/events/ at 600 requests per 60 seconds. These caps sit on top of the 1200 requests per 60 seconds global limit, not beside it. Increases are at Smarkets' discretion and can be requested via api@smarkets.com."
6. **Restrictions:** add "Usage is limited to pre-approved events and markets, and does not extend to latency arbitrage, court-siding, benchmarking our prices against other operators, or sharing platform data. Smarkets can withdraw API access at any time under the API terms."
7. **Market maker:** ensure the decline is the flat line plus "The Pro tier removes the 1,500 bet and £1m staked monthly limits and is available once you pass 80% of either threshold." Do not explain the Swedish tier or any percentage.

---

## 5. Grade

**MINOR FIXES.**

Nothing stated in the described draft is wrong: every described fact checks against the API T&Cs and today's live spec. But four of six answers are partial on points this specific customer will probe, and two omissions are mislead-risk rather than polish:

- Fix 4 (Pro charges on losses, opt-in mechanics) is **mandatory** before send.
- Fix 2 (no streaming, quotes 50/60s as the poll budget) is **mandatory** before send.
- Fixes 1, 3, 5, 6, 7 are one line each and strongly recommended.

No restructuring or rewrite needed.

**Note for Role 1 (fact/process):** `references/commission-tiers-faq.md` table states Pro is "net profit per market" — this contradicts the help-centre commission FAQ (212654665), which states Pro and Select charge "either on the profit if it wins or the losses if it loses". Use the help-centre wording (and VOICE_CORE_PINNED) as the source for any customer-facing Pro mechanics.
