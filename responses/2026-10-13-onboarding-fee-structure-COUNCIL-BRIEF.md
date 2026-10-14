# 2026-10-13 — API onboarding user / fee structure (commission tiers): council brief

Three independent reviewers verify ONE customer-facing Smarkets support draft before
it is presented to Michael. The brief is a map, not gospel: re-verify its claims
against primary sources and report disagreement explicitly. Do not rewrite the
draft wholesale; list minimal, specific fixes with exact wording.

Draft under review:
`/Users/michaelsmyth1/smarkets-api-support/responses/2026-10-13-onboarding-fee-structure-draft-v1.txt`

## What this email is

Reply to a user who is in onboarding ("before getting started") and has asked two
fee-structure questions: (1) confirm commission is standardly 2% on net winnings
per market; (2) whether volume-tiered or reduced commission tiers apply at their
stated £100,000 per month turnover. Info-class response: no account verification
available, so the draft must state policy/defaults only and make no claims about
this user's account, tier, or settings.

## Michael's instruction (verbatim)

"smarkets API helper, answer these questions for an onboarding user"

## Customer message (verbatim)

"Before getting started, could you also clarify a couple of details regarding the
fee structure:
1. Is the commission standardly 2% on net winnings per market?
2. Are there volume-tiered rates or reduced commission tiers available? I anticipate
turning over at least £100,000 per month, assuming unrestricted deposits, so I
would be keen to know if lower rates apply at that level.
Thanks for your help, and I look forward to hearing from you."

## Verified facts (re-verify against sources; parent-verified 2026-10-13)

1. Commission FAQ — live fetch TODAY via Jina (copy:
   `responses/2026-10-13-onboarding-fee-structure-sources/commission_faq_live_2026-10-13.md`;
   identical to local scrape `help-pages/smarkets/en-gb/212654665_Smarkets_commission_FAQ.md`):
   - "As the original 2% commission exchange, our Standard Tier of commission is 2%
     on net profits per market only."
   - "A 1% Pro Tier. Anyone who places more than 1500 bets or stakes more than £1m
     in a calendar month will have to opt in to the Pro Tier to continue trading on
     Smarkets."
   - "Only users who have gone past an 80% threshold of either limit for the Pro
     Tier can opt in."
   - "will pay commission per each individual matched bet that settles (1% for Pro
     Tier, 3% for Select Tier), either on the profit if it wins or the losses if it
     loses."
   - "these metrics are based on all bets placed, whether they are unmatched,
     partially matched or fully matched. The limits are based on the initial bet
     placement."
   - "Amount Staked: This is the liability of all bets placed on Smarkets."
   - "The two metrics related to the Pro Tier (bets placed and amount staked) will
     reset on the 1st of each month".
   - "A 3% Select Tier which is applied to a very small number of the most
     profitable Smarkets users who exceed £25,000 in net profit over the previous
     12 calendar months."
   - "Trading Stats & Commission page which shows you your recent commission
     metrics. Find it via the account drop-down or by going to
     smarkets.com/account/stats when logged in."
2. API T&Cs — live fetch TODAY via Jina with X-Wait-For-Selector (copy:
   `responses/2026-10-13-onboarding-fee-structure-sources/api_tcs_live_2026-10-13.md`;
   matches local scrape `scrape-aug18/help/api-tcs.md`), Section 3 "Setup Fee and
   Commission":
   - "All accounts will be subject to standard Customer Commission as outlined here"
   - "API customers are ineligible for any affiliate commission offers, as well as
     the 60 day 0% commission offer for new customers"
3. Skill ref `~/.hermes/skills/process/smarkets-api-support/references/commission-tiers-faq.md`
   (secondary source): "There is no automatic API discount"; "The Pro Tier (1%) is
   NOT a promotional offer — it's the standard volume-based tier"; API users ineligible
   for promotional rates (0% new-user, affiliate) but can qualify for/opt into Pro.
4. Arithmetic/derivation: customer-stated £100,000/month is below the £1m staked
   limit; the bet-count limb is independent of stake size (counts all bets placed,
   including unmatched), so it can be reached on smaller stakes. This is the draft's
   only derived claim — check the phrasing does not overpromise qualification.

## Editorial decisions to challenge if wrong

- (a) The Select tier sentence is included for completeness (customer asked about
  "tiers" plural). Flag if it reads as scope creep or invites confusion.
- (b) The API-access sentence (standard commission from start; Pro available; promo
  rates not available on API access) is included because the recipient is an
  onboarding user and the API T&Cs flag these exclusions upfront. Flag if unearned.
- (c) "you would sit below the £1m staked limit" + "not apply ... on staking alone"
  plus the bet-count qualification: verify this is accurate and not overpromising
  (see fact 4). Check the customer's words are echoed correctly (they said
  "turning over at least £100,000 per month").
- (d) "Standard is the default for new accounts" — policy statement, not account
  state; flag if it crosses the no-account-claims gate.

## Hard gates (verbatim; pass/fail each)

- Plain text only; no markdown, no tables, no headers, no bold.
- Straight quotes only; no em/en dashes; no hyphenated compound modifiers
  ("opt in" unhyphenated, "new customer", "60 day", "Trading Stats & Commission"
  kept as the page title).
- UK English; contractions acceptable.
- Banned: "Unfortunately", "I'm sorry to say", "I understand", "the upside is",
  "furthermore", "additionally", "Please be advised", "I can confirm that",
  "Thanks for the detailed overview", "do not hesitate".
- No spec/schema/OpenAPI wording; no api@smarkets.com reroute; no competitor
  comparisons; no account-state claims.
- Negative density: count not/no/never/isn't/don't/won't/can't/aren't etc.; report
  as a number; flag if >3 and propose trims that keep material restrictions.
- Every sentence must state a material fact, give the decision, explain a reason,
  or give a next step (four-job test). Early decision is acceptable for this
  info class.
- Sign-off exactly "Kind regards," / "[name]" / "Smarkets Support".
- No huge aggregate numbers; no promises about future tier status.
- Numbers to verify: 2%, 1%, 3%, 1,500, £1m, £100,000, £25,000, 80%, 12 months,
  60 day; "$" not used.

## Reviewer roles and deliverable

- Reviewer 1 — FACT/source: trace every factual claim in the draft to the sources
  above (2% net market basis and netting; Pro thresholds; 80% opt-in; required
  past the limit; per-bet charging including losses; bet count includes unmatched;
  counters reset on the 1st; Select £25k/12 months; API promo exclusions; "default
  for new accounts"); verify every number; flag inference vs verified; check the
  customer echo (they asked "standardly 2% on net winnings per market").
- Reviewer 2 — ADVERSARIAL/recipient + PROCESS: read as the onboarding user. Does
  the email answer BOTH questions directly and completely? Any overreach,
  overpromise, or false expectation (especially the bet-count route and the
  £100k mapping)? Does anything need account verification we do not have? Decide
  whether items (a) and (b) of the editorial decisions earn their place or add
  noise. Check register works for a commercial user pre-start.
- Reviewer 3 — VOICE/structure/compliance: full mechanical scan of every hard
  gate; negative-density count as a number; four-job test per sentence; single
  author voice; prose not FAQ dump; sign-off exact; check no decision is stacked
  (this is info-class, early decisions fine, but no repetition of the same point);
  confirm the closing line adds value or flag for removal.

Output contract (structured): role; grade APPROVED or NEEDS REVISION; findings;
mandatory_fixes (minimal exact wording, or empty).
