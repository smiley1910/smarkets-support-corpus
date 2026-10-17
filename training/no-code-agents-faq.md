# Smarkets API — No-Code FAQ

*For Zapier / Make / n8n / Bubble users. No coding needed, just an HTTP module.*
*Full docs: docs.smarkets.com. API help: api@smarkets.com.*

---

**How do I get access?**
1. You need a verified Smarkets account.
2. Fill in the API Request Form: support.smarkets.com/p/6MLL-PL7/api-request-form
3. It costs £150 once, taken from your balance. You get it back if you quit within 60 days.

There is no test mode and no data-only plan. One product: prices + betting together.

**How do I log in?**
There is no API key. Use your normal email + password.
1. Call `POST api.smarkets.com/v3/sessions/` with `username` = your email, plus `password`. (The field must be called `username`.)
2. Save the `token` from the reply.
3. On every other call, add the header `Authorization: Session-Token YOUR_TOKEN`.

Got an authenticator app? Add one more call after login: `POST /v3/sessions/verify/` with your 6-digit code.

**Why do I keep getting logged out (401)?**
Your login expires after about 20–30 minutes. Fix: log in again and retry once. Build that as a branch, not a loop — login only allows 5 tries per 5 minutes.

**How do I find a bet?**
Go down 4 levels: Event (the match) → Market (e.g. Match Winner) → Contract (e.g. Home Win) → Order (your bet).
- Lists of matches, markets and outcomes are free, no login needed.
- Live prices need your login header.

Website shows a price but the API shows nothing? Normal on quiet live markets. The API only shows other customers' orders.

**How do I place a bet?**
Call `POST /v3/orders/` with these 5 things: `market_id`, `contract_id`, `price`, `quantity`, `side`.

- **Side:** `buy` = back (it WILL happen). `sell` = lay (it WON'T happen).
- **Odds (`price`):** not normal odds. Divide 10000 by what you want. Want 2.0? Send 5000. Want 4.0? Send 2500. Copy the price from the prices call if unsure.
- **Stake (`quantity`):** not pounds. Multiply pounds by 10000. Want £2? Send 20000. Minimum is 500 (£0.05). Sending 800 means £0.08, not £2.
- **Tip:** add a `label` like `"zapier-arsenal-1"` so you can find the bet later.

**Why was my bet rejected?**
- Not enough money → your other open bets are locking it up. Cancel one or lower the stake.
- Wrong price → copy a price from the prices call.
- Market paused (goal, VAR) → wait and retry. To survive pauses, set `type` to `keep_in_play`.
- Asked to do something on the website first (gambling check, ID check) → do it on smarkets.com, then retry. No setup change needed.

**How do I check or cancel a bet?**
- Check: `GET /v3/orders/` shows open + recent bets.
- Cancel one: `DELETE /v3/orders/{order_id}/`.
- Cancel everything: `DELETE /v3/orders/` — max once per minute. Keep it away from auto-retry.

**How often can I check prices?**
Max 50 price checks per minute, 1200 total calls per minute. Two rules:
1. Ask for up to 200 markets in ONE call (comma-separated IDs), not one call each.
2. One timer scenario, not five. Multiple tools on one account share the same limit.

Too fast = error 429. Just wait a minute and slow down.

**What do the errors mean?**
- 401 → logged out. Log in again.
- 403 → not approved yet, or outside your approved markets. Email api@smarkets.com.
- Blocked page (HTML, not JSON) from a cloud server → network block, not your password. Try from home to confirm, then contact support.
- Bet rejected with a code → read the code name, it says the reason (see above).
- 500 / 503 / 504 → our side. Wait, retry once, then email api@smarkets.com with the time.

**What am I not allowed to do?**
View prices and bet. That is it. No copying large amounts of prices without betting, no reselling data, no comparing our prices to sell elsewhere, no extra accounts. Breaks = warning, then suspension, then closure.

**My statement? My commission?**
- Statement: needs exact hour times (e.g. 14:00 to 15:00) or it fails.
- Commission: 2% of profit per market, only when you win. API access does not lower it.

**Who do I email?**
- API errors and limits: api@smarkets.com
- Account, money, ID, application: support@smarkets.com
- Always include: the error code, the call you made (no passwords), what you expected, when it started.
