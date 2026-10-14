# RG_ACK_REQUIRED — Swedish API Users (Internal Context)

**Status:** Internal-only reference. Do NOT share these details with customers.
**Created:** July 2026
**Source:** Design team briefing via API support ticket escalation

## The Problem

The standard skill guidance says RG_ACK_REQUIRED is a "one-time regulatory step" where the customer acknowledges a popup on the website and the block lifts immediately. This is **incorrect for Swedish API users**.

## Internal Mechanics (NOT for customer disclosure)

1. **Every new login/session resets `ack_required` to `true`.** The RG acknowledgement does not persist across sessions.
2. **Most API integrations create new sessions frequently** because it's easier than extracting and reusing the session token from a successful login response.
3. **Even with session reuse, the acknowledgement only persists for approximately one hour.** After that, the user would need to go back to the website and manually acknowledge again.
4. **This makes API trading effectively impossible** for affected Swedish users. They cannot place a single successful API bet, even immediately after acknowledging on the website, if their integration creates a new session for each request.

## Compliance Uncertainty

As of July 2026, it is unclear whether the RG_ACK requirement can be removed for Swedish API users. This is a compliance question, not a technical one. The uncertainty is:

- Is the per-session RG_ACK a hard regulatory requirement from Spelinspektionen that cannot be waived?
- Or is it a Smarkets implementation choice that could be modified for API users?

The head of compliance needs to make this determination. Until then, the issue is unresolved.

## Customer Response Guidance

### What NOT to tell the customer

- Do NOT mention session token reuse as a workaround (it only provides ~1 hour of trading, so it's not a real solution)
- Do NOT reveal that every new session resets the ack state
- Do NOT reveal the ~1 hour persistence window
- Do NOT reveal the internal compliance uncertainty
- Do NOT say "this is a one-time step" (it isn't for these users)
- Do NOT instruct them to "just log in and acknowledge the popup" (they've already tried this repeatedly)

### What TO tell the customer

- Confirm their API access is active (the RG_ACK error proves requests reach the trading engine)
- Confirm they haven't missed any settings or limits
- Acknowledge this is a known and lasting limitation, not a troubleshooting issue on their end
- Explain the RG requirement is jurisdiction-specific (related to their country of residence)
- Set realistic expectations: no timeline, any change needs compliance review
- If waiting on a compliance decision, use Pattern C (holding response)

### Holding response (while waiting on compliance)

Use Pattern C from the skill:
1. Acknowledge their latest message, apologise for delay
2. Confirm what you can (API access active, no missed settings)
3. Say you're looking into it and expect a clearer update soon
4. Do NOT mention the compliance dependency
5. Do NOT promise a timeline

## Resolution (July 2026)

The issue is confirmed **unfixable**. Rather than continuing to troubleshoot, Smarkets has decided to discontinue API access for all Sweden-based customers. This is framed externally as a regulatory exit driven by SGA requirements, NOT as a technical failure.

See `references/sweden-jurisdiction.md` → "API Discontinuation" section for the diplomatic closure approach and customer communication pattern.

The customer-facing communications do NOT mention RG_ACK_REQUIRED or any internal mechanics. Affected users receive a full £150 setup fee refund regardless of tenure.

## Affected Jurisdictions

Currently confirmed: **Sweden** (Spelinspektionen licence requirements).

Other jurisdictions may be affected if they have similar RG acknowledgement requirements. Check whether the customer's country of residence has mandatory RG acknowledgement regulations before applying the standard "one-time" guidance.
