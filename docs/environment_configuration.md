# Environment configuration

Copy `.env.example` to `.env` for local reference and export values through the shell, container, or deployment platform. The application does not load or commit secret files automatically.

`APP_ENV`, `APP_VERSION`, `API_HOST`, `API_PORT`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`, `MAX_UPLOAD_SIZE_MB`, `ALLOWED_VIDEO_EXTENSIONS`, and `ARTIFACT_RETENTION_HOURS` control runtime behavior. Safe defaults are release version `0.12.0`, a 100 MB upload limit, supported MP4/MOV/AVI/MKV/WebM extensions, and 24-hour temporary artifact retention. Feature flags are `ENABLE_SESSION_HISTORY`, `ENABLE_THERAPIST_DASHBOARD`, `ENABLE_ML_SECOND_OPINION`, `ENABLE_REPORT_GENERATION`, and `ENABLE_OVERLAY_GENERATION`.

Development defaults permit the Vite/React ports 5173 and 3000 on localhost. Supply explicit HTTPS web origins in production; a wildcard is discarded in production. Expo devices normally use the computer's LAN address, such as `http://192.168.1.20:8000`, and that browser origin must be added only when applicable.

No real secrets belong in `.env.example`. SQLite is for local evaluation only.
