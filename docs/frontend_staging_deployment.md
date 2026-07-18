# Frontend Staging Deployment

Deploy `frontend/` to Vercel or Netlify as an internal staging site. Configure `VITE_API_BASE_URL` to the HTTPS backend origin before building. Non-development builds now fail closed if this value is absent; localhost fallback exists only in Vite development/test mode.

```powershell
cd frontend
npm install
$env:VITE_API_BASE_URL="https://staging-api.example.com"
npm test
npm run build
```

The backend `CORS_ALLOWED_ORIGINS` must include the exact deployed web origin, without wildcard, path, or trailing slash. Do not put secrets in `VITE_*`; Vite embeds them in public browser code.

After deployment verify the app shell, exercise library, each supported details/guidance route, analysis upload, success/rejection results, login/logout, session history, artifact links, network errors, and the safety disclaimer. Inspect browser logs and network requests for tokens, stack traces, localhost URLs, signed artifact query logging, or identifying filenames.
