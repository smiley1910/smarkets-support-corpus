Hi [Customer name],

Thanks for reaching out.

The ``price`` field in your order already provides the price protection
you're looking for, it acts as a limit price, not a market price. You just
need to combine it with the right order type.

When you place a buy (back) order at ``price``: 5000 (decimal 2.0), the
exchange will only match it at 5000 or better. For a buy order, "better"
means a lower Smarkets price — which equals higher decimal odds (better
value for you as a backer). If the best available price on the exchange has
moved to worse odds than 2.0 (e.g., 5500 = 1.81 decimal), your order will
not match.

So the ``price`` field **is** your price condition, there's no separate
field needed.

Set ``type`` to ``"immediate_or_cancel"``. This tells the exchange to
attempt matching only at placement time. If your order can't be matched at
price 5000 or better, it's cancelled immediately rather than resting in the
order book.

Your ``minimum_accepted_quantity`` is already set to 10000 (the same as your
``quantity``), which makes this a Fill-or-Kill order: the full amount must
be matched at 5000 or better, or nothing is matched at all.

Please try the below:

.. code-block:: json

    {
      "contract_id": "123456",
      "label": "strategy_1",
      "market_id": "128939",
      "minimum_accepted_quantity": 10000,
      "price": 5000,
      "quantity": 10000,
      "side": "buy",
      "type": "immediate_or_cancel"
    }

You should get the following logs:

*  **HTTP 200** — the order was matched. Check ``total_executed_quantity``
   in the response to confirm the fill amount, and ``executed_avg_price``
   for the price you actually got (which may be better than 5000).
*  **HTTP 400** with ``error_type: "ORDER_CANCELLED_INSUFFICIENT_LIQUIDITY"``
   — the price wasn't available and the order was cancelled. Nothing was
   matched.

The POST response is synchronous for ``immediate_or_cancel`` orders; you
get the final result immediately, no polling required.

.. note::

   Without specifying ``type``, the default is ``good_til_halted``. This
   means your order rests in the order book at price 5000 until matched or
   cancelled by a market event (halt, reduction factor, etc.) — it doesn't
   cancel if the price isn't immediately available. That's the behaviour
   you're seeing.

If you'd accept a partial match (e.g., only £0.50 of your £1.00 matched if
that's all that's available at 5000 or better), set
``minimum_accepted_quantity`` lower than ``quantity``:

.. code-block:: json

    {
      "type": "immediate_or_cancel",
      "minimum_accepted_quantity": 5000,
      "quantity": 10000,
      "price": 5000,
      "side": "buy",
      "contract_id": "123456",
      "market_id": "128939"
    }

This would match whatever is available at 5000 or better (down to a minimum
of 5000 units / £0.50) and cancel the rest.

Should you need any further assistance, do not hesitate to reach out.
Wishing you a lovely day.

| Kind regards,
| Michael
