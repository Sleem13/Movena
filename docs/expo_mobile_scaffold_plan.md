# Expo mobile scaffold plan

Recommended stack: React Native, Expo, TypeScript, Expo Router, and a small typed API client.

Planned screens are onboarding and safety, exercise selection, camera/video picker, upload progress, result summary, session history, and safety/about. Store the backend URL in Expo environment configuration. Upload a short local video as multipart form data, show cancellation/retry state, then render the returned summary and expiring artifact links.

Begin with Android physical-device testing over a trusted LAN. Add iOS testing after the upload lifecycle is stable. Do not persist videos by default. Authentication and protected storage must precede real patient data. On-device analysis remains deferred.
