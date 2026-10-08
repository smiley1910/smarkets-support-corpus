Your logs identify the cause.

Your client authenticates with the session token in the Authorization header only. Sessions renew through the refresh token issued at login, and your client is not sending it, so the renewal cannot complete. When the session reaches its renewal point the original token is rejected with AUTH_REQUIRED. That is why every run ends at about twenty minutes, ahead of the thirty minute stop value, even though polling continues every twenty seconds.

The login response includes both tokens in the body and sets them as cookies. Capture both and send them with each request:

Cookie: User-Session-Token=<token>; Refresh-Token=<refresh_token>

When a new User-Session-Token is issued, use it for subsequent requests. Include the response cookies in your logging so the renewals are visible.

Please run the same timed test with this in place and let us know the result.

Kind regards,
Michael
Smarkets Support
