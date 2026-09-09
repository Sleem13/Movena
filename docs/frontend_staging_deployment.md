# Frontend Staging Deployment

Deploy `frontend/` to Vercel, Netlify, or the AWS CloudFront staging stack as an internal staging site. Configure `VITE_API_BASE_URL` to the HTTPS backend origin before building. Non-development builds now fail closed if this value is absent; localhost fallback exists only in Vite development/test mode.

```powershell
cd frontend
npm install
$env:VITE_API_BASE_URL="https://name-movena-api-staging.onrender.com"
npm test
npm run build
```

The backend `CORS_ALLOWED_ORIGINS` must include each exact browser frontend origin, without wildcard, path, or trailing slash. Do not list the API hostname unless it is also serving browser pages. For a new Movena staging frontend and the current CloudFront staging frontend, configure this value in the backend environment:

```text
CORS_ALLOWED_ORIGINS=https://name-movena-web-staging.onrender.com,https://d139746brwkxwp.cloudfront.net
```

Render does not import the repository's `.env.staging.example` automatically. Save environment-variable changes in the provider dashboard and redeploy the backend before testing the browser upload again. Keep `ENABLE_EXERCISE_RECOGNITION=true` when the video identifier should be available at `/api/v1/recognition/models` and `/api/v1/recognition/video`. Do not put secrets in `VITE_*`; Vite embeds them in public browser code.

## 2026-09-09 Deployment Diagnosis

- `https://physio-vision-ai.vercel.app` serves the Movena frontend, but its current bundle is built against `https://name-physiovision-api-staging.onrender.com`.
- `https://name-physiovision-api-staging.onrender.com` responds on `/health`, `/ready`, and `/api/v1/exercises`; gait, balance, shoulder flexion, and hammer curl are marked supported there.
- The same Render backend returns `404` for `/api/v1/recognition/models` when `ENABLE_EXERCISE_RECOGNITION=false`, so the video identifier does not appear as available.
- `https://name-movena-api-staging.onrender.com` was not live during this check and returned `404`; do not use it until the provider hostname is actually created or renamed.
- `https://d139746brwkxwp.cloudfront.net` serves an older frontend bundle and returns `503` for backend paths while the AWS backend is unavailable or suspended.

After deployment verify the app shell, exercise library, each supported details/guidance route, analysis upload, success/rejection results, login/logout, session history, artifact links, network errors, and the safety disclaimer. Inspect browser logs and network requests for tokens, stack traces, localhost URLs, signed artifact query logging, or identifying filenames.
