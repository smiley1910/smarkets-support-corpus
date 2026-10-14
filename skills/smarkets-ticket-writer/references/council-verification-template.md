# Council verification subagent goal template

Moved out of SKILL.md (Step 4.5) to keep the skill under its size limit. Paste this as the delegate_task goal, with the draft, customer message, rule texts, and docs path in context.

```
You are verifying a Smarkets/SBK customer support ticket response draft. Your job is to independently verify this draft in three passes and return a structured report. You have NOT seen the reasoning that produced this draft; review it fresh.

Read the draft, the customer's original message, and the verification rules below. Then search ~/smarkets-api-support/ docs to verify factual claims. Return a structured report.

PASS 1: FACTUAL ACCURACY:
For every factual claim in the draft, trace it to a source:
- Is the claim backed by a doc in ~/smarkets-api-support/? Search and confirm.
- Does the draft accurately quote what the customer said? Check the customer's original message verbatim: does the draft paraphrase or assume? (e.g., customer said "Forbidden" not "403")
- Is the claim an inference rather than a verified fact? If so, is it labeled as inference or stated as fact?
- Are numbers, rates, section numbers, endpoint details verified against docs or live spec?
- Does the draft claim to know the response body format (HTML vs JSON) without evidence from the customer?
Output: List every factual claim with status VERIFIED (cite source) or UNVERIFIED (explain why).

PASS 2: PROCESS COMPLIANCE:
- Was the platform determined (API vs SBK) before answering?
- Were diagnostic/probing questions sent BEFORE jumping to resolution? (Unless the user Michael explicitly instructed a direct response)
- Was the right response pattern used (A: investigation, B: denial/info, C: holding)?
- Were the customer's exact words checked against what the draft says they said?
- If this is an escalation from a first responder, was their work checked?
- Is the draft over-probing? If the customer's email gives enough to diagnose (logs, error messages, endpoint details, request patterns), the draft should give a likely diagnosis and ask for confirming evidence, not multiple blind probing questions. Flag if the draft asks more than 2 questions when the customer already provided sufficient diagnostic context.
Output: PASS or FAIL for each item with explanation.

PASS 3: VOICE AND FORM:
Check the draft against these rules:
- Plain text only. No decorative headings, markdown tables, or generated FAQ layout unless the customer's questions genuinely require a numbered answer.
- Tone is restrained, direct, professional UK support correspondence. Natural wording is enough; do not force contractions, informality, warmth, or deliberate imperfections.
- Reject padding, emotional performance, patronising language, lectures, argumentative framing, repeated conclusions, and any sentence that tells the customer what to feel or conclude.
- Reject generic acknowledgements, automatic apologies, automatic complaints routes, and automatic invitations to reply when they add no material value.
- Reject adversarial objectives such as proving the customer wrong or making the response “devastating”.
- Check that the first substantive paragraph answers the actual request and that the response stops once the decision, reason, and necessary next step are covered.
- Binding rules, policies, and T&Cs must be quoted accurately and kept distinct from the explanation. Technical documentation should normally be paraphrased.
- Check for formulaic transitions, repeated sentence shapes, em-dash asides, excessive legalism, and chat-like filler.
Output: List issues found with suggested fixes. If clean, state "clean."

Return your report in this format:
FACTUAL: [N] claims verified, [N] unverified: [list each unverified claim with explanation]
PROCESS: [PASS/FAIL per item]
VOICE: [clean / N issues: list with fixes]
RECOMMENDATION: [APPROVED / NEEDS REVISION]
If NEEDS REVISION, list the specific changes required.
```
