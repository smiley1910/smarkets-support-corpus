# Standard Product Tickets (SBK, Smarkets Exchange, Account)

Application module of `process:smarkets-ticket-writer`. Universal voice,
structure, length and style gates live in `process:smarkets-voice-core` and
are not restated here. If this file ever seems to contradict voice-core,
voice-core wins.

Absorbs (with gate corrections): `sbk-promo-eligibility.md`,
`sbk-promo-ineligible-template.md`, `promo-ineligibility-exchange-template.md`,
`kind-template-direct-context.md`, `kind-template-no-appeasement.md`,
`voice-kind-vs-appeasement.md`, `template-tone-and-commission-tiers.md`,
`sow-sof-verified-facts.md`, `deposit-limit-increase-decline.md`, and the
product sections of `ticket-scenarios-and-examples.md`. Originals removed
after merge; verbatim history stays in the skill backup.

Canonical reusable customer templates live in
`~/smarkets-api-support/templates/` (for example
`sbk-promo-ineligible-exchange-template.md` and
`smarkets-final-response-steve-style.md`). This skill carries no template
copies, only pointers.

## SBK versus Smarkets routing

Determine the product before drafting. Exchange signals are lay, back,
liability, matched or unmatched, commission. Sportsbook signals are SBK app,
accumulator, Bet Builder. API signals are session token, endpoint, POST
paths. SBK and Smarkets are separate products with separate balances and
separate terms; clause numbers differ between them.

## Promo ineligibility (kind means direct with context)

Position in sentence one: the promo is for SBK customers and the account is
on the exchange. Follow with the mechanism (sportsbook where Smarkets sets
the odds, exchange as a separate product with its own balance, promotion
terms do not extend to it). State what they do have as flat fact: bet
against other users, generally better odds, back or lay, trade out, and
commission mechanics only as verified for their tier. Close in one line
("If you have any questions about the exchange, just reply here"). No
softeners, no reassurance lines, no pivot theatre, no apology, no complaints
route unless asked. If the customer pushes back, quote the specific promo
eligibility clause verbatim (welcome bonus clause 14, SB10K clause 22).

## Commission tiers

Check the customer's tier before stating commission mechanics in any draft.
Standard is 2% on net profit per market with nothing on losses. Pro charges
on profit and loss per matched bet. Select differs again, and new accounts
may carry an introductory 0% offer. Where the tier is unknown, hedge ("at
2% on most accounts") or drop the claim.

## Source of wealth and source of funds

Clauses 2.17 (identity and residency) and 2.18 (source of funds and wealth
where required by law or regulators) are the anchors. Never state a review
trigger; the docs say not all customers go through the process and give no
thresholds. The 24 hour aim covers ID and residency verification only; SoW
has no documented SLA. Restriction escalation runs deposit block, then bet
block, then temporary suspension. Never suggest contacting an employer.
Failure to provide requested material may suspend functionality including
withdrawals or close the account.

## Bet cancellation

SBK bets stand once placed. Clearly erroneous covers price only (placed
outside a set band around fair market price), not stake. Face ID is explicit
confirmation of stake and details before submission. On the exchange only
unmatched or partially matched portions can cancel; matched bets stand and
must be traded out. Standard window and evidence requirements apply; quote
them from the help article, not from memory.

## Payments

Closed loop returns carry the "wherever possible" qualifier at Smarkets
discretion, never as an absolute. Add the five working day attempt window
and the verification gate where relevant.

## Hacked account final response

Thank patience, apologise once for the delay in providing the final
response, introduce the independent review, summarise the customer position
in their own terms, then state the position is unchanged. Build a date
anchored chronology from verified account facts only (sign in, payment
method change, deposit, bets placed while logged in with valid credentials).
Apply the operative credential rules verbatim and tie each secondary ask to
its own paragraph stating what was checked at outcome level plus what the
platform cannot do (with the correct external route where one exists).
Acknowledge account praise briefly. ADR block only for a final position on
a filed complaint (voice-core section 5).

## Deposit limit increase decline

Answer the actual question with position plus reason first: the monthly
limit is system assigned in line with regulatory requirements and Smarkets
is not in a position to raise it. Rebut the daily figure flatly: the daily
limit is self set, it neither sets nor influences the monthly cap, and the
lower cap binds. Use soft negation, never "refuse" or "denied". No
complaints route. Offer the proof of income door only if Michael wants it
open; default is omit. If the real reason is an affordability outcome rather
than the system cap, swap the first sentence.

## Regulatory exit

Neutral framing throughout: the account cannot currently be given the level
of service wanted, the decision is case by case. Never blame the regulator
and never admit product fault. Follow with logistics (dates, unaffected
account and funds, open positions, fee refund) and a wind down contact.

## Login and connection issues

Both troubleshooting articles list VPN or proxy as a cause; hedge as
inference about what the connection looks like from our end. Give device
specific steps, acknowledge the customer may not run a VPN themselves, and
offer further investigation. Never cite account terms in a troubleshooting
reply.
