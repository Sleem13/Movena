# Scheduling journey — screen concepts and component specification

Use the shared Movena surfaces, type hierarchy and light/dark tokens.

Desktop concept: page heading with a Book appointment action, followed by a
two-column appointment layout and an expandable booking form. The implemented
form sits above the upcoming/history columns so its full slot grid has room.
Phones stack the form and cards. Therapist Schedule is a primary tab;
patients enter Appointments from Care/Account. Administrators enter through
Operations and retain the server's existing permissions.

Appointment card: localized date/time with device timezone, care participant,
delivery mode, status and payment state. Primary action is Join video visit when
the server reports can_join. Otherwise show when joining becomes available.
Cancellation opens a labeled reason form; completed/cancelled cards show history.
Staff can confirm or record completed/no-show status; role permission remains
enforced by the API. Rescheduling uses available times and retains the record ID.

Booking concept: active care connection → therapist-local calendar day → available
time (displayed in device timezone) → video/in-person → review and book. Web
previous/next-day buttons supplement the browser date picker. Retain the
same request identity during retries. Do not interpret a request timeout as success.
No appointment booking creates a payment charge. Empty connection/slot states
provide guidance; errors keep input and expose retry. Saved state refreshes the
schedule and displays the confirmed date/time.

Therapist availability: existing weekly windows and a weekday/start/end/timezone
form. Times are explicitly in the named IANA timezone. Invalid or reversed ranges
are rejected. The legacy API supports adding/listing windows, not deleting them;
do not invent deletion semantics during compatibility.

Video join: fetch a fresh short-lived grant only on user action. Validate HTTPS,
expiry and token before showing a web link or opening the native browser. Grants
are held in memory, never local storage or logs. Show an expired/unavailable state
with retry. Testing uses a stub provider; a live visit remains a deployment gate.

All controls use at least 48 logical pixels, visible labels and announced outcomes.
Forms scroll under enlarged text and keyboards. English/Arabic labels, RTL order,
localized dates, reduced motion, loading/empty/error/offline/completion states use
the same components as recovery. Record phone/tablet/desktop checks in STATUS.md.
