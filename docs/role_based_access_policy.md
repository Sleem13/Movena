# Role-Based Access Policy

- `researcher_demo`: owned/demo sessions only; no therapist resources.
- `patient`: owned sessions only; future profile linkage requires consent.
- `therapist`: therapist prototype and development patient/session resources.
- `admin`: local administrative access; public registration cannot create it.

Session routes require authentication. Patient/demo access is owner-scoped; therapist/admin access is broader for the local prototype. Therapist routes require therapist/admin. Analyze routes stay anonymous when `REQUIRE_AUTH_FOR_ANALYSIS=false`; anonymous persistence is refused unless `ENABLE_PUBLIC_DEMO_MODE=true`. Tokens grant no clinical authority.
