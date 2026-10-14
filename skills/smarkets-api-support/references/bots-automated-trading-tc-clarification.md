# "Bots Are Not Allowed" vs "API for Automated Trading" — T&C Clarification

**Customer question:** "Your T&Cs mention that bots are not allowed, but you provide the API for automated trading, which is what I need it for. Those two statements contradict. What is the case?"

**Retrieved:** July 2026. API T&Cs via Jina reader (Cloudflare-blocked). General Customer T&Cs clauses via Jina reader.

---

## Answer: No Contradiction

The customer is conflating two different documents. The general Customer T&Cs flag robotic betting on the **website** as suspicious; the API T&Cs explicitly provide the **authorised channel** for automated trading. They work together.

---

## The Three Key Clauses

### 1. General Customer T&Cs — Clause 7.3.3 (Suspicious Betting)

> "where we have reasonable grounds to suspect that a bet or a string of connected bets were placed robotically (including, but not limited to, use of bots) or by any other means other than the account holder placing each bet manually via their account"

**Context:** This is under Section 7.3 "Suspicious Betting" in the general Customer T&Cs (article 213469085). It applies to bets placed via the **website interface**, where betting is expected to be manual. It targets unauthorised automated access to the website — not approved API trading.

**Critical phrase:** "other than the account holder placing each bet manually via their account." An approved API user IS placing bets via their account — through the API, which is the authorised method.

### 2. General Customer T&Cs — Clause 6.19 (Acknowledgment of Bots)

> "When placing a bet, you are aware that you may be betting against software applications such as bots or trading software."

**Context:** This acknowledges that bots and trading software are legitimate participants on the exchange. The general T&Cs recognise their existence — they don't ban them outright.

### 3. API T&Cs — Section 1 (Explicit Authorisation of Automated Trading)

> "Access to the API — and any automated interactions with our platform or services — is permitted only after you have completed our API Request Form, undergone the authorisation process, and received our explicit approval."

**Context:** The API T&Cs (article 34697834941085) explicitly authorise automated interactions after the approval process. Automated trading is the **intended purpose** of the API, not an exception to a ban.

### 4. API T&Cs — Section 7 (Grounds for Suspension)

Lists three specific grounds: data harvesting, fee avoidance, unfair trading (latency arbitrage, court-siding). **"Using bots" is NOT listed** — because automated trading via an approved API account is the product's purpose.

---

## Response Template (ReST)

> That's not quite right — there's no contradiction, and the T&Cs don't say bots are not allowed. Two different documents are being conflated here.
>
> The general Customer Terms and Conditions (clause 7.3.3) list "robotic" betting, including the use of bots, as a potential indicator of *suspicious betting* — but this clause is about bets placed via the website interface, where betting is expected to be manual. The full wording refers to bets placed "by any other means other than the account holder placing each bet manually via their account." It's targeting unauthorised automated access to the website, not approved API trading.
>
> The same general T&Cs also acknowledge in clause 6.19 that "you may be betting against software applications such as bots or trading software" on the exchange — so bots are recognised as legitimate participants.
>
> The API Terms and Conditions (Section 1) are the document that governs your API access. They explicitly state: "Access to the API — and any automated interactions with our platform or services — is permitted only after you have completed our API Request Form, undergone the authorisation process, and received our explicit approval." Automated trading is the *intended purpose* of the API, not an exception to a ban.
>
> Section 2 of the API T&Cs defines what the API is for: "viewing market prices and placing bets." The prohibited uses listed are specific — odds scraping, concealing API calls, browser impersonation, reverse engineering. Section 7 lists grounds for suspension: data harvesting (requesting prices without corresponding bet volumes), fee avoidance (multiple accounts), and unfair trading (latency arbitrage, court-siding). "Using bots" is not listed, because automated trading via an approved API account is exactly what the product is for.
>
> In short: the general T&Cs prohibit *unauthorised* robotic betting on the website. The API T&Cs provide the *authorised* channel for automated trading. They work together — they don't contradict each other.

---

## Pitfalls

- **Don't say "bots are allowed" without qualification** — the general T&Cs DO flag robotic betting as suspicious in the website context (7.3.3). The nuance is that the API provides the authorised channel.
- **Don't quote 7.3.3 without explaining it applies to the website, not the API** — quoting the clause alone makes it sound like a blanket ban.
- **Always cite both documents** (general Customer T&Cs + API T&Cs) to show they work together. The API T&Cs Section 1 explicitly says the general Customer T&Cs also apply — so you can't ignore either document.
- **Don't conflate "automated trading" with "latency arbitrage" or "court-siding"** — the API T&Cs Section 7 prohibits the latter two specifically. Automated trading in general is permitted; latency arbitrage and court-siding are not.
- **The general Customer T&Cs article (213469085) is also Cloudflare-blocked** — use the Jina reader to access it: ``curl -sL "https://r.jina.ai/https://help.smarkets.com/hc/en-gb/articles/213469085-Smarkets-Terms-and-Conditions"``
