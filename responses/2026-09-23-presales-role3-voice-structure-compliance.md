# Role 3 — Voice / Structure / Compliance check (council pass)
# Smarkets API presales draft — Betfair algo operator, ~£100k/month volume

**Compiled:** 2026-09-23
**Source audited:** the literal draft text recovered from the parent session (message id 183405, session 20260923_173901_c4949e71). Line and sentence references below are to the customer-facing part; the "Key doc references" block is internal (for Michael) and is not part of the sent reply.

**Method:** character-level scan of the literal text for em/en dashes, other non-ASCII, curly quotes, hyphen compounds, markdown tokens, banned phrases, forbidden routes and claims; sentence-by-sentence job test; negative-density count.

---

## 1. Mechanical token scan — all clean

| Check | Result |
|---|---|
| Em dashes / en dashes / any Unicode dash | 0 |
| Curly quotes (single or double) | 0 |
| Any non-ASCII character in the file | 0 (fully ASCII) |
| Hyphenated compound modifiers | 0. Only hyphen in customer text is inside the request-form URL (`6MLL-PL7`, `api-request-form`), which is intrinsic to the URL. `one time`, `60 day`, `market maker`, `preapproved` all correctly unhyphenated |
| Markdown (bold `**`, italic `*`, `__`, `#`, backticks, pipes/tables, links, quotes, `~~`) | 0 in customer text. Internal Key-doc block uses 8 plain `- ` bullets, no bold/italics |
| Banned softeners (`Unfortunately`, `I understand your frustration`, `good news`, `I'm sorry to say`, `the upside is`) | 0 |
| Banned phrases (`I can confirm that`, `do not hesitate to reach out`, `Please be advised`, `We have reviewed your request`, `Thanks for the detailed overview`, `Should you need further assistance`) | 0 |
| IBAS / eCOGRA / UKGC route | 0 |
| `api@smarkets.com` routing (or any api@ reroute) | 0 |
| Public / no-auth endpoint claim | 0 (word "public" absent) |
| Streaming / WebSocket / live-feed claim | 0 (no promise; no feed word used) |
| Wrong order default (`good_til_cancelled`) | 0. Order types not mentioned at all; the word "default" appears only for the 1200/60s rate limit |
| `amend` endpoint claim | 0 (correctly phrased as "changes handled by cancelling the open order and placing a new one") |
| Competitor names (Betfair etc.) | 0 |
| Semicolons, rhetorical questions, exclamation marks, apologies | 0 |
| Numbering of points | 0 (prose throughout, as Michael requested) |
| Sign-off | `Kind regards, / Smarkets Support` — matches required shape |

STAR order holds: one neutral acknowledge line that mirrors the customer's own term ("moving your algorithm"), then answers in his question order (apply, discovery/live data, place/amend/cancel, fees, market maker, limits). No paragraph over 4 sentences.

---

## 2. Line-level violations

**V1 — COMPLIANCE, MANDATORY (undocumented error claim).** P2: *"Trading is limited to preapproved events and markets for your account, so an order outside that scope will return an error, and use outside that scope including data extraction without matching trading volume or redistribution is not permitted."*
No out-of-scope error is documented anywhere (Role 1 verified: no scope-related code among the 92 live error codes). The promise "will return an error" is unverified behaviour. Delete the clause or reword to "may be rejected; the specific error is not published."

**V2 — COMPLIANCE, MANDATORY (Pro mechanic missing; speculative trailer).** P3: *"The Pro rate of 1% is available once you reach 80% of 1,500 bets or GBP1M staked in a month and contact support to opt in, so it would become relevant if your volume grows toward that level."*
The Commission FAQ charges Pro "per each individual matched bet that settles ... on the profit if it wins or the losses if it loses". Without that, "Pro rate of 1%" reads as a discount and is a later-complaint line at his volume. The trailer "if your volume grows toward that level" is also misleading: the 1,500-bet trigger counts all bets placed including unmatched and cancelled ones and is independent of stake size, so an algo at £100k/month may already cross it. Delete the trailer, add the loss-charging mechanic.

**V3 — VOICE, MINOR (blanket company statement).** P3: *"We do not offer reduced fees or market maker rates by access method, and API use does not change the tier."*
Approved shape is per-account: "The Market Maker commission tier isn't available for your account" (do not state a company-wide absence, do not explain the Swedish tier). Keep the adjacent Pro alternative; it is correctly paired.

**V4 — PRECISION, MINOR.** P3: *"the Standard rate of 2% on net winnings per market"* — Commission FAQ wording is "2% on net profits per market only". Use "net profit per market".

**V5 — PRECISION, MINOR.** P4: *"We preapprove call limits and repeated excess can lead to temporary suspension."*
T&Cs §5: exceeding preapproved call limits may lead to temporary suspension, and repeated violations could result in permanent revocation. As written it understates (first excess can trigger suspension) and "repeated excess" is awkward. Reword: "Exceeding your preapproved call limits can lead to temporary suspension."

**V6 — PASS WITH NOTE (live prices).** P2: *"retrieve live prices through the quotes and related price endpoints"* — "live" is accurate for an approved API user with a session token, and the sentence is conditioned on "Once approved", so it is compliant. But for a Betfair operator "live prices" can be read as a feed; recommend the word "polling" (e.g. "poll prices from the market quotes endpoint") to pre-empt the streaming assumption. No streaming claim is made, so this is a recommendation, not a violation.

**Internal block note:** the "Key doc references" block is for Michael only and must be stripped before the reply is sent; it contains "OpenAPI spec" wording that must never reach the customer.

---

## 3. Negative density

Patterns `will not / is not / cannot / not / never` in the customer text: **4 occurrences of "not"** (of which `is not` = 1), `will not` = 0, `cannot` = 0, `never` = 0.

1. P2: "...redistribution **is not** permitted."
2. P3: "We **do not** offer reduced fees or market maker rates by access method..."
3. P3: "API use **does not** change the tier."
4. P3: "API accounts are also **not** eligible for the 60 day 0% offer or affiliate offers."

Plus 1 "without" (P2, data extraction). At 331 words this is at the heuristic threshold (>3). Recommend reducing 4 to 2 by positive framing, keeping the two that carry material restrictions:
- #3 → "the same tiers apply to API and website trading" (positive; states the fact).
- #4 → "the 60 day 0% offer and affiliate offers are for website customers" (positive; states who has them).
- Keep #1 (scope restriction is material) and the V3 market maker decline (required flat line).

---

## 4. Sentences to delete or tighten

**Delete / reword:**
1. "so an order outside that scope will return an error" (V1 — undocumented).
2. "so it would become relevant if your volume grows toward that level" (V2 — speculative and wrong on the trigger basis).

**Tighten (long chained sentences; each split is a line edit, no rewrite):**
3. P2 S1 (48 words): *"Once approved you can discover events and markets through GET /v3/events/ and related market endpoints and retrieve live prices through the quotes and related price endpoints, and you can place and cancel orders programmatically with changes handled by cancelling the open order and placing a new one."* — and...and...and chain; also "related market endpoints" / "related price endpoints" are vague. Split into two sentences and name the paths: `GET /v3/events/`, `GET /v3/events/{event_ids}/markets/`, the market quotes endpoint.
4. P2 S2 (38 words): *"Trading is limited to preapproved events and markets for your account, so ... and use outside that scope including data extraction without matching trading volume or redistribution is not permitted."* — two distinct ideas (scope limit; prohibited uses) in one sentence. Split.
5. P1 S3 (34 words): *"We review each application against exchange health guidelines and you will need to share details of your technical setup and intended interaction, with a compliance review of your account within the first 60 days."* — split the review and the requirement.
6. P4 S2: "We preapprove call limits and repeated excess can lead to temporary suspension." — see V5.

**Keep:** the acknowledge line (one line, mirrors his term), "On limits," as the topic opener, and the P3 fee sentences other than the fixes above — each does fact/decision work.

---

## 5. Grade

**MINOR FIXES.** The voice/structure layer is mechanically clean: no banned tokens, no em dashes, no hyphen compounds, straight ASCII only, no markdown in the customer text, no IBAS or api@ routing, no public/no-auth or streaming claims, no wrong order default, prose and sign-off correct. No rewrite needed.

Ready to send only after the two mandatory line edits:
- V1 delete/reword the out-of-scope error promise.
- V2 add the Pro loss-charging mechanic and delete the "grows toward that level" trailer.

V3, V4, V5 and the three sentence splits are recommended one-line edits; the negative-density reduction (4 → 2) is recommended.
