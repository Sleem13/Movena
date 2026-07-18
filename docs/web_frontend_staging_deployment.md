# Web Frontend Staging Deployment

Create a restricted Vercel project rooted at `frontend/`. Set `VITE_API_BASE_URL` to the real Render HTTPS origin, then use `npm install` and `npm run build`; publish `dist/`. Non-development builds fail when the API URL is missing, so localhost cannot silently enter staging.

Set backend CORS to the exact Vercel origin only. Do not put secrets in Vite variables. After deployment test exercise metadata, upload, success/rejection results, auth, history, signed artifacts, offline/backend errors, and safety text. Inspect network requests for localhost and restrict Vercel deployment access where the plan supports it.

The local staging build is verified. Actual Vercel deployment is blocked because no Vercel project/token and no Render staging URL are available.
