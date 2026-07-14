# Mobile Strategy

## Recommendation

Use **React Native with Expo** for the first mobile client because the current frontend is React, the team can reuse TypeScript/JavaScript skills, API models, validation helpers, design tokens, and testing conventions. Flutter remains viable if future staffing or performance requirements justify a separate Dart stack, but it creates more duplicated product logic today.

The first mobile architecture is thin-client capture and display:

```text
Mobile camera/library -> secure upload -> FastAPI processing -> result/artifact APIs -> mobile result view
```

Backend-side analysis keeps pose, validity, rule, threshold, and report versions consistent across web and mobile. Offline/on-device inference is deferred.

## Mobile MVP Screens

1. **Welcome and safety:** product scope, privacy summary, consent, and stop guidance.
2. **Exercise list:** squat active; future exercises visibly unavailable rather than simulated.
3. **Recording guide:** supported view, stable camera, lighting, clothing, full-body framing, and repetitions.
4. **Camera/upload:** permission handling, capture or library selection, preview, trim, replace, and retention choice.
5. **Processing:** upload and server-processing states, retry, cancellation, and background-interruption recovery.
6. **Result:** validity, movement observations, repetition count, score where meaningful, confidence, feedback, limitations, and annotated video/report links.
7. **Session history:** only after authenticated persistence exists; filtering, expiration, delete, and export.
8. **Settings/safety:** accessibility, permissions, privacy controls, support, and educational-use disclaimer.

## Therapist Sharing

Reports should be shared through an authorized session link or user-initiated file export. Avoid public permanent URLs and implicit therapist access. The patient sees what is shared, with whom, for how long, and how to revoke access where supported.

## Mobile Engineering Requirements

- Secure token storage, certificate-valid HTTPS, no secrets bundled in the app, and no health/media content in analytics or crash breadcrumbs.
- Network-aware compression limits without altering movement timing.
- Codec/device test matrix and clear upload errors.
- Accessibility labels, dynamic text, contrast, reduced motion, orientation handling, and screen-reader testing.
- API contract generation or shared schemas to prevent web/mobile drift.
- Store descriptions and screenshots that avoid diagnostic or clinical-performance claims.

