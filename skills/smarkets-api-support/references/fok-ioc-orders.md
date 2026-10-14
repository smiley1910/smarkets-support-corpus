# FOK / IOC Order Types in Smarkets v3 REST API

The v3 REST API does **not** have a `time_in_force` field. Fill-or-Kill and Immediate-or-Cancel are achieved through the `type` + `minimum_accepted_quantity` fields on `POST /v3/orders/`.

## The `type` field

From the live OpenAPI spec (v3). **Default is `good_til_halted`** — if the customer omits the `type` field entirely, they get `good_til_halted` behaviour, NOT `good_til_cancelled`.

The spec includes an explicit lifetime table:

| Order type | Market goes live | Market halted | Reduction factor applied |
|-------|-----------|-----------|-----------|
| `good_til_cancelled` | **Cancelled** | **Cancelled** | **Cancelled** |
| `good_til_halted` | **Kept** | Cancelled | Cancelled |
| `keep_in_play` | **Kept** | **Kept** | Cancelled |
| `immediate_or_cancel` | N/A — matches at placement time only | N/A | N/A |

**Key distinctions agents get wrong:**
- `good_til_cancelled` is cancelled in ALL THREE situations (live, halted, RF). It does NOT "stay open until you cancel it" — the exchange cancels it automatically.
- `good_til_halted` is the DEFAULT. Its key feature: survives the market going live (unlike GTC). Still cancelled on halt and RF.
- `keep_in_play` is the most persistent — survives both market going live AND being halted. Only killed by RF.
- `immediate_or_cancel` is completely different — it's a fill-now-or-cancel order, not a persistent order.

## Achieving FOK vs IOC

### Fill-or-Kill (FOK)
The entire quantity must be matched immediately or nothing is matched:

```json
{
  "market_id": "128939",
  "contract_id": "123456",
  "price": 5000,
  "quantity": 100000,
  "side": "buy",
  "type": "immediate_or_cancel",
  "minimum_accepted_quantity": 100000
}
```

### Immediate-or-Cancel (IOC)
Partial fills are accepted; any unfilled remainder is cancelled:

```json
{
  "market_id": "128939",
  "contract_id": "123456",
  "price": 5000,
  "quantity": 100000,
  "side": "buy",
  "type": "immediate_or_cancel",
  "minimum_accepted_quantity": 50000
}
```

## Common pitfalls

- **Omitting `minimum_accepted_quantity`** — the field is optional (minimum 0). If omitted, the system may default to accepting zero matches, causing the order to cancel immediately with nothing filled. Always set it explicitly for `immediate_or_cancel` orders.
- **Confusing with `good_til_cancelled` / `keep_in_play`** — these are persistent order types, not IOC/FOK. They stay on the book until matched or explicitly cancelled.

## Critical: Unit conversion (most common gotcha)

In the Smarkets API, **10,000 internal units = £1.00** (or equivalent in the user's currency).

| Quantity (internal units) | Monetary value |
|---|---|
| 800 | £0.08 |
| 5,000 | £0.50 |
| 10,000 | £1.00 |
| 20,000 | £2.00 |
| 100,000 | £10.00 |

**Customers reporting a "partial fill" on FOK often have a units error.** The pattern is:

> Customer: *"I placed a £2.00 FOK order with quantity=800 and got a partial fill of £0.08!"*

The math: 800 / 10,000 = **£0.08**. The engine received an 800-unit FOK order, found 800 units of liquidity, and correctly filled it 100%. The customer's intended £2.00 would require `quantity: 20000`.

**Diagnostic step when a customer claims FOK partially filled:** Always verify their quantity value against their stated stake. Compute `quantity / 10000` in the user's currency before investigating further.

## Common troubleshooting scenarios

### Scenario 1: Customer reports partial fill on FOK (units mismatch)

**Symptoms:** Customer says they placed a £X FOK order but got a smaller fill. They passed `minimum_accepted_quantity` equal to `quantity`.

**Root cause:** Quantity units mismatch (see unit conversion above). The engine correctly filled what was asked.

**Fix:** Explain the 10,000 units = £1.00 conversion and show the math.

### Scenario 2: Customer says POST response doesn't carry fill info, tries to poll

**Symptoms:** Customer places `immediate_or_cancel` order, then polls `GET /v3/orders/{id}/` after a delay to check fill status, then tries to cancel as safety net, hitting `ORDER_CANCEL_REJECTED_TOO_LATE`.

**Root cause:** Customer doesn't know that IOC orders are **synchronous**. The POST blocks until the engine finishes matching.

**Fix:** For `immediate_or_cancel` orders, the POST response IS the final state:

- **HTTP 200** → order was accepted and executed. Read `total_executed_quantity` (not `quantity_filled` — that field doesn't exist on POST response). If `total_executed_quantity === quantity`, full fill. `orig_price` being `null` means no executions happened.
- **HTTP 400** with `error_type: ORDER_CANCELLED_INSUFFICIENT_LIQUIDITY` → order was killed because minimum could not be met. Zero fill.

Recommended pattern — no polling or cancel safety net needed:

```
POST /v3/orders/ {type: immediate_or_cancel, ...}

if resp.status == 200:
    # order filled — total_executed_quantity has the final count
    if resp.total_executed_quantity == quantity:
        # full fill — proceed to close leg
elif resp.error_type == "ORDER_CANCELLED_INSUFFICIENT_LIQUIDITY":
    # no fill — retry or move on
```

### Scenario 3: Customer says placing IOC with minimum_accepted_quantity failed

**Symptoms:** `immediate_or_cancel` order with `minimum_accepted_quantity` set still gets cancelled with nothing filled.

**Common cause:** The field is missing or set to 0. When omitted, the system default is 0, meaning "accept zero matches" — the order cancels immediately. Always set it explicitly.

## Response template for customer queries

When a customer asks about `time_in_force` or FOK, use this structure:

> The Smarkets v3 REST API doesn't use a `time_in_force` field directly. Fill-or-Kill behaviour is handled by combining the `type` and `minimum_accepted_quantity` fields.
>
> Set `type` to `"immediate_or_cancel"` and `minimum_accepted_quantity` to the same value as `quantity`. This tells the exchange to only attempt matching at placement time and to require the full quantity before filling anything.
>
> ```json
> {
>   "type": "immediate_or_cancel",
>   "minimum_accepted_quantity": 100000,
>   "quantity": 100000
> }
> ```
>
> If you omit `minimum_accepted_quantity`, the system may accept a zero-match and cancel the order immediately with nothing filled. Always set it explicitly for FOK orders.
>
> If you want IOC (partial fill OK) instead, set `minimum_accepted_quantity` lower than `quantity` — e.g. 50000 vs 100000.

## Common sources of the `time_in_force` confusion

If the customer pushes back asking why they see `time_in_force` in their logs:

1. **Their own abstraction layer** — their application code may use the conventional field name `time_in_force` internally, mapped to `type` before the HTTP request is sent. The log captures the abstraction, not the raw payload.
2. **Crypto exchange crossover** — Binance, Bybit, Hyperliquid etc. all use `timeInForce` / `time_in_force`. If they trade on multiple platforms, it's an easy mental cross-wire.
3. **Legacy v2 API** — the old Smarkets v2 REST API (deprecated, no longer documented) may have used different field names. Their codebase may predate the v3 migration.

## Price as Limit Price (Common Customer Confusion)

Customers frequently ask: *"How do I only place a bet if the price is available? I want the order cancelled if price 5000 (2.0) isn't available — only take >= 5000, nothing less."*

They look at the four order types (GTC, KIP, GTH, IOC) and none mention price protection, because **price protection is inherent in the ``price`` field itself**, not the order type.

**The answer:**

- The ``price`` field IS the limit price. For a buy (back) order at ``price: 5000``, the exchange only matches at 5000 or better (lower Smarkets price = higher decimal odds = better value for the backer). If the best available price is worse than 5000 (e.g., 5500 = 1.81 decimal), the order won't match.
- Combined with ``type: "immediate_or_cancel"``, if the price isn't available at placement time, the order is cancelled immediately rather than resting in the book.
- The order type controls *when/how long* the order lives; the ``price`` field controls *at what price* it matches.

**Why customers get confused:**

The four documented order types all describe *lifetime* behaviour (what happens on market-live, halt, RF). None of them describe *price* behaviour — because that's the ``price`` field's job. A customer reading only the ``type`` descriptions won't find "only match at this price or better" because it's not an order type feature — it's fundamental to how the exchange matching engine works.

**Key point to communicate:** Without specifying ``type``, the default is ``good_til_halted``, which means the order rests in the book at the specified price until matched or cancelled by a market event. The customer needs ``immediate_or_cancel`` to get the "cancel if price not available" behaviour they want.

**Response template (ReST format):**

The customer's payload needs only one addition — ``"type": "immediate_or_cancel"``. Their existing ``minimum_accepted_quantity`` matching ``quantity`` makes it Fill-or-Kill (all-or-nothing at the specified price or better). If they want partial fills, set ``minimum_accepted_quantity`` lower than ``quantity``.

Expected responses:
- **HTTP 200** — matched. Check ``total_executed_quantity`` and ``executed_avg_price`` (may be better than requested).
- **HTTP 400** ``ORDER_CANCELLED_INSUFFICIENT_LIQUIDITY`` — price not available, order cancelled, nothing matched.

POST is synchronous for IOC — no polling needed.
