
╔══════════════════════════════════════════════════════════════╗
║        SMARKETS API - COMPLETE ENDPOINT REFERENCE           ║
║        Source: docs.smarkets.com (OpenAPI v3)               ║
╚══════════════════════════════════════════════════════════════╝


============================================================
  ACCOUNT_ACTIVITY
============================================================

  GET /v3/account_activity_csv/{start_datetime}/{end_datetime}/
  --------------------------------------------------------------
  Summary: Return the account activity between the two specified datetimes as a gzipped CSV.
  Auth: REQUIRED (Session-Token)
  Parameters:
      path: start_datetime (string) REQUIRED
      path: end_datetime (string) REQUIRED
  Notes: ## Description
Start and end datetimes have to be separated by an hour, also these have to be exactly on the hour.

  GET /v3/accounts/activity/
  ---------------------------
  Summary: Retrieve statement information for your account.
  Auth: REQUIRED (Session-Token)
  Parameters:
      query: timestamp_max (string) optional
      query: timestamp_min (string) optional
      query: limit (integer) optional
      query: market_id (array) optional
      query: order_id (array) optional
      query: pagination_last_seq (string) optional
      query: pagination_last_subseq (string) optional
      query: sort (string) optional
      query: source (array) optional
      query: event_info (boolean) optional
  Notes: ## Description
This information should be used for accounting reconciliation.<br>
This data is what is being used in <a href="https://smarkets.com/account/statement">our statement page</a>

============================================================
  ACCOUNTS
============================================================

  GET /v3/accounts/
  ------------------
  Summary: Retrieve account information.
  Auth: REQUIRED (Session-Token)

============================================================
  COMPETITORS
============================================================

  GET /v3/events/{event_ids}/competitors/
  ----------------------------------------
  Summary: Retrieve competitors of a set of events.
  Auth: Not required
  Parameters:
      path: event_ids (array) REQUIRED

============================================================
  CONTRACTS
============================================================

  GET /v3/markets/{market_ids}/contracts/
  ----------------------------------------
  Summary: Retrieve contracts by a set of market ids.
  Auth: Not required
  Parameters:
      query: include_hidden (boolean) optional
      query: jurisdiction (string) optional
      path: market_ids (array) REQUIRED

============================================================
  CURRENCIES
============================================================

  GET /v3/currencies/{code}/
  ---------------------------
  Summary: Retrieve the conversion rate for one specific currency.
  Auth: Not required
  Parameters:
      path: code (string) REQUIRED
  Notes: ## Description
This can be used to convert quantities from GBP to the user's currency

============================================================
  EVENTS
============================================================

  GET /v3/events/
  ----------------
  Summary: Retrieve events that are available on Smarkets to bet on.
  Auth: Not required
  Parameters:
      query: id (array) optional
      query: inplay_enabled (boolean) optional
      query: state (array) optional
      query: type (array) optional
      query: type_domain (array) optional
      query: type_scope (array) optional
      query: with_new_type (boolean) optional
      query: parent_id (array) optional
      query: start_datetime_min (string) optional
      query: start_datetime_max (string) optional
      query: last_modified_min (string) optional
      query: last_modified_max (string) optional
      query: pagination_last_display_order (integer) optional
      query: pagination_last_start_datetime (string) optional
      query: pagination_last_id (string) optional
      query: pagination_last_name (string) optional
      query: sort (string) optional
      query: limit (integer) optional
      query: include_hidden (boolean) optional
      query: jurisdiction (string) optional
      query: platform (string) optional
  Notes: ## Description
Events in Smarkets follow a tree structure per sport,
where events can have several child events, but only one parent event.<br>
As an example for football, we have:<ul>
<li>The root event which is the sport - Football
<li>Child events which are leagues - Premier League, La Liga, etc


  GET /v3/events/{event_ids}/states/
  -----------------------------------
  Summary: Retrieve the current states for events by id.
  Auth: Not required
  Parameters:
      path: event_ids (array) REQUIRED

============================================================
  MARKETS
============================================================

  GET /v3/events/{event_ids}/markets/
  ------------------------------------
  Summary: Retrieve markets by event ids. This should be done after getting events.
  Auth: Not required
  Parameters:
      query: sort (string) optional
      query: limit_by_event (integer) optional
      query: popular (boolean) optional
      query: market_types (string) optional
      query: include_hidden (boolean) optional
      query: jurisdiction (string) optional
      path: event_ids (array) REQUIRED
  Notes: ## Description
Each bettable event has a set of markets. Each market will have a set of contracts.

  GET /v3/events/{event_ids}/markets_count/
  ------------------------------------------
  Summary: Retrieve markets_count by event ids. This should be done after getting events.
  Auth: Not required
  Parameters:
      query: include_hidden (boolean) optional
      query: jurisdiction (string) optional
      path: event_ids (array) REQUIRED
  Notes: ## Description
Each bettable event has a set of markets.

============================================================
  ORDERS
============================================================

  DELETE /v3/orders/
  -------------------
  Summary: Cancel all orders.
  Auth: REQUIRED (Session-Token)
  Parameters:
      query: market_id (string) optional
  Notes: ##  Rate limits
Maximum 1 request per 60 seconds<br>

  GET /v3/orders/
  ----------------
  Summary: Retrieve current orders on Smarkets, these include open and recently settled orders.
  Auth: REQUIRED (Session-Token)
  Parameters:
      query: contract_id (string) optional
      query: created_datetime_max (string) optional
      query: created_datetime_min (string) optional
      query: id (array) optional
      query: limit (integer) optional
      query: market_id (array) optional
      query: pagination_last_id (string) optional
      query: sequence_number_max (integer) optional
      query: sequence_number_min (integer) optional
      query: state (array) optional
      query: side (string) optional
      query: sort (string) optional

  POST /v3/orders/
  -----------------
  Summary: Place orders on the exchange.
  Auth: REQUIRED (Session-Token)
  Notes: ## Description
This route only works for Smarkets API users, other users will receive a 403 status code response.<br><br>
For immediate_or_cancel orders type, the route will return when the order is matched (or cancelled).<br>
For all other order types, the route will return when the order is accept

  GET /v3/orders/fullcover/
  --------------------------
  Summary: Get all fullcover orders for an account.
  Auth: REQUIRED (Session-Token)
  Parameters:
      query: states (array) optional
      query: limit (integer) optional
      query: pagination_last_id (string) optional

  DELETE /v3/orders/{order_id}/
  ------------------------------
  Summary: Cancel specific order.
  Auth: REQUIRED (Session-Token)
  Parameters:
      path: order_id (integer) REQUIRED
  Notes: ##  Rate limits
Maximum 10 requests per second<br>

============================================================
  PRICES
============================================================

  GET /v3/markets/{market_ids}/last_executed_prices/
  ---------------------------------------------------
  Summary: Retrieve the last executed price and timestamp for each contract in the market ids provided.
  Auth: REQUIRED (Session-Token)
  Parameters:
      path: market_ids (array) REQUIRED

  GET /v3/markets/{market_ids}/quotes/
  -------------------------------------
  Summary: Get the current prices from the exchange.
  Auth: REQUIRED (Session-Token)
  Parameters:
      path: market_ids (array) REQUIRED
  Notes: ## Description
If session token is not sent, these prices will be delayed.<br><br>
The rate limits below are applicable to API users.
The rate limits for non-API users are lower.

##  Rate limits
Maximum 50 requests per 60 seconds

============================================================
  SESSIONS
============================================================

  DELETE /v3/sessions/
  ---------------------
  Summary: Logout from the current session.
  Auth: Not required
  Notes: ##  Rate limits
Maximum 30 requests per 60 seconds<br>

  POST /v3/sessions/
  -------------------
  Summary: Login using this route.
  Auth: Not required
  Notes: ## Description
This will return a token that can be used in the Authentication header in the
form "Session-Token <your_token>" on authenticated requests.<br>
The token is valid for 30min, but if you make an authenticated request
with it, it will be renewed for the next 30min.

##  Rate limits
Maximu

  POST /v3/sessions/verify/
  --------------------------
  Summary: Verify login step for multi factor authentication (MFA).
  Auth: Not required
  Notes: ## Description
To enable MFA on a Smarkets account:<br>
 - Go to <a href="https://smarkets.com/account/settings/login">login settings</a>
and click "Enable Two-Factor Authentication"<br>
 - Copy the secret into your TOTP library<br>
 - Generate one code using it and paste it in the dialog<br>
 - Cli

============================================================
  VOLUMES
============================================================

  GET /v3/markets/{market_ids}/volumes/
  --------------------------------------
  Summary: Retrieve traded volumes by market ids.
  Auth: REQUIRED (Session-Token)
  Parameters:
      path: market_ids (array) REQUIRED


============================================================
  ERROR SCHEMAS
============================================================

  InternalServerError:
    data: object
    error_type: string = ['INTERNAL_ERROR']

  RateLimitError:
    data: object
    error_type: string = ['RATE_LIMIT_EXCEEDED']

  RequestValidationError:
    data: string
    error_type: string = ['REQUEST_VALIDATION_ERROR']

  CountryBlockedError:
    data: object
    error_type: string = ['COUNTRY_BLOCKED']

  RequestTooLarge:
    data: object
    error_type: string = ['REQUEST_TOO_LARGE']

  NoResultsFound:
    data: object
    error_type: string = ['NO_RESULTS_FOUND']

  BadRequest:
    data: object
    error_type: string = ['BAD_REQUEST']

  GatewayTimeout:
    data: object
    error_type: string = ['ZEUS_TIMEOUT', 'RECKONATOR_UNAVAILABLE']


============================================================
  AUTHENTICATION
============================================================

  api_key:
    Type: apiKey
    In: header
    Header: Authorization