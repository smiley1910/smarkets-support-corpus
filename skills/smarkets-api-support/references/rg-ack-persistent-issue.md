# Persistent RG_ACK Issue — Swedish API User Case Study (July 2026)

## Background

A Swedish API user with approved API access receives `RG_ACK_REQUIRED` (HTTP 403) on every API order placement attempt, despite repeatedly acknowledging the RG popup on the website. Website betting works fine. The user has been patient across multiple exchanges and has asked whether other Swedish API users are affected, whether it's related to their country of residence, and whether there are additional settings/limits they've missed.

## Internal Context (NOT for customer)

- Every new login/session resets `ack_required` to `true`
- Most API integrations create new sessions frequently (easier than grabbing the token from a successful login and reusing it)
- Even with proper session reuse, the ack only persists for approximately one hour before the customer would need to manually re-ack on the website
- Whether the ack requirement can be removed for Swedish API users is a compliance question, not a technical one — may be a regulatory red line for the jurisdiction regardless of whether trading is automated

## Key Decisions

1. Do NOT suggest session token reuse — only buys ~1 hour, not a real solution. The user (Michael) considers this misinformation.
2. Keep responses vague — do not reveal internal mechanics (session resets, 1-hour window, compliance uncertainty)
3. Acknowledge it's a lasting issue — don't string the customer along with false hope of an imminent fix
4. Holding response first — when waiting on compliance decision, use a holding response rather than the full honest breakdown

## Holding Response Draft (July 2026)

Used when compliance decision is pending (e.g., head of compliance returning Monday — do not mention this to the customer):

> Hi [name],
>
> Thank you for the follow-up, and apologies for the delay getting back to you — I understand the frustration, especially when you've been thorough in testing everything on your end.
>
> I can confirm you haven't missed any settings or limits — your API access is active and your account is configured correctly. The `RG_ACK_REQUIRED` response is not an authentication or approval issue.
>
> This is something I'm actively looking into with our team, and rather than give you a partial answer now, I want to make sure I come back to you with something concrete. I expect to have a clearer update for you in the coming days.
>
> I appreciate your patience — I know that's not the immediate resolution you're looking for, but I want to get this right rather than send you round in circles.

## Full Honest Response Draft (July 2026)

Used when a holding response is no longer sufficient and the customer needs a definitive answer:

> Hi [name],
>
> Thank you for your patience and for the thorough troubleshooting. I appreciate the effort you've put into testing this, and I apologise for the time it's taken to come back to you with a clear answer.
>
> **Your API access is active**
>
> The `RG_ACK_REQUIRED` response confirms your requests are reaching our trading engine. This is not an authentication or approval issue. Your account is fully configured for API use, and you haven't missed any settings or limits.
>
> **About the RG acknowledgement**
>
> The responsible gambling acknowledgement is a regulatory requirement that applies based on your jurisdiction. You're correct that this is related to your country of residence. Responsible gambling requirements are jurisdiction-specific and apply differently depending on where an account is registered.
>
> This is a known and lasting limitation of how the RG acknowledgement requirement interacts with API trading. The website works because the acknowledgement is handled within the browser environment, but the API does not currently have an equivalent mechanism for maintaining that acknowledgement state.
>
> This is something our team is aware of, but I can't provide a specific timeline for when this might change. Any modification to how regulatory requirements apply to API users would need to go through a compliance review.
>
> **Regarding other Swedish users**
>
> I'm not able to share details about other accounts, but the responsible gambling requirements that apply to your account are jurisdiction-based, so the experience for users in other countries may differ.
>
> **In the meantime**
>
> The website remains the reliable way to place bets on your account.

## Pre-Sales API Enquiry (July 2026)

A prospective API user (not yet signed up) asked two questions:

1. **When does the 60-day refund window start?** — From successful registration, when the £150 fee is deducted and API access is activated (T&C Section 3)
2. **Can they test by retrieving data before placing bets?** — Yes, a short integration testing phase is fine. The API supports both viewing market data and placing bets (T&C Section 2). However, the T&Cs prohibit using the API "strictly for data extraction purposes without commensurate trading volumes" (Section 6.1), and "data harvesting" is grounds for suspension (Section 7). A temporary integration phase is expected; prolonged data-only usage is not.

## Style Notes (from this session)

- User considers em-dashes an AI writing tell. Use commas instead.
- ReST syntax broke in the ticketing system. User fell back to plain text with plain quotation marks and bare URLs.
- User prefers concise responses for pre-sales/information queries. Let T&C quotes do the work.
- Do not use the term "paper testing" — implies a paper trading environment exists, which it doesn't.
