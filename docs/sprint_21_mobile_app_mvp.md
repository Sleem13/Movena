# Sprint 21 — Mobile App MVP

## Delivered scope

Sprint 21 adds an isolated `mobile/` Expo Router application using React Native and TypeScript. It consumes the Sprint 20 exercise metadata API and the five existing analyzer endpoints. The app does not perform pose estimation, biomechanics analysis, exercise recognition, or ML/DL on-device.

## App flow

Onboarding → Exercise Library → Exercise Details → Camera Guidance → Video Selection/Recording → Upload → Result. Separate routes provide protected session history, login/registration/profile, and safety/privacy information.

The library loads `GET /api/v1/exercises`, permits only records with `supported_in_app=true`, and renders planned exercises disabled. Guidance uses the backend metadata's camera view, required landmarks, expected movement, and safety note.

## Upload and result behavior

`expo-image-picker` selects an existing video or records through the platform camera. Camera recordings request a 60-second maximum where supported, and files known to exceed 100 MB are blocked before upload. React Native `XMLHttpRequest` sends a `video` multipart field, adds an optional bearer token, and reports transfer progress.

The result contract tolerates exercise-specific and missing fields. Rejected results never display a movement score or ML panel; they show the rejection reason, validation warnings, and recording improvements. Success results show reps, score when present, confidence, pose quality, observations, feedback, limitations, and temporary artifact links.

## Authentication and history

JWTs are stored only in `expo-secure-store`. Login, public demo registration, profile/logout, session list/filter, and session detail use existing backend endpoints. Logout clears the device token; refresh tokens and server-side revocation are not implemented.

## Safety boundary

Manual exercise selection and rule-based analysis remain primary. Recognition and ML/DL remain experimental. The app describes observed movement patterns, possible compensation, limited observed range, and confidence. It does not diagnose, detect injury or weakness, prescribe treatment, or determine that an exercise is safe.

Do not enter real patient-identifiable information. This development app and its local backend are not medical-record infrastructure.

## Validation commands

```powershell
cd mobile
npm install
npx expo install --check
npm test
npm run typecheck
npx expo start

cd ..
.\.venv\Scripts\python.exe -m pytest
```
