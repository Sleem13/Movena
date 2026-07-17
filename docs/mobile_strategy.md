# Mobile Strategy

## Roadmap position

The mobile MVP is Sprint 16, not the immediate next step. It follows Sprint 12 API hardening, Sprint 13 authentication/roles/privacy, Sprint 14 multi-dataset ML/DL architecture, and Sprint 15 dataset adapters. This sequence stabilizes identity, access, data boundaries, and API contracts before a mobile client increases reach and data capture.

## Recommended architecture

Use React Native with Expo. The current React experience makes TypeScript models, API concepts, design tokens, and test conventions easier to reuse. The first mobile client is a thin capture/display client:

```text
Mobile camera or picker → authenticated upload → FastAPI analysis → result/artifact APIs → result screen
```

Analysis remains backend-side initially so validity, rule versions, safety wording, and reporting stay consistent. On-device pose or biomechanics analysis is future work requiring a separate performance, device-compatibility, privacy, and validation program.

## Sprint 16 MVP screens

1. Login and explicitly limited demo mode.
2. Exercise selection showing only supported analyzers.
3. Camera/video picker with recording guidance and consent notice.
4. Upload progress, cancellation, retry, and clean errors.
5. Result summary with validity, reps, score where meaningful, confidence, feedback, and limitations.
6. Authorized session history.
7. Safety/about page with intended use and stop guidance.

Current active choices are bodyweight squat and sit-to-stand only. Planned exercises must not be shown as available.

## Security and privacy gate

Before remote use: token security, role-based authorization, HTTPS, consent, retention/deletion controls, protected artifacts, no health/media details in analytics, and privacy-reviewed storage are required. A physical Expo device uses a LAN-reachable backend URL during development; `127.0.0.1` refers to the device itself.
