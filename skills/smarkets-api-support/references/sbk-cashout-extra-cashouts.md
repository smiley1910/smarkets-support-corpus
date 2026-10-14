# SBK cash-outs beyond the closing set — complaint + make-good pattern

Case class: SBK customer's balance drops after "cash out" actions, or the customer raises confusing balance changes after cashing out, where extra cash-outs were executed beyond the ones that closed their bets. Worked case: Lee, Arsenal back bets, Oct 2026 (make-good £118.29).

## Mechanics (grounded)

- SBK help article "Cash out on SBK" (help.getsbk.com 15988549801245): *"Cashing out is the same thing as betting on the opposite outcome to happen. So when you cash out, the app will immediately place a counter bet to the one you placed originally."* Amount credited immediately on success.
- Once the customer's bets are fully cashed out, there is nothing left to close. Any further cash-out action goes beyond the bets and acts as a fresh counter position: it reserves value and can lose, cutting the secured amount instead of adding to it.
- Documented glitch class: the same help article (accumulator section) warns "Do not constantly tap the cash out button, as this may cause the feature to lag and place the offer without your confirmation, or even cash out of the same bet twice."
- Support position (Michael, Oct 2026, authoritative): an SBK customer with N back bets should have N cash outs and no further; extra cash-outs beyond that should not have been possible; the make-good amount is exactly what the extra cash-outs cost the customer.

## Audit method — two independent measures, both must agree

1. **Peak measure:** peak available balance minus post-extra available balance.
   Lee case: 133.01 + 187.02 = 320.03 peak; 320.03 − 201.74 = 118.29.
2. **End-state measure:** actual final settled balance vs the counterfactual (as if only the closing cash-outs had happened).
   Lee case: actual 34.74; counterfactual 34.74 + 118.29 = 153.03 (cross-check 133.01 + 220.02 − 200 = 153.03). Difference = 118.29.
3. **Extras' cost** = sum of the extra cash-outs' reservations from the statement's liability column. Lee case: 29.54 + 29.54 + 29.67 + 29.54 = 118.29.
4. Net-result check: (backs' winnings) − (closing reservations + extras' reservations) = statement net profit; without the extras = the flat locked result. Expect ≤1p rounding noise from the statement's truncated figures.
5. Statement has two columns — settled balance (flat until withdrawal/settlement) vs the moving cash-out value. For the extras, the drop prints on placing (reservation), not at match. Do not misread which column moved.

## Customer-facing email rules (approved 2026-10-13; council 3/3)

- SBK concealment: cash outs are cash outs. No lay / hedge / exchange / matched / counter bet terminology; local times only, no UTC or BST labels; no bet IDs; exact figures only.
- Full grant of the amount → complaints pointer ABSENT (voice-core §5). One apology tied to the specific cause ("should not have been possible"); a single decision sentence (returning the amount); no systemic promises and no timeframes for the credit unless Michael supplies one.
- Keep figures and times consistent with any earlier explanation emails sent on the same case.
- Delete any reassurance sentence ("no funds missing") — the reconciliation and the credit do that job.

## Template (Lee case — approved, sent-ready)

```
Hi [name],

Thank you for raising the cash outs on your Arsenal bets from 10 October.

I have reviewed the full sequence. Once your three £30 bets on Arsenal had been cashed out in full at 14:01, there was nothing left to cash out. The four further cash outs between 14:01 and 14:02 went beyond your bets and traded away part of the £320.03 you had secured, reducing your available balance to £201.74. Those further cash outs should not have been possible, and I am sorry that this happened.

I am returning the £118.29 that the further cash outs took from your balance. You will see it added to your account.

If you have any questions about this, just reply here.

Kind regards,
[agent name]
Smarkets Support
```

Adapt amounts, times, bet counts; keep the shape: acknowledge → what was reviewed → why it should not have happened (reason) → single apology → single remedy sentence → short close.

## Files (case record)

- `~/smarkets-api-support/responses/2026-10-13-lee-cashout-refund-FINAL.txt` (approved text)
- `~/smarkets-api-support/responses/2026-10-13-lee-cashout-refund-COUNCIL-BRIEF.md` (facts + audit trail)
