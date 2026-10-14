# Complaint Intake Questionnaire and Fact-Finding Protocol

**Trigger:** Michael pastes a complaint, a formal complaint, a final-response request, or a
threatening escalation (IBAS / UKGC / eCOGRA / social media / resolver / solicitor).

**Rule:** when this triggers, do NOT draft a customer response first. Run this intake, return
the questions, and stop. Drafting waits until the material gaps are closed (voice-core §9).

The purpose is to make Michael's side of the work a single pass. Every question here exists
because its answer can change at least one of: the decision, the remedy, the rule cited, the
wording of the decision sentence, or the ADR route. If an answer cannot change any of those,
do not ask it.

---

## Output contract

When a complaint lands, return exactly this shape and nothing more:

```
CLASSIFICATION
  Product:      <Smarkets exchange | SBK | Smarkets API | unclear>
  Jurisdiction: <UK | EU/EEA (state) | Sweden | other | unknown>
  Status:       <first-line reply | formal complaint filed | final response requested>
  ADR raised:   <none | named by customer | already filed>
  Class:        <one or more classes from the list below>

QUESTIONS TO MICHAEL
  1. ...
  2. ...
  (numbered, each with a suggested answer or a pick-list where the answer is finite)

QUESTIONS TO THE CUSTOMER (if a reply is being sent before any decision)
  ...   (only if we are answering before the position is decided; keep to 1 to 3)

HOLDING DRAFT
  (only if a holding reply is needed; otherwise omit)
```

Keep the whole thing under 200 words unless the complaint is genuinely multi-class. Do not
restate the complaint back. Do not include an assessment, a position, or a rule citation in
the intake. The position comes after the answers, not during the questions.

---

## Part A. Triage answered from the complaint itself

Extract these from the complaint before asking anything. Only ask what is genuinely absent.

- A1. Which product? Smarkets exchange, SBK sportsbook, or the Smarkets API. Signals: lay,
  back, liability, matched, commission, trade out = exchange. Accumulator, Bet Builder, the
  app, SBK = sportsbook. Session token, endpoint, 401/403/429, POST /v3/ = API. If the
  complaint is ambiguous, ask; never assume (voice-core §7C).
- A2. Which jurisdiction is the customer in? UK, EU or EEA member state (name it), Sweden,
  or elsewhere. This decides the ADR route and sometimes the T&Cs version. If the customer
  has not said, ask; do not infer it from a timezone or a league.
- A3. What is the case status? A first-line reply, a complaint the customer has now filed, a
  complaint already answered where this is the final response, or a customer who has named
  an ADR body. This drives the complaints-process gate (voice-core §5).
- A4. What does the customer actually want? Name the remedy in their words: a regrade, a
  refund, a credit, a reinstatement, an explanation, an apology, an account change.
- A5. Which class or classes does this fall into? Pick from the classified list below. A
  complaint can be two classes; say so rather than forcing it into one.

### Complaint classes

1. Settlement or result dispute (bet settled the customer disagrees with).
2. Void, unvoid, or reinstatement (void reversed or not reversed, re-bet after chat).
3. Match market or market-definition dispute (90 minutes versus to advance, draw present).
4. Dead heat or multiples interaction (Bet Builder, Top 5/10/20, reduction of the multiple).
5. Reduction factor (horse racing, withdrawn runner, price or stake effect).
6. Non-standard match format (quarters, shortened friendly, abandoned).
7. Bet cancellation or stake-error request.
8. Account restriction, verification, source of funds or source of wealth.
9. Payment, withdrawal, closed-loop, or deposit issue.
10. Bonus or promotion eligibility.
11. API technical (auth, rate limit, orders, streaming, access or refunds).
12. Unauthorised access or a hacked account.
13. Reliance on live-chat guidance (customer acted on what an agent said).
14. Social responsibility, affordability, or duty of care (often a templated form).
15. Non-delivery of service or a general service complaint.
16. Complaint about how a previous complaint or ticket was handled.

---

## Part B. Questions by class

Ask only the block that matches the classified complaint. Where a question resolves to a
closed set, offer the set so it can be answered in one word.

### 1 and 2. Settlement, void, unvoid, reinstatement

- B1.1 Exact bet IDs, and for each one: stake or liability, price or odds taken, side, market
  name, and whether it was matched, partially matched, or unmatched.
- B1.2 For each bet, the current ledger treatment: stands as settled, voided, stake returned,
  or credited. Name the figure credited, not an approximation.
- B1.3 If any credit was already applied, which rule was it processed under: Rule 4.6
  correction of a wrong void, Rule 9.4 discretion, or a goodwill gesture. This attribution
  must come from the sent response, not from memory; if it is unclear, ask before drafting.
- B1.4 Was the customer given live-chat guidance, and what exactly was said? Verbatim if
  available. This separates a rule-backed limb from a discretionary one.
- B1.5 Was the market voided because of a data-provider error, a cancelled event, a fixture
  recreated under a new name, or something else? State which, only if verified.
- B1.6 Did the customer re-bet on their own initiative or on our advice? (Decides whether
  there is a discretionary limb at all.)
- B1.7 For negative balances following resettlement: Did the customer withdraw funds
  between initial settlement and correction? What caused the correction (e.g. steward inquiry
  before weigh-in under Rule 13.1.1, feed error under Rule 4.6)? Does internal policy enforce
  full balance recovery (Rules 4.7 and 5.2) or grant discretionary relief under Rule 9.4?

### 3. Match market or market definition

- B3.1 Which market was the bet on, and did it offer a Draw selection? (A Draw means a
  90-minute market; an overall-winner market would not carry one.)
- B3.2 Was a To advance (including extra time and penalties) market available for the same
  event at the time of the bet? If yes, note it; it is the alternative we point to.
- B3.3 Was the complaint about settlement or about how the market was presented? These are
  different cases; do not merge them.

### 4. Dead heat or multiples

- B4.1 Was the slip a Bet Builder or a standard multiple? The slip controls the treatment.
- B4.2 Which selections were involved, and how did each settle (won, lost, dead heat, void)?
- B4.3 If the customer is arguing a reduction factor should apply instead of a void, note the
  factor they calculated without re-performing their arithmetic.

### 5. Reduction factor

- B5.1 Which runner was withdrawn, and what was the reduction factor applied (or claimed)?
- B5.2 Price and stake as matched, and which matched bets were affected.
- B5.3 Did any price land below 1.00 after the reduction (the stake-returned floor)?

### 6. Non-standard match format

- B6.1 What was the actual format played, and how was it officiated (periods, total minutes)?
- B6.2 Was the format known before the bet, and was it the format the customer expected?
- B6.3 Did the match complete, or was it abandoned?

### 7. Bet cancellation or stake error

- B7.1 Which product, and was the bet matched or unmatched?
- B7.2 Was the cancellation requested within the allowed window, and on what grounds:
  clearly erroneous price, stake input error, or a mistake identification of a contract?
- B7.3 When was the request made relative to the result being decided?

### 8. Account restriction, verification, source of funds or wealth

- B8.1 What restriction is live: deposit block, bet block, suspension, or full closure?
- B8.2 What documents or information were requested, and on what date?
- B8.3 Has anything been supplied, and what happened after it was supplied?
- B8.4 Is the complaint actually about a delay, the request itself, or the outcome?
- B8.5 Has the customer asked why they were selected? If so, remember the documents do not
  publish any selection criteria, so do not invent a trigger.

### 9. Payment or withdrawal

- B9.1 Which method and how much; was the withdrawal requested or only attempted?
- B9.2 Has verification been satisfied, or is that the blocker?
- B9.3 Is the customer asking about closed-loop return to the deposit method? If so, the
  qualifier in T&C 5.11 applies (returned to the same method wherever possible).

### 10. Bonus or promotion

- B10.1 Which promotion, and what were its published conditions?
- B10.2 Which product is the customer on, exchange or SBK? Different products, different
  terms; an exchange account is outside SBK promotions.
- B10.3 Commission tier, if the reply touches commission (Standard, Pro, Select, or a new
  account offer).

### 11. API technical

- B11.1 What did the customer actually see? The full error body, not a status code alone
  (HTML versus JSON changes the diagnosis).
- B11.2 Which endpoints, and what request pattern and volume, over what window?
- B11.3 Has it happened since, and did it resolve on its own or after a re-auth?
- B11.4 Is this actually an access, rate-limit, or scope question rather than a fault?

### 12. Unauthorised access or hacked account

- B12.1 Was this already answered, and is this a final response?
- B12.2 What does the account show: sign-in location, any payment method added, balance
  movement, and whether the bets were placed while logged in with valid credentials?
- B12.3 Did the customer say they never shared the password, and is there a prior credit or
  goodwill already on the account?
- B12.4 Has the customer filed a complaint, or is this the first reply?

### 13. Reliance on live-chat guidance

- B13.1 What exactly did the agent say, and when, relative to the bet?
- B13.2 Does Michael authorise stating that the chat guidance was incorrect? (Do not state it
  without authorisation.)
- B13.3 Does the discretionary limb get a credit, and if so which rule labels it?

### 14. Social responsibility, affordability, duty of care

- B14.1 Is this a templated complaint (look for a solicitor's block, a regulator citation, an
  affordability or LCCP argument, a request to refund all losses)?
- B14.2 What specific intervention is the customer alleging should have happened, and when?
- B14.3 What tools are already on the account: deposit limits, session limits, self-exclusion?
- B14.4 Has the customer asked for a refund of losses, or for the account to be closed, or
  both?

### 15 and 16. Service complaint, or complaint about handling

- B15.1 Which interaction is being complained about, and on what date?
- B15.2 What was promised, and by whom (refer to "the live chat agent", never a name)?
- B15.3 What outcome is the customer asking for that we can actually deliver?

---

## Part C. Michael-side operational questions (internal, never customer-facing)

These are the facts only Michael or the account data can confirm. Ask them plainly and
separate them from anything the customer stated.

- C1. What is the internal decision? Uphold, decline, partial grant, or not yet decided.
- C2. For every figure quoted, is it exact and from the account, or an approximation? Exact
  figures with IDs beat hedges; never write a hedge when an exact figure exists.
- C3. Is there a prior credit or goodwill already on the account, and under which rule?
- C4. Does the customer's jurisdiction match what we are about to tell them about ADR?
- C5. Is there a prior response we must stay consistent with? If a claim was framed to the
  customer a certain way before, do not silently recharacterise it now.
- C6. Is the customer already in the complaints process, or is this the first reply? Only the
  complaints process route can be offered when the customer has raised it or when this is
  the final position on a filed complaint.

---

## Part D. Evidence and verification rules

- D1. Separate four things explicitly in everything you return: verified account or event
  data supplied by Michael, the approved internal decision, what the customer said, and
  inference. Never promote inference to fact.
- D2. Quote the customer's words, not your translation of them. If they wrote a library
  error message, do not relabel it as an HTTP status they never used.
- D3. Verify every rule, clause, price, and figure against the source file before it enters a
  draft. If it cannot be traced, mark it unverified rather than guessing.
- D4. Do not assert that no system error occurred, or that a market rendered normally,
  unless it has been verified against the event or ticket data. Otherwise say the market was
  settled in line with the published rules.
- D5. For a delay complaint, the internal SLA in the T&Cs is the binding figure. The help
  article's longer outer limit does not replace it. Flag the discrepancy to Michael rather
  than quoting either figure to the customer without instruction.

---

## Part E. Remedy and ADR gate

Run this last, after the decision is known. It decides one line of the reply.

- E1. Did the customer explicitly ask to complain, to escalate, or name IBAS, eCOGRA, UKGC,
  the MGA, the EU ODR, a solicitor, or social media? A threat alone is not a request; do not
  engage it and do not pre-empt it with a route.
- E2. Is this a partial grant? If so, a complaints pointer is included at the end.
- E3. Is this a full grant? If so, the complaints line is absent.
- E4. Is this the final position on a complaint the customer has already filed? Only then is
  the ADR route stated, and it must match the customer's jurisdiction.
- E5. Which ADR body is correct for this customer? UK: IBAS. Outside the UK: eCOGRA. Outside
  the UK and Sweden: also the MGA. EU: also the EU ODR service. Sweden is carved out of the
  MGA route. Use the route the T&Cs name, and if the help article names a shorter list, the
  T&Cs govern.

---

## Part F. Pitfalls

- Do not draft before the intake is answered. A draft built on gaps will be rewritten.
- Do not ask a question whose answer is already in the complaint, an earlier message in the
  thread, or a local case file.
- Do not ask more than the case needs. A single-class complaint with a clear remedy needs
  nothing beyond the triage and its one block.
- Do not fold two classes into one position. If a customer disputes both a void and a
  reduction factor, answer each on its own facts.
- Do not turn the intake into an assessment. No positions, no rule quotes, no conclusions
  until the answers are in.
- Do not offer the complaints route in the intake. It is a remedy-stage decision (Part E).

---

## Part G. Holding reply, when one is needed before the position is set

Only when the customer must be answered before the facts are in. Straight quotes, plain
text, no markdown, no em dashes, no hyphens in compound modifiers.

```
Hi <name>,

Thank you for your email. I've started looking into this and I want to make sure I get it
right, so I'm checking the account records before I come back to you.

So that I can be certain about <the specific point>, could you confirm <the one or two
things only they can tell us>?

I'll come back to you as soon as I've been through it.

Kind regards,
<name> Smarkets Support
```

One ask set, one question or two at most. Do not list every possible fact you might need.
