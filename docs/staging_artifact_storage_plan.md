# Staging Artifact and Media Storage Plan

Uploaded videos are written to `backend/tmp/uploads` only during processing and removed in endpoint `finally` blocks. Reports and overlays are written under `backend/artifacts/reports` and `backend/artifacts/overlays`. Session rows may store non-sensitive media metadata and the source filename; staging testers must use non-identifying filenames.

For internal single-instance staging, local backend storage is acceptable for at most 24 hours. Artifacts can disappear during deploy/restart, are not durable records, and cannot support multiple instances. When protected analysis is enabled, returned artifact URLs contain an expiring HMAC signature or require a valid bearer-authenticated request. IDs alone do not grant staging access.

Run cleanup at least hourly through the platform scheduler:

```powershell
python scripts/cleanup_artifacts.py --dry-run --retention-hours 24
python scripts/cleanup_artifacts.py --retention-hours 24
```

Review the dry-run output before enabling the scheduled deletion. The script only traverses report/overlay subdirectories and skips symlinks. Monitor disk usage and failed cleanup jobs without logging tokens, URLs with signatures, filenames, or raw media.

Before external testing, replace local storage with private S3-compatible object storage, server-side encryption, short-lived signed URLs, per-user authorization, deletion/audit operations, and a documented retention/legal basis.
