# External Beta Consent Tracking Protocol

> Invite-only beta only. No public release. No real patient data. No clinical use. No diagnosis or treatment claims. The beta is blocked until private staging, the Android build, physical-device QA, and active feedback/support links are ready.

## Boundary

Consent tracking is for a future invite-only beta only, not public release or clinical use. No real patient data, diagnosis, treatment information, or sensitive health information is permitted. Beta execution remains blocked until staging, Android build, physical-device QA, active feedback/support/privacy links, and approval are complete.

Use `data/processed/beta/external_beta_consent_tracker.csv`. It is header-only until a real invited tester reviews the approved, versioned consent. Do not pre-fill or infer acknowledgement.

## Required gate

A tester cannot receive assignments or upload until all are true:

- `consent_acknowledged`
- `data_handling_acknowledged`
- `no_real_patient_data_acknowledged`
- `safety_limitations_acknowledged`
- matching `consent_version`, app build, and timestamp
- `withdrawal_requested` is false

Acknowledgement must be an affirmative tester action against the exact approved text. Absence, ambiguity, an old version, or partial acknowledgement means blocked. The tracker stores a generated tester ID, not name/contact/health details.

On withdrawal, stop assignments, revoke access, document the request, review eligible beta records for deletion, confirm the outcome through the approved private channel, and keep only the minimum legally/operationally required audit record. A new consent version requires renewed acknowledgement before further testing.
