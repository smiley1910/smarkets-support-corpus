# Common Technical Scenarios

Extracted from SKILL.md. Detailed escalation scenarios with API examples and response templates.


## Common Technical Scenarios

### 401 AUTH_REQUIRED on POST but GET works
This is a top-3 support issue. Three main causes:

1. **Mixed auth methods** — GET may work via cookie auth (browser) while POST requires `Authorization: Session-Token <token>` header. Cookie auth is not part of the documented API. The user must use the same auth method for ALL requests.

2. **Stale token** — Token may have expired (30 min inactivity) or been invalidated by a session limit. They must log in again to get a fresh token.

3. **MFA not fully verified** — If the account has MFA enabled, `POST /v3/sessions/` returns a limited session. They must complete `POST /v3/sessions/verify/` with the TOTP code before placing orders.

**Key diagnostic:** Ask for full curl output showing headers, URL, and response body. 401 with `data: None` suggests a completely unrecognised token.

### 403 — Cloudflare vs API
- **API FORBIDDEN (JSON response)**: Account-level — check approval, compliance, fee payment. May also return SOURCE_BLOCKED or IP_NOT_TRUSTED for IP-based blocks
- **Edge block (HTML response)**: Network-level — VPS blocks, source IP issues. Not controllable via API auth. IP whitelisting is not a documented or self-service feature, but internal Cloudflare allowlisting CAN be requested via api@smarkets.com for datacenter IPs in supported jurisdictions. If a customer is in a supported jurisdiction (UK, Malta, Ireland, Sweden) but still getting Cloudflare challenges on a datacenter IP, offer to raise an internal allowlisting request rather than telling them it's impossible. Two failure factors: (1) jurisdiction check (blocking unsupported countries), (2) IP reputation (datacenter IPs challenged even in supported jurisdictions). When a customer provides hostnames for whitelisting, only confirm ``api.smarkets.com`` (the documented endpoint). Streaming hostnames like ``sio-live.smarkets.com`` are NOT part of the API — see ``references/streaming-infrastructure-and-cftc-product.md``.
- **Jurisdiction-based block (HTML response, same Cloudflare challenge)**: If the server IP geolocates to a jurisdiction where Smarkets is not licensed (e.g. Finland, where a Hetzner Helsinki VPS would be blocked), ALL requests are blocked at the Cloudflare edge regardless of allowlisting. This looks identical to a generic datacenter IP block (same ``cf-mitigated: challenge``, same HTML "Security Check" page) but the root cause is the server's geographic location, not bot detection. IP allowlisting will NOT help — the customer must host their server in a supported jurisdiction. There is no alternative hostname or access route. Supported jurisdictions include UK, Malta, Ireland, and Sweden. Key diagnostic clue: if the customer confirms their local (residential IP) environment works but the VPS does not, and the VPS is in a country where Smarkets is not licensed, this is a jurisdiction block, not a WAF rule that can be adjusted.

### IP Allowlisting with Undocumented Hostnames

When Smarkets offers internal IP allowlisting (Cloudflare edge configuration) for a customer's datacenter IP in a supported jurisdiction, the customer may respond with multiple hostnames they've discovered through network inspection or deprecated documentation. Only ``api.smarkets.com`` is the documented API base URL.

**Three distinct Smarkets infrastructure tiers:**

| Tier | Hostname | Protocol | Status |
|------|----------|----------|--------|
| Old streaming API (deprecated) | ``stream.smarkets.com:3801`` | TCP + SSL + protobuf | Deprecated; was in ``smk_python_sdk`` (GitHub, copyright 2011, Python 2.7/3.5) |
| Current REST API (v3) | ``api.smarkets.com`` | HTTPS / JSON | Active, documented at docs.smarkets.com |
| Website frontend Socket.IO | ``sio-live.smarkets.com`` | WebSocket (Socket.IO) | Internal frontend infrastructure, never documented as API |

**Critical distinction:** ``sio-live.smarkets.com`` is NOT from the deprecated GitHub SDK. The old ``smk_python_sdk`` (``github.com/smarkets/smk_python_sdk``, still public) used ``stream.smarkets.com:3801`` with protobuf-over-TCP. ``sio-live`` is the website's Socket.IO push channel, discovered by customers through browser DevTools. Neither the old streaming API nor ``sio-live`` are part of the current documented API.

**How to handle:**

#. Confirm the allowlisting request for ``api.smarkets.com`` only
#. Flag any additional hostnames (e.g., ``sio-live.smarkets.com``) as not part of the documented API
#. If the customer needs streaming/real-time data, take ownership and ask them to reply here with the use case, the old streaming API (``stream.smarkets.com:3801``) is deprecated and ``sio-live`` was never an API endpoint
#. The deprecated ``smk_python_sdk`` repo (archived Jan 2019) and ``smk_api_docs`` repo are on GitHub. Customers may find them and assume the streaming API is still supported. It is not — ``stream.smarkets.com`` is NXDOMAIN (verified July 2026). **Verify infra claims before citing: see** ``references/deprecated-streaming-api-and-sio-live.md`` **§ Verification Evidence.**
#. Full streaming topology, CFTC product details, and infrastructure intelligence map: see ``references/streaming-infrastructure-and-cftc-product.md``

See ``references/deprecated-streaming-api-and-sio-live.md`` for full research findings.

### Rate limiting (429)
- Check `expiry` field — customer must wait until that time
- If hitting limits with low usage: investigate multiple concurrent clients
- Higher limits: take ownership and ask the customer to reply here with the use case
- Quotes endpoint: 50 requests/60 seconds for API users

### Customer mentions streaming endpoints (sio-live, sio-delayed, etc.)

Customers may mention ``sio-live.smarkets.com`` or other streaming hostnames when requesting IP whitelisting or asking about real-time data. They discovered these by reading the Smarkets website's public frontend JavaScript (DevTools → Sources → search JS chunks for ``wss://``).

**Key facts:**
- The documented API is REST-only via ``api.smarkets.com``
- WebSocket streaming endpoints exist as website infrastructure but are NOT part of the public API
- The old deprecated SDK (``smk_python_sdk``) used ``stream.smarkets.com:3801`` (protobuf/TCP) — that host is dead
- Current streaming uses WebSocket (``sio-live.smarkets.com``, ``sio-delayed.smarkets.com``)
- CFTC-specific variants exist (``cftc-sio-live.smarkets.com``) for the unannounced US prediction market product

**Response structure:**
1. Confirm the whitelisting request for ``api.smarkets.com`` (the documented endpoint)
2. Flag that ``sio-live.smarkets.com`` is not part of the documented API
3. The documented approach for market data is REST endpoints (quotes, last_executed_prices, volumes)
4. If they need streaming: take ownership and ask them to reply here with the use case
5. Do NOT mention CFTC endpoints or the Smarkets Predictions product
6. Do NOT confirm or deny the existence of streaming endpoints as API features
7. Do NOT raise the T&C concern about reverse engineering — flag internally only

Full detail: ``references/streaming-infrastructure-and-cftc-product.md``

### Order placement failures
Rejection codes from `POST /v3/orders/` response schemas:
- **400 codes**: ORDER_REJECTED_MARKET_SETTLED, ORDER_REJECTED_MARKET_NOT_FOUND, ORDER_REJECTED_LIMIT_EXCEEDED, ORDER_INVALID_INVALID_PRICE, ORDER_INVALID_INVALID_QUANTITY, ORDER_REJECTED_INSUFFICIENT_FUNDS, ORDER_REJECTED_CONTRACT_SETTLED, ORDER_CANCELLED_TRADING_SUSPENDED, ORDER_REJECTED_MARKET_HALTED, ORDER_REJECTED_THROTTLE_EXCEEDED, ORDER_REJECTED_CROSSED_SELF, ORDER_CANCELLED_MARKET_HALTED, ORDER_REJECTED_STAKE_LIMIT_EXCEEDED, ORDER_REJECTED_CAPACITY_REACHED, ORDER_REJECTED_CONTRACT_NOT_FOUND, ORDER_CANCELLED_INSUFFICIENT_LIQUIDITY, ORDER_CANCELLED_MEMBER_REQUESTED, ORDER_REJECTED_MARKET_NOT_OPEN, ORDER_REJECTED_TRADING_SUSPENDED, ORDER_REJECTED_ACCOUNT_SUSPENDED, ORDER_REJECTED_SERVICE_TEMPORARILY_UNAVAILABLE, ORDER_CANCELLED_ADMIN_REQUESTED
- **403 codes**: KYC_PERMISSION_DENIED, NO_DEPOSITS, ACCOUNT_UNVERIFIED, ACTION_BLOCKED, RG_ACK_REQUIRED
- **503 codes**: CREATE_ORDER_TIMEOUT, KYC_SERVICE_UNAVAILABLE, ORDER_UNAVAILABLE, AUTH_UNAVAILABLE, KYC_SERVICE_INTERNAL_ERROR

### Commission tier queries ("Can I get Pro Tier 1%?")

Customers often assume API access automatically means better rates. It doesn't.

**Quick reference for the three tiers:**
- **Standard (2%)** — `commission_type: 0.02`, default for all accounts
- **Pro (1%)** — `commission_type: 0.01`, requires ≥80% of 1,500 bets/month OR £1M staked/month, then opt-in via support
- **Select (3%)** — `commission_type: 0.03`, auto-applied when net profit >£25K over 12 months

**Three rules of thumb:**
1. **API access ≠ lower rates.** The same tier system applies to website, mobile, and API users. No API-specific discount exists.
2. **Pro Tier requires opt-in.** Even if a customer's volume qualifies, it's not automatic — they must contact support.
3. **API users ARE eligible for Pro Tier**, just not promotional rates (0% new-user, affiliate). The Pro Tier (1%) is a volume-based tier, not a promotion.

**Response structure:**
1. Check what `commission_type` they're seeing (0.02, 0.01, 0.03)
2. If they're on Standard: explain that Pro Tier requires volume thresholds + opt-in, not automatic
3. If they think they qualify: direct them to contact support to opt in
4. If they're on Select (3%): explain it's automatic based on profit, not a penalty

Full detail in `references/commission-tiers-faq.md`.

### Read-Only / Data-Only API Access Requests

**Common customer ask:** "I only want to retrieve live prices for personal research. I will not trade via the API. Can I get read-only access?"

**Answer:** No. Smarkets does not offer a read-only or data-only API tier. The API is a single product — GBP150 setup fee, full access (market data + order management). There is no reduced-access or data-feed-only option.

**Key documentation points:**
- Per Section 2 of API T&Cs: *"All other uses are strictly prohibited, including but not limited to, odds scraping, concealing API calls, browser impersonation or reverse engineering."* — standalone data extraction is not a permitted use
- **Market data endpoints work without auth but return delayed data.** The quotes endpoint description explicitly states: *"If session token is not sent, these prices will be delayed."* The rate limit note distinguishes "API users" (50 req/60s) from "non-API users" (lower). In practice, `GET /v3/markets/{id}/quotes/`, `GET /v3/markets/{id}/last_executed_prices/`, and `GET /v3/markets/{id}/volumes/` all return HTTP 200 with full data (including multi-level order book depth) without any auth header. The OpenAPI spec marks these as `security: [{"api_key": []}]` (auth required) but the runtime behaviour contradicts this — the spec's `security` field is imprecise documentation. See `references/noauth-quotes-endpoint.md` for full evidence and the "issue vs delayed feed" analysis
- **All three market data endpoints confirmed working without auth** (June 2026 live testing): `quotes/`, `last_executed_prices/`, and `volumes/` all return HTTP 200 with full data. The spec marks them `security: [{api_key: []}]` but runtime contradicts this.
- Public unauthenticated endpoints (events, markets, contracts, competitors, states) all return full data without a token

**How to decline (Pattern B — short, quoting docs):**

> Thanks for reaching out.
>
> Unfortunately, Smarkets does not offer a read-only API tier. The API is a single product that requires the full application process and GBP150 setup fee — there is no separate data-only plan.
>
> Per the API T&Cs (Section 2): *"All other uses are strictly prohibited, including but not limited to, odds scraping, concealing API calls, browser impersonation or reverse engineering."* While some market data endpoints (quotes) technically respond without auth, the T&Cs prohibit unauthenticated data extraction. Public endpoints for events/competitors/contracts are available. See `references/noauth-quotes-endpoint.md` for details on which endpoints respond without auth.
>
> If your research can justify the GBP150 fee (refundable within 60 days if you withdraw), you are welcome to apply via the API Request Form. Otherwise we cannot accommodate read-only access at this time.

**Alternative paths to offer (if appropriate):**
- Unauthenticated public endpoints for event/market/contract data, plus quotes (delayed) — technically accessible without auth but T&Cs prohibit standalone data extraction
- Full API application (GBP150, refundable within 60 days)

**Pitfalls:**
- Do not suggest scraping as an alternative — it is explicitly prohibited in the T&Cs
- Do not promise a future option — there is no roadmap for a read-only tier in any current documentation
- Do not pad with multiple alternatives if none are viable — a clean decline with one alternative is better than a confusing list of dead ends

### Jurisdiction queries ("Can I use the API from [country]?")

Questions about whether a specific country is supported follow a standard pattern.

**How to determine the answer:**
1. Check if there's a dedicated Help Centre in that country's language (e.g. `/hc/sv` for Sweden, `/hc/en-se` for English-language Swedish articles)
2. Check if the country's currency is listed as supported (quick_reference_cheatsheet.md has the currency list — SEK, DKK, NOK, PLN, CZK, HUF are common EU-based currency examples)
3. Search for a Smarkets licence announcement or help article for that country
4. If none of the above confirms: the answer is "I don't have jurisdiction information for that country — please contact support@smarkets.com to confirm"

**Sweden-specific shortcut:** Smarkets holds a Spelinspektionen licence, SEK is supported, and a Swedish Help Centre exists. Yes to all. Full detail in `references/sweden-jurisdiction.md`.

**Response principles:**
- Be clear about supported vs. speculative — if you found a licence announcement, say so. If you're guessing, don't.
- Differentiate between "can I open an account?" (jurisdiction question) and "can I use the API?" (same rules apply — API access follows account jurisdiction)
- COUNTRY_BLOCKED (451) is a separate, code-distinct issue from general eligibility questions. If they're getting 451, something is specifically blocked at the IP or account level — not a general policy question.
- **Always cite specific documented figures with their source.** When you mention a fee (e.g. £150 setup fee), commission rate, or any other concrete number, anchor it explicitly to the documented source — e.g. "GBP150 one-time setup fee (refundable within 60 days) — per API T&Cs, Section 3". Don't just repeat the number from memory or general knowledge. If the figure is in a reference file, say which one. This prevents the "plausible-sounding-number" trap and lets the customer verify independently.

### RG_ACK_REQUIRED — Responsible Gambling acknowledgement needed

This is one of the most common onboarding errors. Customer has API access approved but gets a 403 `RG_ACK_REQUIRED` when trying to place orders via `POST /v3/orders/`.

**What it means:** The account is approved for API use and has passed the setup/approval process. But the Responsible Gambling acknowledgement popup on the website has not been completed. This is a regulatory step Smarkets requires before any account can place bets (website or API).

.. warning:: The "one-time" characterisation is NOT accurate for all jurisdictions. For Swedish API users (and potentially others), the RG_ACK requirement resets with every new session/login, and even with session reuse only persists for approximately one hour. This makes API trading effectively impossible for affected users, as most API integrations create new sessions frequently. The standard advice ("log in and acknowledge the popup") does not resolve the issue for these users. See ``references/rg-ack-swedish-api-users.md`` for internal context. When responding to affected users: keep the response vague, do NOT mention session token reuse as a workaround (it only provides ~1 hour of trading), and do NOT reveal internal mechanics (session resets, compliance uncertainty). Use the holding response pattern (Pattern C) if waiting on a compliance decision.

.. warning:: **Persistent RG_ACK is a different scenario.** If the customer has already acknowledged the RG popup on the website but still receives ``RG_ACK_REQUIRED`` on every API order, the standard "log in and acknowledge" advice below is WRONG. See `Persistent RG_ACK (jurisdictional / session-based)`_ below. Do NOT repeat the standard guidance to a customer who has already acknowledged multiple times.

**Distinguish from other 403s:**
- `RG_ACK_REQUIRED` → API access IS active, just needs an RG checkbox ticked on the website
- `FORBIDDEN` (JSON, no specific code) → Account NOT yet approved for API, or still under the 60-day compliance review
- `FORBIDDEN` (HTML/Cloudflare) → Network-level edge block, not an account issue
- `KYC_PERMISSION_DENIED` → Identity not verified
- `NO_DEPOSITS` → No money deposited

**Response structure (standard — one-time RG_ACK):**
1. Confirm their API access is already active — the 403 is NOT about API approval
2. Explain ``RG_ACK_REQUIRED`` is the RG acknowledgement step, a regulatory requirement
3. Instruct: log in to smarkets.com, complete the RG acknowledgement popup/questionnaire
4. The block lifts immediately — no code changes needed
5. If they can't find the popup, suggest navigating to a market page which may trigger it

**Response structure (recurring RG_ACK — Swedish/affected jurisdictions):**
1. Confirm their API access is active — the error proves requests reach the trading engine
2. Confirm they haven't missed any settings or limits
3. Acknowledge this is a known and lasting limitation, not something they can troubleshoot
4. Explain the RG requirement is jurisdiction-specific (related to their country of residence)
5. Do NOT suggest session token reuse as a workaround
6. Do NOT reveal internal mechanics (session resets, 1-hour window, compliance uncertainty)
7. Set realistic expectations — no timeline, any change needs compliance review
8. If waiting on an internal decision, use the holding response pattern (Pattern C)

**Key nuance to avoid:** Don't tell them to submit the API Request Form or pay the setup fee again — they've already done that if they received this specific error code.

### Persistent RG_ACK (jurisdictional / session-based)

When a customer confirms they have acknowledged the RG popup on the website but STILL receives ``RG_ACK_REQUIRED`` on every API order attempt, this is a **known and lasting limitation**, not a troubleshooting gap on their end.

**Internal context (do NOT disclose to customer):**

- Every new login/session resets ``ack_required`` to ``true``
- Most API integrations create new sessions frequently rather than reusing tokens, triggering the reset each time
- Even with proper session reuse, the ack only persists for approximately one hour before a manual re-ack on the website is needed
- Whether the ack requirement can be removed for API users in specific jurisdictions (e.g. Sweden) is a compliance decision, not a technical one

**What NOT to tell the customer:**
- Do NOT suggest reusing a session token as a workaround (only buys ~1 hour, not a real solution)
- Do NOT reveal the session-reset mechanic or the 1-hour window
- Do NOT confirm or deny whether other users in their jurisdiction are affected
- Do NOT say "this is a one-time step" or "the block lifts immediately"

**Holding response pattern (when compliance decision is pending):**
When waiting on an internal compliance decision, use a holding response that:
#. Confirms API access IS active (the ``RG_ACK_REQUIRED`` error proves the request reached the trading engine)
#. Confirms they haven't missed any settings or limits
#. States you're actively looking into it with the team
#. Gives a vague timeline ("coming days") without revealing the compliance dependency
#. Does NOT promise a fix, just a "clearer update"

**Full honest response pattern (when a definitive answer is needed):**
#. Confirm API access is active, not an auth/approval issue
#. Confirm the RG acknowledgement is a regulatory requirement based on their jurisdiction
#. Acknowledge this is a known and lasting limitation of how RG interacts with API trading
#. Explain the website works because the ack is handled within the browser environment, but the API does not have an equivalent mechanism for maintaining that state (vague, do NOT mention session tokens)
#. State you can't provide a timeline, as any modification would need a compliance review
#. For "are other users affected?" — say RG requirements are jurisdiction-based, experience may differ by country. Do not confirm or deny.
#. Offer the website as the reliable alternative

See ``references/rg-ack-persistent-issue.md`` for the Swedish user case study with email drafts.

### "Is [Market X] Pre-Approved?" Queries

**Customer ask:** A potential API user wants to know if specific leagues/markets (e.g. table tennis TT Elite Series, Czech Liga Pro over/under) are on the pre-approved list before they apply.

**The answer is always:** The pre-approved list isn't published. It's determined per-account during the application process. Customers detail their intended markets in the API Request Form and Smarkets reviews and sets scope accordingly.

**How to handle it:**
1. State the pre-approved list is not published — it's set per-account during application
2. Confirm the use case (e.g. value betting on exchange markets) is standard and not excluded by T&Cs
3. Clarify fair usage governs *rate limits*, not market types or bet directions — the key restriction from Section 2 is "viewing market prices and placing bets ONLY"
4. Note post-approval scope changes can be discussed with api@smarkets.com
5. Recommend submitting the API Request Form with technical setup details

**Key distinction:** This is NOT a Pattern B (denial) query. The answer is "apply and find out" — direct them to the application process. The GBP150 fee is refundable within 60 days, which de-risks the decision.

### "Bots Are Not Allowed" — T&C Contradiction Claim

**Customer ask:** "Your T&Cs mention that bots are not allowed, but you provide the API for automated trading. Aren't these contradictory?"

**Answer:** No contradiction — the customer is conflating two different documents. See `references/bots-automated-trading-tc-clarification.md` for the full resolution with quoted clauses.

**Quick summary for the agent:**

1. **General Customer T&Cs clause 7.3.3** flags "robotic" betting (including bots) as a potential indicator of *suspicious betting* — but this applies to bets placed via the **website interface**, where betting is expected to be manual. It targets unauthorised automated access to the website, not approved API trading.
2. **General Customer T&Cs clause 6.19** acknowledges that "you may be betting against software applications such as bots or trading software" on the exchange — recognising bots as legitimate participants.
3. **API T&Cs Section 1** explicitly authorises automated trading: "Access to the API — and any automated interactions with our platform or services — is permitted only after you have completed our API Request Form."
4. **API T&Cs Section 7** lists grounds for suspension: data harvesting, fee avoidance, unfair trading (latency arbitrage, court-siding). "Using bots" is NOT listed.

**Key distinction:** An approved API user placing bets through the API IS placing bets "via their account" — just through the API rather than the website. This is the intended method, not a violation of 7.3.3.

**Response template** is in `references/bots-automated-trading-tc-clarification.md`. The full API T&Cs text is in `references/api-tcs-full-text.md` (retrieved via Jina reader — the help centre article 34697834941085 is Cloudflare-blocked).

**Pitfalls:**
- Don't say "bots are allowed" without qualification — the general T&Cs DO flag robotic betting as suspicious in the website context
- Don't quote 7.3.3 without explaining it applies to the website, not the API
- Always cite both documents (general Customer T&Cs + API T&Cs) — the API T&Cs Section 1 says the general T&Cs also apply, so you can't ignore either

### Fraud / Abuse Signals in API User Registrations

When reviewing suspicious API registrations, these non-API signals are relevant:

**User-Agent patterns:**
- If your official app sends a custom UA (e.g. `YourApp/1.2.3 CFNetwork/...`), then a bare `CFNetwork/version Darwin/version` means raw URLSession calls from a custom client, bypassing the official app
- Fraudsters automate against API endpoints directly using native networking libraries
- A fraudster using a residential proxy WILL use a realistic UA to pass superficial checks — the mismatch against your app's known UA is the signal

**IP escalation pattern (residential proxy → business VPN):**
- A user who registers from a residential proxy IP and, when challenged, switches to a business VPN is using evasion tactics, not verifying their identity
- Legitimate users verify from the same connection they registered from
- This sequence is a known fraud ring playbook — flag the user identity, not just the IP

**Registration from small-regional-ISP residential proxy pools:**
- BrightData, Oxylabs, IPRoyal lease /24 blocks from smaller ISPs
- Indicators: machine-generated PTR naming (repeated network prefix in hostname), rwhois address that's a residential house, no open ports on a live host, ProxyCheck `type: Business` despite `cpe` hostname label
- These IPs will pass all standard VPN/proxy detection checks — that's by design

### EV / P&L Display Questions

**⚠️ Important: Two distinct scenarios exist. Distinguish them carefully before responding.**

#### Scenario A: Old Smarkets Platform EV Display (Legacy UI)

**Customer context:** The customer has an **open position** on the Old Smarkets (legacy) exchange platform and sees "EV: +£X.XX" displayed next to it.

**Facts:**
- The Old Smarkets exchange platform **did** calculate and display EV on open positions. This was a native platform feature, not a third-party overlay.
- The EV appeared beside the customer's open position and was calculated based on the position's entry vs current market prices.
- A customer may describe the calculation as "weird" or "not right" because the displayed EV often didn't match their intuitive expectation.

**What to do:**
1. Acknowledge this was a platform feature — avoid categorically stating "Smarkets doesn't display EV", which contradicts their lived experience
2. Note that this was a legacy feature; the current SBK/Smarkets UI may behave differently
3. If the customer is asking *how* the EV was calculated: Smarkets' exact formula is undocumented in our workspace. The most common approach for exchange EV on an open position is: `EV = (implied_win_probability × potential_profit) + (implied_loss_probability × potential_loss)`, where implied probability comes from the current market price (not entry price). This can produce counter-intuitive results when the market has moved significantly
4. If the customer has specific numbers (entry price, current price, stake, displayed EV), offer to walk through the math to see if it reconciles
5. If you can't reconcile it and the customer needs the official answer, escalate to support@smarkets.com

**Pitfall to avoid:** Do NOT tell a customer who has an open position with an EV display that "Smarkets doesn't display EV" — this contradicts their lived experience and damages credibility. Always check first: "Are you seeing this on an open position you hold, in the website itself?"

#### Scenario B: Third-party Browser Extension/P&L Overlay

**Customer context:** The customer sees "P&L", "EV", or "Traded £X" figures overlaid on the market listing page (not on an open position) that don't match Smarkets' UI labels.

**What they're actually seeing vs what it is on Smarkets:**

| What they see | What it actually is on Smarkets |
|---|---|
| "Traded £34k" | Total matched volume across all outcomes in the market |
| "P&L £278.27 / -£399.66" | Best available **back** (£278) and **lay** (£399 liability) — Smarkets labels as "Back £X / Lay £Y", not P&L |
| "EV: +£18.75" | External tool's EV calculation, not from Smarkets market pages |

**Why the EV "doesn't seem right" (Scenario B):**

The third-party tool calculates EV using its own probability estimate. The gap between displayed EV and current traded price reflects the difference between the tool's probability model and the market-implied probability.

**Common tools that overlay on exchange pages:**
- OddsMonkey Toolbar (matched betting browser extension)
- RebelBetting / BettingHero (value betting services)
- Custom user scripts (Greasemonkey/Tampermonkey)
- Outplayed OddsMatcher (web-based tool, not a browser overlay)

**Response structure for Scenario B:**
1. Confirm Smarkets doesn't show EV/P&L on market pages — the figures are from a third-party tool
2. Explain what they're actually seeing (back/lay amounts labelled as P&L)
3. Explain why EV differs from traded prices (different probability estimates)
4. Ask which extension/tool they're using

**Pitfall to avoid for Scenario B:** Don't speculate about *how* the third-party tool calculates its EV — you don't have access to their probability model. Say: "The EV figure isn't from Smarkets. The gap is between the tool's probability estimate and the market-implied probability. For details on the tool's calculation, contact their support."

#### Quick Diagnosis: Scenario A vs Scenario B

| Question | Scenario A (Old Platform EV) | Scenario B (Third-party Overlay) |
|---|---|---|
| Where is it displayed? | Next to an **open position** the customer holds | Overlaid on the **market listing page** |
| Labels visible? | "EV: +£X.XX" alongside position info | "P&L £X / -£Y", "Traded £Z" near prices/volume |
| Customer question | "How is this EV calculated — it doesn't match my expectation?" | "Where is this EV/P&L figure coming from?" |
| Platform | Old Smarkets (legacy UI) | Either Old Smarkets or SBK |
| Your answer | This was a legacy platform feature | Third-party extension overlay |

### FOK / IOC order type confusion

Customers may ask about `time_in_force` or "Fill-or-Kill" orders, expecting a field they've seen on other exchanges. The Smarkets v3 REST API does **not** have a `time_in_force` field — FOK/IOC is handled through `type` + `minimum_accepted_quantity`.

**Common sources of the confusion:**
1. **Customer's own abstraction layer** — their code might use `time_in_force` internally and log it, but the raw HTTP payload uses `type` and `minimum_accepted_quantity`
2. **Crypto exchange crossover** — Binance, Bybit, Hyperliquid etc. use `timeInForce` as a standard field; customers mix up APIs
3. **Legacy v2 API docs** — the old Smarkets v2 REST API (long deprecated) may have used different schema names

**How to handle it:** Correct the assumption directly, then map the concept to the actual API fields. The response template in `references/fok-ioc-orders.md` has the exact wording and JSON examples.

**FOK =** `type: "immediate_or_cancel"` + `minimum_accepted_quantity` matching `quantity`
**IOC =** `type: "immediate_or_cancel"` + `minimum_accepted_quantity` lower than `quantity`
**Gotcha:** Always set `minimum_accepted_quantity` explicitly on `immediate_or_cancel` orders to control partial-fill behaviour. The spec doesn't document what happens when it's omitted — don't assume a default.

### Instant Match Voiding Complaints ("My in-play bet was voided")

Customers complain that their bet showed as matched/fully filled, then was voided. This is Instant Match working as designed — not a bug.

**How Instant Match works:** Bets are matched immediately (no delay), then enter a confirmation period of 8 or 14 seconds (stated on each event page). If the scouting feed flags a material event during this period, bets in pending are voided. This protects customers from those with faster feeds (Rule 8.3.4).

**Critical distinction — material events vs set-piece events:**
- **Material events** (goal, penalty, red card — Rule 12.8.1): halt market, extend pending, void bets if confirmed
- **Set-piece events** (corner, dangerous free-kick — Rule 12.8.2): extend pending only, do NOT halt market. Bets voided ONLY if the set-piece leads directly to a goal. If set-piece ends without a goal → bets confirmed.

**Rule 8.3.5:** Voids can happen even when no material event actually occurred (scout feed false positive). Smarkets will not reinstate. This is the rule that applies when a customer says "nothing happened" but their bet was voided.

**Drafting guidance for complaint responses:**
- Do NOT hedge or admit feed errors — if the rules support the void, state it confidently. A paragraph like "the feed may have been wrong but we won't reinstate" reads as both weak and cold.
- Do NOT share raw rule numbers unless quoting — the customer wants to know *why*, not the rule number. Quote the rule's substance with a link.
- Quote Rule 8.3.4 verbatim with a link to the help centre page — it does the heavy lifting ("protection against those with faster feeds").
- Use "8 or 14 seconds, as stated on the market page" — NOT "8-second" (Rule 10.5 says "eight-second" but 8.3.3 is more precise).
- Add a brief empathetic opener for complaint context (e.g. "I understand this can be frustrating") before the factual explanation — but don't over-soften.

Full rules, quotes, template email, and pitfalls at `references/instant-match-voiding.md`.

### Erroneous Bets / Outlier Ticket Audits

When auditing or composing a customer-facing ticket about clearly erroneous bets or outlier transactions:

1. **Determine complaint timing first** — Was the complaint within 60 minutes? This determines which threshold applies:
   - Within 60 min → Section 4 (±15% voiding threshold, Smarkets "reserves the right to void")
   - After 60 min → Section 3 (±20% outlier threshold, only available mechanism for late complaints)
   - If unknown, flag it — do not assume.
2. **Verify the calculation** — The policy works in "absolute difference in percentage price" (Section 1). Convert odds to percentage, subtract threshold in percentage points, convert back. See `references/clearly-erroneous-bets-policy.md` for worked examples.
3. **Check language accuracy** — Don't say "deemed to be an outlier" if the bet is within the 20% threshold. Say "deemed not to be an outlier" or "assessed under the outlier policy."
4. **Explain the calculation to the customer** — "20% of 3.4 was odds of 10.63" is opaque. Explain the percentage price conversion so the customer can verify the math independently.
5. **State the 60-minute context** — If the outlier threshold applies because the complaint was late, say so explicitly.
6. **Use ReST syntax from the first draft** — All ticket responses must use ReST formatting. Template: `templates/erroneous-bet-outlier-response.rst`. Reference: https://wiki.typo3.org/ReST_Syntax.

Full reference: `references/clearly-erroneous-bets-policy.md`

### Key URLs to Include
```
- API Base: https://api.smarkets.com
- Swagger Docs: https://docs.smarkets.com
- API Request Form: https://support.smarkets.com/p/6MLL-PL7/api-request-form
- Help Centre: https://help.smarkets.com/hc/en-gb
- API Support Email: api@smarkets.com
- Document Upload: https://docs.smarkets.com/
```
