# Recovery journey component specification

Reference: `role-workspaces.png`. This specification covers the initial connected
recovery slice; it does not stand in for designs of unreplaced journeys.

| Screen | Structure and primary action | State behavior |
|---|---|---|
| Sign in | Movena wordmark, email/username, password, recovery, language | Disable duplicate submit; announce failures; never persist passwords |
| Today | Date, plan title, completed count, next exercise, assigned list, care link | Loading region; empty plan guidance; retry on failure; completed items stay accessible |
| Check-in | Prescription and precautions, recording action, response form, save | Preserve existing response values; optional scores remain unavailable; symptom guidance requires acknowledgement; saved confirmation returns to Today |
| Analysis | Exercise, recording/selection, playback, submit, progress, result | Preserve submission key on uncertain retry; distinguish rejection/error/success; return only a successful saved session to check-in |
| Patients | Searchable connected patients, invitation form, review entry | Empty connections, error/retry, invitation confirmation; server enforces relationships |
| Review | Patient selector, dated responses, symptoms, linked session, review form | Show review form only where review is required; all five dispositions; rationale required for no change; clinician attestation; saved review |

Shared components: 48 CSS-pixel / logical-pixel minimum actions; 12-pixel controls
and 20-pixel surface radii; blue primary actions and teal completion accents from
the shared token catalog. All form controls have visible labels. Status messages
are announced. Fields retain values after failed requests. Double submit is
disabled. No health response or access token is stored in browser local storage.

Web: four destination sidebar on desktop, bottom navigation on phones; content
has a readable maximum width, with single-column forms on narrow screens.
Native: Material controls, SafeArea, scrollable forms and keyboard avoidance.
Arabic mirrors navigation and reads shared translations; user/clinician content
is preserved as authored. Dates and numeric summaries use locale formatting.
Dark mode uses coordinated surfaces and contrast; reduced motion disables
decorative transitions. Verify at 320, 390, tablet and desktop widths, with
screen-reader semantics and enlarged text before cutover.

Offline: show a recoverable connection error; do not claim that a mutation saved
until confirmed. Interrupted uploads with unknown server outcome must retain the
same submission key. Receipt reconciliation and cross-launch resume remain
cutover requirements; they are not simulated by a progress animation.

Check-in symptom editing: show the existing eight symptom flags as a labeled
checkbox group beneath changed/stopped symptoms. Preserve checked values when
reopening, allow explicit corrections, and require the existing safety
acknowledgement whenever any symptom flag, changed symptoms or stopping is
reported. Do not pre-check acknowledgement or infer symptoms from a score.
Changes use the existing clinician-review workflow and server validation.
