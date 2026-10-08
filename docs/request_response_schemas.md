# Smarkets API - Request/Response Schemas (Key Endpoints)
> Extracted from OpenAPI spec at https://api.smarkets.com/v0/control/openapi/

## POST /v3/orders/
**Summary:** Place orders on the exchange.
**Description:** ## Description
This route only works for Smarkets API users, other users will receive a 403 status code response.<br><br>
For immediate_or_cancel orders type, the route will return when the order is matched (or cancelled).<br>
For all other order types, the route will return when the order is accepted by the exchange.<br>
In the latter case, GET v3/orders should be used to check the status of the order, using the order id
returned by this response.

##  Rate limits
Rate limits are applied on an per account basis

### Request Body Schema
```json
{
  "properties": {
    "contract_id": {
      "description": "This ID uniquely identifies the contract",
      "example": "123456",
      "pattern": "^[0-9]+$",
      "type": "string"
    },
    "label": {
      "description": "Label is a user-defined string that will be stored in the order.\nIt can be used to identify different trading strategies",
      "example": "strategy_1",
      "type": "string"
    },
    "market_id": {
      "description": "This ID uniquely identifies the market",
      "example": "128939",
      "pattern": "^[0-9]+$",
      "type": "string"
    },
    "minimum_accepted_quantity": {
      "description": "\nIf this minimum accepted quantity is not matched on bet placement time,\nthe order will be cancelled and nothing will be matched.<br>\nOnly applicable to immediate_or_cancel order types.\n    ",
      "example": 10000,
      "maximum": 4294967295,
      "minimum": 0,
      "type": "integer"
    },
    "price": {
      "description": "\nThis price is in percentage basis points.<br>\nExample: 5000 = 50% <br>\nTo convert it to decimal odds, just divide 10000 by it<br>\nExample: 10000 / 5000 = 2.0 (decimal odds).<br>\nThis price has to conform to a valid tick on the exchange;\nan invalid price error will be returned if it does not.",
      "example": 5000,
      "maximum": 9999,
      "minimum": 1,
      "type": "integer"
    },
    "quantity": {
      "description": "\n    Quantity is the sum of the total pot (back+lay) in case the order is matched<br>\n    The units are 1/10000 * one unit of the user's currency.<br>\n    Example: Quantity 500 = 0.05 GBP<br>\n    To convert it to back stake, just multiply by the price and divide by 100000000<br>\n    Example: 100000 (quantity) * 5000 (price) / 100000000 = 5 GBP back stake<br>\n    The minimum stake is \u00a30.05 or currency equivalent",
      "example": 10000,
      "maximum": 4294967295,
      "minimum": 0,
      "type": "integer"
    },
    "side": {
      "description": "\nside can either be:<ul>\n<li>buy: backing a contract\n<li>sell: laying a contract\n</ul>",
      "enum": [
        "buy",
        "sell"
      ],
      "example": "buy",
      "type": "string"
    },
    "type": {
      "default": "good_til_halted",
      "description": "Order types can have the following values:\n    <ul>\n    <li>good_til_cancelled: this order will be open until a reduction\n    factor is applied or a market state changes to live, which will cancel the order.\n    <li>keep_in_play: the same as good_til_cancelled,\n    except it will not be cancelled on market state changes\n    <li>good_til_halted: the same as good_til_cancelled, except a market\n    <li>immediate_or_cancel: if the minimum_accepted_quantity is not\n    matched at the time of order placement, this order will be cancelled. \n    </ul>\n    <p>The following table explains the lifetime of orders:</p>\n    <table cellpadding=\"3\" style=\"border: 1px solid white;\">\n      <tr>\n        <th>order_type</th>\n        <th>Market Goes Live</th>\n        <th>Market Halted</th>\n        <th>Reduction Factor Applied</th>\n      </tr>\n      <tr>\n        <td>good_til_cancelled</td>\n        <td>Cancelled</td>\n        <td>Cancelled</td>\n        <td>Cancelled</td>\n      </tr>\n      <tr>\n        <td>good_til_halted</td>\n        <td>Kept</td>\n        <td>Cancelled</td>\n        <td>Cancelled</td>\n      </tr>\n      <tr>\n        <td>keep_in_play</td>\n        <td>Kept</td>\n        <td>Kept</td>\n        <td>Cancelled</td>\n      </tr>\n    </table><br>\n    <p>Orders marked as immediate_or_cancel must be executed\n    immediately and thus will not remain in the book.</p>\n    ",
      "enum": [
        "good_til_cancelled",
        "keep_in_play",
        "good_til_halted",
        "immediate_or_cancel"
      ],
      "example": "good_til_halted",
      "type": "string"
    }
  },
  "required": [
    "market_id",
    "contract_id",
    "price",
    "quantity",
    "side"
  ],
  "type": "object"
}
```

### Responses
- **200**: Order placement success
- **400**: ORDER_REJECTED_MARKET_SETTLED, ORDER_REJECTED_MARKET_NOT_FOUND, ORDER_REJECTED_LIMIT_EXCEEDED, ORDER_INVALID_INVALID_PRICE, ORDER_INVALID_INVALID_QUANTITY, ORDER_REJECTED_INSUFFICIENT_FUNDS, REQUEST_VALIDATION_ERROR, ORDER_REJECTED_CONTRACT_SETTLED, ORDER_CANCELLED_TRADING_SUSPENDED, ORDER_REJECTED_MARKET_HALTED, ORDER_REJECTED_THROTTLE_EXCEEDED, ORDER_REJECTED_CROSSED_SELF, ORDER_INVALID_INVALID_PRICE, ORDER_CANCELLED_MARKET_HALTED, ORDER_REJECTED_STAKE_LIMIT_EXCEEDED, ORDER_REJECTED_CAPACITY_REACHED, ORDER_REJECTED_CONTRACT_NOT_FOUND, ORDER_CANCELLED_INSUFFICIENT_LIQUIDITY, ORDER_CANCELLED_MEMBER_REQUESTED, ORDER_REJECTED_MARKET_NOT_OPEN, ORDER_REJECTED_TRADING_SUSPENDED, ORDER_REJECTED_ACCOUNT_SUSPENDED, ORDER_INVALID_INVALID_QUANTITY, ORDER_INVALID_INVALID_QUANTITY, ORDER_INVALID_INVALID_PRICE, ORDER_REJECTED_SERVICE_TEMPORARILY_UNAVAILABLE, ORDER_CANCELLED_ADMIN_REQUESTED
- **401**: AUTH_REQUIRED
- **403**: KYC_PERMISSION_DENIED, NO_DEPOSITS, ACCOUNT_UNVERIFIED, ACTION_BLOCKED, FORBIDDEN, RG_ACK_REQUIRED
- **429**: RATE_LIMIT_EXCEEDED
- **451**: COUNTRY_BLOCKED
- **500**: Internal server error
- **503**: CREATE_ORDER_TIMEOUT, KYC_SERVICE_UNAVAILABLE, ORDER_UNAVAILABLE, AUTH_UNAVAILABLE, KYC_SERVICE_INTERNAL_ERROR

## POST /v3/sessions/
**Summary:** Login using this route.
**Description:** ## Description
This will return a token that can be used in the Authentication header in the
form "Session-Token <your_token>" on authenticated requests.<br>
The token is valid for 30min, but if you make an authenticated request
with it, it will be renewed for the next 30min.

##  Rate limits
Maximum 5 requests per 300 seconds<br>

### Request Body Schema
```json
{
  "additionalProperties": false,
  "properties": {
    "create_social_member": {
      "description": "If true, and the user logging in does not have an associated social member,this call will also take care of creating the social member for this user",
      "example": true,
      "type": "boolean"
    },
    "password": {
      "description": "Your account password",
      "example": "verysecurepassword",
      "minLength": 1,
      "type": "string"
    },
    "remember": {
      "description": "True if the client wants Smarkets to allow\nthis device to renew the token even after its expiration",
      "example": true,
      "type": "boolean"
    },
    "reopen_account": {
      "description": "If true, and the user has closed their own account,then their account will be reopened and they will log in as normal.",
      "example": false,
      "type": "boolean"
    },
    "use_auth_v2": {
      "description": "If true, and the user logging will be forced to use auth v2,and should expect refresh_token and access_token in the cookies and response",
      "example": false,
      "type": "boolean"
    },
    "username": {
      "description": "Your username",
      "example": "john.doe@company.com",
      "format": "email",
      "type": "string"
    }
  },
  "required": [
    "password",
    "username"
  ],
  "title": "session_create",
  "type": "object"
}
```

### Responses
- **201**: Token response for old and new auth v2.
- **400**: INVALID_DEVICE_COOKIE, REQUEST_VALIDATION_ERROR
- **401**: INVALID_CREDENTIALS, PASSWORD_RESET_NEEDED
- **403**: DEVICE_NOT_TRUSTED, USER_SELF_SUSPENDED, IP_NOT_TRUSTED, CLIENT_JURISDICTION_MISMATCH, SOURCE_BLOCKED, USER_SUSPENDED, USER_EXCLUDED, SESSION_LIMIT_REACHED, USER_ON_TIMEOUT
- **429**: RATE_LIMIT_EXCEEDED
- **451**: COUNTRY_BLOCKED
- **500**: Internal server error
- **503**: AUTH_UNAVAILABLE, TIMEOUT


## Detailed: POST /v3/orders/ Request Body
This is the most used endpoint - placing bets. Schema details:

- `contract_id` (string, REQUIRED): This ID uniquely identifies the contract [e.g., 123456]
- `label` (string, optional): Label is a user-defined string that will be stored in the order.
It can be used to identify different trading strategies [e.g., strategy_1]
- `market_id` (string, REQUIRED): This ID uniquely identifies the market [e.g., 128939]
- `minimum_accepted_quantity` (integer, optional): 
If this minimum accepted quantity is not matched on bet placement time,
the order will be cancelled and nothing will be matched.<br>
Only applicable to immediate_or_cancel order types.
     [e.g., 10000]
- `price` (integer, REQUIRED): 
This price is in percentage basis points.<br>
Example: 5000 = 50% <br>
To convert it to decimal odds, just divide 10000 by it<br>
Example: 10000 / 5000 = 2.0 (decimal odds).<br>
This price has to conform to a valid tick on the exchange;
an invalid price error will be returned if it does not. [e.g., 5000]
- `quantity` (integer, REQUIRED): 
    Quantity is the sum of the total pot (back+lay) in case the order is matched<br>
    The units are 1/10000 * one unit of the user's currency.<br>
    Example: Quantity 500 = 0.05 GBP<br>
    To convert it to back stake, just multiply by the price and divide by 100000000<br>
    Example: 100000 (quantity) * 5000 (price) / 100000000 = 5 GBP back stake<br>
    The minimum stake is £0.05 or currency equivalent [e.g., 10000]
- `side` (string, REQUIRED): 
side can either be:<ul>
<li>buy: backing a contract
<li>sell: laying a contract
</ul> [e.g., buy] [one of: ['buy', 'sell']]
- `type` (string, optional): Order types can have the following values:
    <ul>
    <li>good_til_cancelled: this order will be open until a reduction
    factor is applied or a market state changes to live, which will cancel the order.
    <li>keep_in_play: the same as good_til_cancelled,
    except it will not be cancelled on market state changes
    <li>good_til_halted: the same as good_til_cancelled, except a market
    <li>immediate_or_cancel: if the minimum_accepted_quantity is not
    matched at the time of order placement, this order will be cancelled. 
    </ul>
    <p>The following table explains the lifetime of orders:</p>
    <table cellpadding="3" style="border: 1px solid white;">
      <tr>
        <th>order_type</th>
        <th>Market Goes Live</th>
        <th>Market Halted</th>
        <th>Reduction Factor Applied</th>
      </tr>
      <tr>
        <td>good_til_cancelled</td>
        <td>Cancelled</td>
        <td>Cancelled</td>
        <td>Cancelled</td>
      </tr>
      <tr>
        <td>good_til_halted</td>
        <td>Kept</td>
        <td>Cancelled</td>
        <td>Cancelled</td>
      </tr>
      <tr>
        <td>keep_in_play</td>
        <td>Kept</td>
        <td>Kept</td>
        <td>Cancelled</td>
      </tr>
    </table><br>
    <p>Orders marked as immediate_or_cancel must be executed
    immediately and thus will not remain in the book.</p>
     [e.g., good_til_halted] [one of: ['good_til_cancelled', 'keep_in_play', 'good_til_halted', 'immediate_or_cancel']]


## POST /v3/orders/ Response (200 Success)
- `available_balance` (string, REQUIRED): Current available balance on the account,
it is equal to the balance deducted by the exposure [e.g., 100.00]
- `available_quantity` (integer, REQUIRED): Quantity left to be matched in the order [e.g., 15000]
- `contract_id` (string, REQUIRED): This ID uniquely identifies the contract [e.g., 123456]
- `executed_avg_price` (integer, REQUIRED): The average price for the executions on the order [e.g., 5000]
- `exposure` (string, REQUIRED): Current exposure on the account [e.g., -50.00]
- `market_id` (string, REQUIRED): This ID uniquely identifies the market [e.g., 128939]
- `order_id` (string, REQUIRED): This ID uniquely identifies an order [e.g., 1518455672861]
- `orig_price` (integer, REQUIRED): The price at which the order was placed at, it can be different
from the matched price. This value will be null if there were no executions. [e.g., 5000]
- `price` (integer, REQUIRED): 
This price is in percentage basis points.<br>
Example: 5000 = 50% <br>
To convert it to decimal odds, just divide 10000 by it<br>
Example: 10000 / 5000 = 2.0 (decimal odds).<br>
This price has to conform to a valid tick on the exchange;
an invalid price error will be returned if it does not. [e.g., 5000]
- `quantity` (integer, REQUIRED): 
    Quantity is the sum of the total pot (back+lay) in case the order is matched<br>
    The units are 1/10000 * one unit of the user's currency.<br>
    Example: Quantity 500 = 0.05 GBP<br>
    To convert it to back stake, just multiply by the price and divide by 100000000<br>
    Example: 100000 (quantity) * 5000 (price) / 100000000 = 5 GBP back stake<br>
    The minimum stake is £0.05 or currency equivalent [e.g., 10000]
- `side` (string, REQUIRED): 
side can either be:<ul>
<li>buy: backing a contract
<li>sell: laying a contract
</ul> [e.g., buy] [one of: ['buy', 'sell']]
- `total_executed_quantity` (integer, REQUIRED): Quantity matched (executed) in the order [e.g., 15000]