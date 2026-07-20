# Product Hardening Checklist Before Closed Pilot

## Privacy and Consent

- [ ] Privacy policy page exists.
- [ ] Consent screen exists before upload/analysis.
- [ ] User acknowledges system limitations.
- [ ] No real patient data policy is visible.
- [ ] Data deletion request process exists.
- [ ] Data export request process exists.

## Safety

- [ ] No diagnosis claims.
- [ ] No treatment prescription claims.
- [ ] Confidence and limitations shown in results.
- [ ] Invalid/static videos rejected safely.
- [ ] Planned exercises are disabled.
- [ ] Manual exercise selection remains primary.

## Security

- [ ] SECRET_KEY is not committed.
- [ ] DATABASE_URL is not committed.
- [ ] Supabase password is not committed.
- [ ] Render env variables are stored only in Render.
- [ ] Upload size limits are enforced.
- [ ] File cleanup policy is enabled.

## Monitoring

- [ ] Backend errors are logged.
- [ ] Failed analyses are tracked.
- [ ] Upload failures are tracked.
- [ ] Feedback form exists.
- [ ] Issue tracking file or system exists.

## Mobile

- [ ] Staging API URL configured.
- [ ] Android staging build tested.
- [ ] Auth flow tested.
- [ ] Upload flow tested.
- [ ] Result screen tested.
- [ ] Safety text visible.

## Closed Pilot Gate

- [ ] Tester onboarding document exists.
- [ ] Consent record template exists.
- [ ] Feedback form exists.
- [ ] Issue report template exists.
- [ ] Pilot GO/NO-GO decision document exists.
