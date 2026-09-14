# Visit notes

From each scheduled or historical appointment, open Visit notes. The heading
keeps the appointment context. Clinicians see saved notes and an Add note action;
patients see only notes explicitly shared with them. All states use the normal
role permissions even where administrators share the clinician layout.

The editor has a required visit summary, optional recommendations and an unchecked
Share with patient checkbox. Explain that an unchecked note stays private to
authorized staff. Notes are appended, with author ID and localized date retained;
this journey does not edit or delete historical notes. Corrections are new notes.
Do not generate clinical observations or interpret the clinician's text.

Use a narrow form with growing text areas, wrapping actions and at least 48-point
touch targets. Preserve text line breaks. Render content as plain text, never HTML.
Arabic mirrors navigation and localizes labels/dates; notes retain their original
language. Support 200% native text scaling, light/dark surfaces and screen readers.

Loading shows a labeled indicator. Empty patient history says no shared notes;
empty staff history offers Add note. Read failures offer retry. Save failures
retain the draft and use the same submission key for the same payload. Ambiguous
failures freeze the submitted draft for an identical retry; the user can inspect
saved notes before attempting another note. A confirmed save closes the editor,
shows success and refreshes the list. Drafts remain in memory only.

The legacy service remains the authoritative writer. Two additive read endpoints
enforce appointment ownership, active clinician care access and patient-visible
filtering. Django rechecks object access before replaying a creation receipt.
Unresolved upstream writes remain a reconciliation/cutover gate; no automatic
retry may create a second note. Native OS and deployment acceptance remain separate.
