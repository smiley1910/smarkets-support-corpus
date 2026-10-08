# 2026-09-24 — WebSocket + matched volume ticket: evidence brief (internal, for council roles)

## Customer email (verbatim)

Hi Smarkets Support,
I recently purchased access to your v3 REST API for use in a liquidity monitoring application that compares real-time matched volume across betting exchanges.
After extensive testing I cannot find any endpoint in the v3 REST API that returns matched/traded volume figures for markets or contracts. Specifically:
* /events/{id}/states/ returns lifecycle state only (no volume field)
* /markets/{id}/states/ returns market state only (no volume field)
* /markets/{id}/trades/ returns 404
* wss://api.smarkets.com/v3/ws/ returns 404
Could you please confirm:
1. Is matched volume (total traded) accessible anywhere in the v3 public REST API?
2. Is the streaming WebSocket API available at any endpoint for standard API subscribers, and if so what is the correct URL and auth method?
3. If neither is available at the standard tier, what subscription level provides access to real-time matched volume?
If matched volume and/or streaming data is not included in the standard API subscription, I would like to discuss whether my subscription is fit for purpose given my use case, as this was the primary reason I purchased access.

## Context from Michael

The user "looks to be misusing or angling for websocket which is not offered". Task: audit the query, then a council of 3 reviews the response. The user's described purpose (a liquidity monitoring app that compares matched volume across betting exchanges) is a monitoring/comparison use, not trading.

## Verified facts (all checked 2026-09-24)

1. **Live OpenAPI spec** (fetched from https://api.smarkets.com/v0/control/openapi/?tags=trading_api, saved at /tmp/live_spec_20260924.json): 18 paths total. `/v3/markets/{market_ids}/volumes/` IS present. Zero occurrences of websocket / wss / streaming / socket / trades anywhere in the document.
2. **Live probes** (unauthenticated GET, 2026-09-24 ~13:00 UTC):
   - `GET /v3/markets/165905519/volumes/` -> 200, body `{"volumes": [{"double_stake_volume": 82, "market_id": "165905519", "volume": 89}]}`. Spec text: volume = "traded volume measured in GBP... sum of back stake (on the back side) with liability (on the lay side)... This is the volume displayed in our website."; double_stake_volume = "twice back stake for every execution". Up to 300 market ids per request.
   - `GET /v3/markets/165905519/last_executed_prices/` -> 200 (last executed price + timestamp per contract).
   - `GET /v3/markets/165905519/states/` -> 404 NOT_FOUND "Nothing matches the given URI". `/v3/markets/165905519/state/` and `/v3/markets/states/` also 404. There is no markets states route.
   - `GET /v3/markets/165905519/trades/` -> 404 NOT_FOUND.
   - `GET /v3/events/45333523/states/` -> 200 (event_states: lifecycle/clock data; no volume).
   - `GET /v3/ws/` -> 404 NOT_FOUND.
3. **Market state** is a field on market objects from `GET /v3/events/{event_ids}/markets/` (values: new/open/live/halted/settled/voided/unavailable).
4. **No websocket/streaming for the API**: REST only. Approved scoped denial wording (skill reference `deprecated-streaming-api-and-sio-live.md` line 85): "We don't offer websockets or a streaming feed. The API is REST only, so there is no websocket interface to connect to." NEVER claim no websocket exists anywhere at Smarkets (the website frontend uses one — do not mention it). Do not mention the archived SDK or sio-live.
5. **No subscription levels**: no recurring or subscription API fee is documented. One-time £150 setup fee (T&Cs Section 3); Section 5 carries a caveat that usage "may be subject to specific restrictions and/or incur additional fees". No level of access includes streaming.
6. **T&Cs quotes** (canonical source: `~/.hermes/skills/process/smarkets-api-support/references/api-tcs-full-text.md`, mirrored at `~/smarkets-api-support/scrape-aug18/help/api-tcs.md`):
   - Section 2: "The API is designed to allow authorised users to view market prices and place bets on their Smarkets account. All other uses are strictly prohibited..."
   - Section 5: "Additionally, usage of the API or its data to benchmark markets, prices, liquidity or systems is not permitted."
   - Section 6.1 (prohibited list): "Use the API strictly for data extraction purposes without commensurate trading volumes"; "Monitor or benchmark our services for competitive purposes."
   - Section 7 (grounds for suspension): "Data Harvesting: Requesting high volumes of pricing data without placing a corresponding volume of bets. Our real time odds are proprietary - using the API solely to monitor markets violates this"
   - Section 3: "A one-time administrative setup fee of £150, or account currency equivalent... Should you choose to permanently withdraw from API usage within the first 60 days, your setup fee will be refunded."
7. **Precedent notes**:
   - `responses/api-scope-confirmation.txt` Q8: cross-exchange ARBITRAGE — "isn't explicitly prohibited" but the benchmarking overlap was deferred for review. DISTINCTION: this ticket is a monitoring/comparison tool (no trading described), which Section 5 (liquidity explicitly named), Section 6.1 and Section 7 hit directly. Approved training FAQ: "Can I use the API to benchmark Smarkets against other exchanges?" -> "No."
   - 2026-09-16 websocket denial precedent: `responses/2026-09-16-websocket-and-ratelimits-v4-FINAL.txt`.
   - Refund offering precedent: skill guidance for unsupported use cases (rate-limit denial) — offer Section 3 refund, neutral framing, not admission of fault; outside 60 days the clause does not apply.

## Hard constraints for the customer text

- Plain text only; straight quotes; no em dashes; no hyphenated compound modifiers (write "real time"); no markdown; contractions are good.
- Scoped websocket denial; no blanket "no websocket anywhere"; no sio-live/SDK references; no "public/no-auth" claims; no api@smarkets.com rerouting; no competitor names; no "OpenAPI/spec/schema" wording.
- Voice-core rules: STAR; no banned softeners ("Unfortunately", "I understand", "good news", "the upside is"); no "additionally"/"furthermore"; decision/facts first; check negative density; sign-off "Kind regards, / [name] / Smarkets Support".
- The response must: answer Q1 (volume IS available — volumes endpoint), Q2 (no websocket; REST only; no URL/auth to give), Q3 (no levels; nothing unlocks streaming), flag the use restrictions (Section 5 benchmarking / 6.1 / 7), and handle the fit-for-purpose ask (neutral Section 3 refund path).

## Draft under review

File: `~/smarkets-api-support/responses/2026-09-24-websocket-volume-draft-v1.txt`

---
Hi [name],

Thanks for your email. I've checked the endpoints you tested.

Matched volume is available through the API. GET /v3/markets/{market_ids}/volumes/ returns the traded volume for each market you request, measured in GBP and calculated as the back stake on the back side plus the liability on the lay side. That is the same volume figure shown on the Smarkets website. The last traded price for each contract, with its execution timestamp, comes from GET /v3/markets/{market_ids}/last_executed_prices/. The endpoints you tried are not where this data sits: the events states endpoint returns lifecycle state only, and there is no markets states endpoint or trades endpoint, so those requests return 404.

The API is REST only. We don't offer websockets or a streaming feed, so there is no websocket URL or authentication method for one, and no level of access includes a streaming feed. Price and volume updates are retrieved by polling the endpoints above, within your rate limits.

I should also be clear about the scope of the access. The API is provided for viewing market prices and placing bets on your Smarkets account. Section 5 of the API terms states: "usage of the API or its data to benchmark markets, prices, liquidity or systems is not permitted." The fair usage terms treat using the API solely to monitor markets as a breach of the terms. A tool that compares our liquidity against other exchanges falls within those restrictions, so it is not a use the access permits.

If the access is not a fit for your purposes, under Section 3 your setup fee will be refunded if you permanently withdraw from API usage within the first 60 days. If you'd like to discuss this further, reply to this email.

Kind regards,
[name]
Smarkets Support
---

## Note for reviewers

This brief is a map, not gospel. Independently re-check the load-bearing claims against the source files above (and live probes where useful) before grading. Report any disagreement with the brief explicitly.
