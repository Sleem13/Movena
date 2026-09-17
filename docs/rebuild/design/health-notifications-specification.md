# Patient health profile and notifications

## Screen concepts before implementation

Account → Health profile presents an optional emergency contact followed by
medical summary and precautions. A single prominent Save action commits the
explicitly edited fields. An empty field means unavailable; clearing a saved
field sends null. The form does not suggest diagnoses or change clinician plans.
Consent history below the form shows recorded type, version, acceptance and date.
Consent changes require the corresponding approved policy content; this stage
displays existing records only.

Today and Account → Notifications opens a newest-first inbox. Unread messages
have a teal indicator and an explicit Mark as read action. Reading never follows
an arbitrary action URL. Recognized legacy workspace destinations map to their
replacement; unsupported actions remain text until their journey is replaced.
Notification content authored by people/services is preserved verbatim.

## Components and states

- White/dark surface panels, bold headings, blue actions, logical spacing, 48-unit
  targets, EN/AR labels and localized date formatting.
- Loading occupies the content region. Initial errors expose Retry. Empty inbox
  and absent consent history have distinct explanatory text.
- Save/read requests disable only their affected controls. Failures retain form
  input and unread state; success is announced through a status region or snackbar.
- Do not persist health information or notification bodies in local preferences.
  Expired authentication returns to sign-in through the existing session layer.
- Patient endpoints remain patient-only. Object ownership is enforced by the
  authoritative legacy service through v2; test cross-user notification IDs.
- The current backend caps the inbox at 100 entries. Do not imply complete
  notification history or introduce a client-only deletion control.

## Acceptance

Save → reload preserves text; clearing fields yields null. Therapist requests are
denied. Marking one notification read leaves others unchanged and cannot mutate
another account's message. Arabic dark phone layouts remain usable at 200% text.
No patient data is used in screenshots or fixtures.
