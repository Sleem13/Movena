# Mobile deployment strategy

The existing HTTPS-ready REST boundary can support a future mobile client without moving pose analysis onto the device. During Expo development, configure the API base URL to the backend computer's reachable LAN address; `127.0.0.1` on a phone points to the phone itself.

An initial deployment should keep short video processing server-side, return compact summaries by default, expose expiring report/overlay URLs, and retry uploads carefully. Authentication, per-user authorization, consent, encryption, rate limits, secure object storage, and deletion policy are prerequisites for real participant or patient use.

On-device inference is deferred because model packaging, battery/thermal cost, device variance, validation, and update governance require a dedicated milestone.
