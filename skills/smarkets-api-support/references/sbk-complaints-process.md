# SBK / Smarkets Complaints Process

> **Sources:** T&Cs Section 16 (Smarkets 213469085, SBK 360030574872) and the help-centre
> article "Making a complaint" (Smarkets 212032069, SBK 360030578872). The T&Cs are binding;
> the help article is not, and the two differ on one point (see the SLA note below).

## Internal Process (Step 1)

Contractual position, T&Cs 16.1 (identical wording in both products):

- The complaint is emailed to customer support (support@smarkets.com, or support@getsbk.com
  for SBK) and is escalated to management.
- Smarkets will endeavour to tackle the complaint within two working days of receipt.
- The outcome will be communicated within 10 days of receipt of the complaint.

Help-article position: "in some circumstances it may take up to 8 weeks for a decision to be
provided."

**SLA note for tickets.** These two figures conflict, and the older version of this reference
wrongly stated that no shorter SLA is documented. The T&Cs are the binding term, so the two
working days and 10 days are the commitment. The 8-week figure is an outer limit in a help
article and must not be presented to a customer as the commitment. If a customer cites either
figure, flag it to Michael rather than quoting the other without instruction.

## External Escalation (Step 2, once the internal process is exhausted and deadlock exists)

T&Cs Section 16, in order:

- **16.2 IBAS** (Independent Betting Adjudication Service) for customers **within the UK**.
  Named as the third-party adjudicator in all disputed matters. All contact is in writing and
  an adjudication form must be requested first.
  Post: IBAS, PO Box 62639, London, EC3P 3AS
  Email: adjudication@ibas-uk.co.uk
  Website: www.ibas-uk.com
- **16.3 eCOGRA** for customers **outside the UK**. Dispute raised via the eCOGRA dispute form
  at https://ecogra.org/ata/policies_procedures.php
- **16.4 MGA** (Malta Gaming Authority) for customers **outside the UK and Sweden**.
  Player support portal: https://www.mga.org.mt/support/online-gaming-support/
  Email: support.mga@mga.org.mt
- **16.5 EU ODR** service for customers **within the EU**: https://ec.europa.eu/consumers/odr

**Sweden carve-out.** T&Cs 16.4 excludes Sweden from the MGA route. A Swedish customer's
non-UK route is eCOGRA (16.3) and, being in the EU, the EU ODR service (16.5). Do not offer
the MGA to a Swedish customer.

**Help-article divergence.** The "Making a complaint" articles say that all customers may
contact IBAS and name the MGA for customers outside the UK plus the EU ODR platform. They do
not name eCOGRA at all. Where the two disagree, the T&Cs govern: a customer outside the UK is
directed to eCOGRA, with the MGA additionally available outside the UK and Sweden.

## Route selection, quick reference

Customer location to ADR route:

- UK: IBAS (16.2).
- Outside the UK: eCOGRA (16.3).
- Outside the UK and Sweden: the MGA is additionally available (16.4), alongside eCOGRA.
- Sweden: eCOGRA (16.3) and EU ODR (16.5). Not the MGA.
- EU member state: the EU ODR service is additionally available (16.5).

## Key Points for Ticket Responses

- When a customer asks for the complaints procedure, give the internal process first: the
  email address, the two-working-day acknowledgement, and the 10-day outcome commitment.
- Name the ADR body only at the stage the gate allows. The gate in
  `process:smarkets-voice-core` §5 governs: offer the route only where the customer
  explicitly asked to complain or escalate, where Michael instructed it, or where this is the
  final position on a complaint already filed. A threat alone is not a request, so do not
  engage it and do not pre-empt it with a route.
- The process is the same for both products, with the contact address being the only
  difference: support@smarkets.com for the exchange, support@getsbk.com for SBK.
- Match the ADR body to the customer's jurisdiction before writing it into a reply. The most
  common error is offering only IBAS, or only the MGA, to a non-UK customer when 16.3 puts
  eCOGRA first.
- Intake questions for a complaint, and the full ADR gate, are in the ticket-writer reference
  `complaint-intake-questionnaire.md`.