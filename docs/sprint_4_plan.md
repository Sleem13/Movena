# Sprint 4 Plan

## Theme

Visual Feedback and Therapist-Friendly Reporting.

## Goal

Make the existing rule-based squat result easier to understand and present by adding temporary annotated video, bounded frame-level metrics, therapist-friendly PDF export, camera guidance, and clearer frontend results.

## Scope

- Reuse extracted pose frames to draw a CPU-friendly eight-joint skeleton overlay.
- Return summary JSON by default and at most 300 sampled frame rows on request.
- Generate a temporary PDF report for each successful session.
- Serve artifacts through opaque UUID-based download routes with one-hour expiry.
- Display report download, optional overlay preview, camera guidance, metrics, observations, feedback, limitations, and explicit safety wording.

## Non-goals

No ML training, new exercise, authentication, database, permanent session history, clinical diagnosis, or architecture redesign.

## Acceptance Criteria

- Sprint 3 regression tests remain green.
- Real-video analysis returns its prior summary fields plus a downloadable PDF.
- `include_overlay=true` produces a non-empty annotated MP4 on a real fixture.
- `include_frame_data=true` returns bounded timestamps, angles, phase, and possible issue labels.
- Temporary source uploads are deleted; artifacts expire and invalid IDs cannot escape the artifact directory.
- Frontend tests cover camera guidance, result cards, report control, overlay section, safety notice, and API errors.
- Backend, frontend tests, production build, and dependency audits pass.

## Risks

- OpenCV `mp4v` output is portable for download but may not preview in every browser.
- Pose landmarks are available only on detected frames; other overlay frames remain unmarked.
- Frame warnings are visual heuristics, not diagnoses.
- A local TTL folder is suitable for the MVP but not multi-instance production hosting.
- PDF placeholders are not a clinical record system and contain no persistence or access controls.
