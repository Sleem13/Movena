# Mobile Strategy

## Recommendation

Use **React Native with Expo** for the first mobile client because the current frontend is React, the team can reuse TypeScript/JavaScript skills, API models, validation helpers, design tokens, and testing conventions. Flutter remains viable if future staffing or performance requirements justify a separate Dart stack, but it creates more duplicated product logic today.

The first mobile architecture is thin-client capture and display:

```text
Mobile camera/library -> secure upload -> FastAPI processing -> result/artifact APIs -> mobile result view
```

Backend-side analysis keeps pose, validity, rule, threshold, and report versions consistent across web and mobile. Offline/on-device inference is deferred.

## Mobile MVP Screens

1. **Onboarding:** product scope, privacy summary, consent, and stop guidance.
2. **Login:** added only after secure identity/session APIs exist.
3. **Patient profile:** minimal preferences, consent, and accessibility controls.
4. **Exercise program:** assigned exercises with squat as the only initially active analyzer.
5. **Camera recording:** permission handling, guidance, capture/library selection, preview, trim, and replace.
6. **Upload/progress:** upload and server-processing states, retry, cancellation, and interruption recovery.
7. **Analysis result:** validity, movement observations, reps, score where meaningful, confidence, feedback, and limitations.
8. **Session history:** authorized filtering, expiration, deletion, and export.
9. **Report sharing:** explicit recipient, artifact, duration, and revocation where supported.
10. **Safety/about:** intended use, limitations, privacy, support, and stop guidance.

## Therapist Sharing

Reports should be shared through an authorized session link or user-initiated file export. Avoid public permanent URLs and implicit therapist access. The patient sees what is shared, with whom, for how long, and how to revoke access where supported.

## Mobile Engineering Requirements

- Secure token storage, certificate-valid HTTPS, no secrets bundled in the app, and no health/media content in analytics or crash breadcrumbs.
- Network-aware compression limits without altering movement timing.
- Codec/device test matrix and clear upload errors.
- Accessibility labels, dynamic text, contrast, reduced motion, orientation handling, and screen-reader testing.
- API contract generation or shared schemas to prevent web/mobile drift.
- Store descriptions and screenshots that avoid diagnostic or clinical-performance claims.

An Android-first internal or patient MVP is acceptable. Keep recordings short and use bounded, timing-preserving compression; enforce backend upload size/duration limits and explain failures before retry. Privacy and retention notices appear before video upload. Offline and on-device analysis remain future work.
