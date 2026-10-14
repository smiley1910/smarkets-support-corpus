# Customer-Claim-by-Claim Rebuttal Map

For decline and partial-decline tickets, produce a separate point-by-point rebuttal map that Michael can sense-check before the customer-facing email goes out.

## When to use

- Refund denied
- Credit denied (further credit on top of a prior credit)
- Settlement upheld
- Complaint rejected
- Any ticket where Michael wants to verify every customer ask was considered before sending

Simple one-line answers (password reset, login troubleshooting, single-fact verification) do NOT need a rebuttal map. The rebuttal map is for contested cases.

## Why it exists

Per Michael, 7 Aug 2026 (Cerezo Osaka decline ticket): "can you highlight each point in his email and the rebuttal so i can be sure to sense check before sending."

The rebuttal map serves three purposes:

1. **Sense-check** — Michael can read the customer email and the rebuttal side-by-side and confirm nothing was missed.
2. **Deliberate-non-response visibility** — the map spells out which parts of the customer's email the draft DELIBERATELY does NOT respond to (e.g. "I match bet full time", "this is very incompetent", "Please do what's right"). Without this list, Michael may "fix" the gaps on the next pass and accidentally re-introduce material that should stay unsaid.
3. **Risks surface** — figures not explicitly named, rule attributions that could be contradicted, framing risks. Michael catches these in the rebuttal map review before they hit the customer.

## What the map must contain

### 1. Real mapping section (when applicable)

For void/unvoid, multi-set, or sequence-based cases, lay out the operational mapping in plain language at the top, BEFORE walking through the customer points. Example shape (Cerezo Osaka 7 Aug 2026):

```
- 1st set of lays (pre-chat, the two bet IDs the customer names):
    Bet 203590086076350473: £359.87 liability
    Bet 203590086253387785: £599.79 liability
    Total: £959.66
    Status: voided then SETTLED ON THE RESULT. Stand as settled.
    NOT covered by the prior credit.

- 2nd set of lays (post-chat, voided then unvoided by Smarkets):
    These were the bets CORRECTED by the prior ~£700 credit
    under Rule 4.6 (reversal of the void).

- 3rd set of lays: on a different exchange. Not our transaction.
```

This lets Michael see the structure of the case before wading through the point-by-point.

### 2. Per-point rebuttal

For each numbered customer point:

```
================================================================
CUSTOMER POINT N — "<quote or paraphrase of the customer point>"
================================================================

REBUTTAL: <paragraph number(s)> of the draft.

"<exact quote of the relevant draft paragraph(s)>"

REASONING:
- What the customer actually asked / claimed.
- What the position is and why (which rule, which fact, which decision).
- Any nuance worth flagging to Michael.
```

### 3. Deliberate non-responses

A separate section listing parts of the customer email the draft does NOT address, with a one-line reason for each. Common categories:

- Customer identifying as a matched bettor (don't moralise)
- Customer's emotional characterisation ("incompetent", "ridiculous", "agents who are telling me the wrong thing") (one apology covers it, don't accept the characterisation)
- Customer's closing appeal ("Please do what's right") (the position is the answer)
- Customer's re-framing of an internal fact (e.g. "the prior credit was goodwill" when it was actually Rule 4.6 correction) (quietly correct in the draft, don't confront)
- Threats (UKGC, IBAS, social media) (do not engage, do not pre-empt with a route)

### 4. Quick sense-check table

```
Customer asks for:                  Draft response:
  £959.66 top-up                  : Para 2: settlement stands,
                                     prior credit addressed.
  Credit all void/unvoid bets      : Para 3: same reasoning,
                                     prior credit addressed overall.
  ...
```

### 5. Risks / things-to-double-check

Numbered list of things Michael should confirm before sending. Common entries:

- Figures not explicitly named in the draft that the customer expects to see (e.g. "the £959.66 figure is implied but not named — confirm whether to add a one-liner").
- Rule attribution that could contradict prior customer-facing communication (e.g. "if the prior credit was framed to the customer as goodwill at the time, this recharacterisation contradicts it").
- ADR routing questions (do we offer IBAS here? See "Do NOT proactively offer the complaints process" in SKILL.md).
- The customer's loaded word (e.g. "unvoided") deliberately avoided in the draft — confirm we're aligned on the avoidance.
- Any soft inferences (e.g. "the customer probably already had a £700 credit — we're inferring this from his email, not from account data — confirm before stating it as fact").

## File naming and location

Save in `~/smarkets-api-support/responses/` alongside the draft:

- Customer-facing draft: `customer-email-YYYY-MM-DD-<topic>-DRAFT.txt`
- Rebuttal map: `customer-email-YYYY-MM-DD-<topic>-REBUTTAL-MAP.md`

The rebuttal map is for Michael's eyes, NOT the customer's. It can use whatever layout makes the mapping easy to scan — tables, sections, block quotes, full prose. It does not need to follow the customer-facing voice rules.

## Pitfalls

- **Do not skip the deliberate-non-responses section.** It's the most valuable part of the map for Michael's review. Without it, the map looks incomplete and Michael will read through the draft looking for what was missed.
- **Do not include unverified inferences as facts in the map's reasoning section.** If the position depends on an inference, label it as inference and flag for confirmation.
- **Do not write the map in the customer-facing voice.** "I appreciate the inconsistency" is for the customer. The map is internal correspondence with Michael.
- **Do not update the map after Michael reviews it unless he asks.** The map is a snapshot of "here's what the draft does and doesn't do" at the point of review. If the draft changes, regenerate the map. Don't try to keep both in sync.
