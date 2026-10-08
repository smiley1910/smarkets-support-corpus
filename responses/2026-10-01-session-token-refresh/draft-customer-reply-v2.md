Your logs show what is happening.

The client sends the session token in the Authorization header only. Sessions renew through the refresh token issued at login; without it, no new session token is generated and requests carrying only the old one are rejected with AUTH_REQUIRED at the rotation point. That point is the twenty minute mark where every run has ended, and with the renewal in place the session continues past the thirty minute stop. This also corrects what we explained earlier: the session does not renew from your requests alone, which is why polling every twenty seconds did not keep it alive.

The login response returns both tokens in the body, token and refresh_token. Capture both, keep your current Authorization header, and add the Cookie header alongside it for every request after login:

Cookie: User-Session-Token=<token>; Refresh-Token=<refresh_token>

The server issues a new User-Session-Token automatically, as a Set-Cookie header on a poll response just after the twenty minute mark. Parse Set-Cookie on every response, and switch to the new value as soon as it changes, updating the cookie and the Authorization header together. Please run the timed test long enough to cross both marks, around thirty five minutes. Expect the session to hold at twenty minutes, a new User-Session-Token just after it, and the run to continue past the original stop. If a rejection appears, send the log around that moment with the response headers.

Kind regards,
Michael
Smarkets Support
