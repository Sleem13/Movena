# Data rights journey

## Patient

The Account screen links to **Privacy and data**. The screen explains the three
request types (export, correction, deletion), shows the patient's previous
requests, and makes the irreversible effect of an approved deletion clear before
submission. A submitted request appears immediately with its current status.

Loading, empty, validation, offline/error, duplicate-open, and completion states
are explicit. Submission uses a retry-safe key. Dates use the selected locale,
and status is never conveyed by colour alone.

## Administrator

Protected super administrators see **Data rights requests** in Operations. Each
row includes the account name and email, request type, details, date, and status.
Pending requests require a reason before Approve or Reject is enabled. Approved
deletion requests display their retention deadline. Ordinary administrators do
not receive this control.

## Components

- `DataRightsHistory`: responsive list of patient-owned requests.
- `DataRightsRequestForm`: type selector, optional details, deletion notice, and
  primary submit action.
- `DataRightsQueue`: protected operational queue with per-row review controls.
- `StatusBadge`: localized text plus a semantic status token.

All controls retain a minimum 48-point target. Layout uses logical CSS/Flutter
direction so Arabic reverses naturally. Screen-reader announcements cover load,
failure, submission, and review completion. Motion follows reduced-motion
preferences.
