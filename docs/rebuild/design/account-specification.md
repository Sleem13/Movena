# Account journey specification

Use the Movena split welcome/form layout on desktop and a scrolling single column
on phones. Registration, email verification and password reset use dedicated pages
with the same labels, error region and primary action. Flutter uses a dedicated
route for each action and keeps request state in an account view model.

Registration collects name, username, email and password, with separate unchecked
terms/privacy consent controls. Patient is the requested public role; privileged
roles remain unavailable to public registration. Preserve backend consent versions
and verification state. Registration does not silently sign in. Delivery failure
retains a resend entrypoint because the account may already exist.

Verification consumes a supplied token only when the user chooses Verify. Reset
requires a new password and matching confirmation, then returns to login. Read
tokens from the existing email-link query or fragment and immediately remove them
from the address bar. Keep tokens in memory only. Never log tokens or passwords.
Native movena://verify-email and movena://reset-password links open these forms.
Production email origin and universal-link associations require deployment setup.

Loading disables repeated submissions. Errors retain input for retry. Success
clears passwords/tokens. Expired links offer resend or a fresh reset request.
Forgot/resend messages never reveal account existence. Offline is not delivery.
Use 48-pixel targets, text scaling, RTL and light/dark variants.

Operator-approved terms/privacy URLs must be configured before public registration
cutover. Preserve existing consent records without inventing legal terms.
