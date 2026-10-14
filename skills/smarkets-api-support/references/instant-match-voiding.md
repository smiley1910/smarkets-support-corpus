# Instant Match Voiding — Rules, Complaint Responses & Pitfalls

> **Source:** Smarkets General Betting Rules (1-11), Rule 8.3 (Instant Match);
> Football Rules (Rule 12), Section 12.8 (Instant Match).
> Help Centre articles: Instant Match, General Rules, Football Rules.
> All quotes verbatim from scraped help pages (June 2026).

## The Mechanism — How Instant Match Works

Instant Match is Smarkets' system for in-play football (and other scouted events).
Unlike delayed in-play markets (4s horse racing/darts, 8s everything else),
Instant Match matches bets **immediately** with no delay, then subjects the
matched bet to a **confirmation period**.

**Rule 8.3.3:**
> "Once matched, an executed bet will be subject to a confirmation period of
> between 8 and 14 seconds, as stated on the market. Bets which are subject to
> confirmation will be in a 'Pending' state on the bet slip. Once the bet is out
> of its pending period and is confirmed, this will be recorded on your account
> statement."

**Rule 8.3.4:**
> "At the point in time a bet is matched, the price of the execution is fixed.
> In most cases such a bet will be subsequently confirmed after the pending
> period has elapsed, but if we receive information about a significant event in
> the match during this period (see sport specific rules for details) we will
> void this execution to give customers protection against those with faster
> feeds and advantageous information."

**Key point:** The bet IS matched — it's a confirmed P2P transaction. The
voiding happens retroactively during the confirmation period. This is not a bug;
it's the design of Instant Match.

## Material Events vs Set-Piece Events — Critical Distinction

### Material Events (Rule 12.8.1)
> "For the purposes of football, we deem a material event to be one of: goal,
> penalty, red card."

**Rule 12.8.4:** If data indicates a material event is **potentially** occurring
(possible goal, possible penalty, possible red card), markets are halted and
the pending confirmation period is extended for all bets in pending state.

**Rule 12.8.4.2:** If subsequent data confirms the event **did** happen →
markets resume, bets in pending are **voided**.

**Rule 12.8.4.1:** If subsequent data confirms the event **did not** happen →
markets resume, bets in pending are **confirmed**.

### Set-Piece Events (Rule 12.8.2)
> "For the purposes of football, we deem a set-piece event to be either a corner
> or a free-kick deemed dangerous by our data feed."

**Rule 12.8.5:** If data indicates a significant set-piece is occurring (corner
kick, free-kick in a dangerous pitch zone), the pending confirmation period is
extended, **but markets are NOT halted**.

**Rule 12.8.6.1:** If the set-piece ends without a goal (defending team regains
possession, ball goes safe, other non-goal event) → bets are **confirmed**.

**Rule 12.8.6.2:** If the set-piece leads **directly** to a goal → bets are
**voided** (but this is the goal/material event triggering the void, not the
set-piece itself).

### ⚠️ Common Error: "Set-piece events void bets"

**FALSE.** Set-piece events only EXTEND the confirmation period. They do not
void. Only a confirmed material event (goal, penalty, red card) voids bets. A
set-piece that ends without a goal results in confirmation. This distinction
matters for accurate customer responses.

### VAR Reviews (Rule 12.8.7)
Same pattern as material events: halt + extend pending. If the decision is
confirmed → void. If reversed → resume and unsettle any determined markets.

## Rule 8.3.5 — Voids When No Material Event Occurred

**Rule 8.3.5:**
> "The system relies on external data fed by scouts at the ground. This means
> that in rare cases, material events may be missed or executions may be voided
> when a material event does not occur. In these cases, we reserve the right to
> void bets where an unfair advantage was gained in accordance with rule 8.1.5.
> We will not reinstate already voided bets, so it is important to make sure
> your bet is confirmed."

This rule covers the scenario where the scout feed flags something that didn't
actually happen — a false positive. The bet is still voided, and Smarkets will
not reinstate. This is the rule that applies when a customer says "nothing
happened in the match" but their bet was voided.

## Rule 10.5 — Keep Bets In-Play + Material Events

> "If your bet is matched in-play and a material event occurs during the
> eight-second confirmation period, the bet will be voided and therefore will
> not remain when the market reopens."

Note: Rule 10.5 says "eight-second" but Rule 8.3.3 says "between 8 and 14
seconds." The Instant Match help page clarifies: "either 8 or 14 seconds and
this is stated at the top of the event page once the event is live." Always use
"8 or 14 seconds" in customer communications — it's the more precise and
authoritative figure.

## Drafting Complaint Responses — Pitfalls & Guidance

### Pitfall 1: Don't hedge or admit feed errors

If the rules support the void, state it confidently. Do NOT include paragraphs
like:

> ❌ "The system relies on live data fed by scouts at the ground, and in some
> cases a potential event may be flagged that does not ultimately result in a
> confirmed material event. However, per rule 8.3.5, we reserve the right to
> void bets in these circumstances and will not reinstate already voided bets."

This reads as "we might have got it wrong but tough luck" — it undermines the
position and sounds both weak and cold. The verbatim rules quote (8.3.4) does
the heavy lifting. Let it. Don't undermine it with a qualifier.

### Pitfall 2: Don't share raw rule numbers with customers

Rule 8.3.5 is written for internal use. Sharing it with a complaining customer
feels like "we're hiding behind policy." The customer wants to know *why it
happened*, not the rule number. Quote the rule's substance in plain English with
a link to the help centre page.

### Pitfall 3: Don't distinguish material vs set-piece events unless asked

For a standard "my bet was voided" complaint, just say "a material event was
flagged during the confirmation period." Don't volunteer the set-piece
distinction — it adds complexity without helping the customer. Only go into
set-piece detail if the customer specifically asks about corners/free-kicks.

### Pitfall 4: Confirmation period wording

Always say "8 or 14 seconds, as stated on the market page" — NOT "8-second" and
NOT "8-14 seconds." Rule 8.3.3 says "between 8 and 14 seconds, as stated on the
market." The Instant Match help page says "either 8 or 14 seconds." The specific
duration is shown on each event page.

### Recommended Email Structure

```
1. Acknowledge + state what happened (bet voided, material event flagged
   during confirmation period)
2. Explain the mechanism (Instant Match matches immediately, then 8 or 14
   second confirmation period)
3. Quote Rule 8.3.4 verbatim with link (protection against faster feeds)
4. State stake returned
5. Close warmly
```

### Template

> Thank you for your email.
>
> After checking your bet, I can see that it was voided as our data feed flagged
> a potential material event during the confirmation period.
>
> Under our [Instant Match rules](https://help.smarkets.com/hc/en-gb/articles/212106249-Instant-Match),
> in-play bets are matched immediately and then enter a confirmation period of
> 8 or 14 seconds, as stated on the market page. During this period, if our
> scouting feed flags a material event (defined in our
> [football rules](https://help.smarkets.com/hc/en-gb/articles/210005425-12-Football-rules)
> as a goal, penalty, or red card), bets in the pending state are voided.
>
> As stated in our [general betting rules (8.3.4)](https://help.smarkets.com/hc/en-gb/articles/212183509-1-11-General-Smarkets-betting-rules):
>
> > "If we receive information about a significant event in the match during
> > this period, we will void this execution to give customers protection
> > against those with faster feeds and advantageous information."
>
> Your stake has been returned to your account. Should you need any further
> assistance, do not hesitate to reach out.

## Help Centre Links

- Instant Match: https://help.smarkets.com/hc/en-gb/articles/212106249
- General Betting Rules (1-11): https://help.smarkets.com/hc/en-gb/articles/212183509
- Football Rules (12): https://help.smarkets.com/hc/en-gb/articles/210005425

## RAG Context Correction

The RAG context file at `~/smarkets-api-support/rag-context/betting-rules.md`
contains an oversimplification in the In-Play Betting (Rule 8) section:

> "Instant Match: No betting delay; 8-14 second confirmation period; bet can be
> voided if material event occurs during confirmation"

This is incomplete:
1. Does not distinguish material events (void) from set-piece events (extend
   only — void only if set-piece leads to goal)
2. Does not mention Rule 8.3.5 (voids when no material event occurred)
3. Does not mention that the specific duration (8 or 14 seconds) is stated on
   each event page

The RAG context should be updated to reflect the distinction. This reference
file serves as the authoritative correction.
