# External Beta Feedback Form

Use the machine-readable template at `data/processed/beta/external_beta_feedback_template.csv`. One row represents one testing session. Use a beta alias and generated feedback ID; do not enter a name, email, diagnosis, symptoms, health history, patient identifier, raw token, secret, or identifiable video link.

Tester-facing form: `[PRIVATE FEEDBACK LINK — REQUIRED BEFORE GO]`. Privacy/safety concerns must use `[PRIVATE INCIDENT CONTACT]` rather than ordinary form attachments.

## Tester questions

1. Confirm consent and the test-only/no-patient-data rule.
2. Record date, beta alias, device/OS, app build, backend environment, selected exercise, and whether the source was a new self-test or supplied fixture.
3. Did upload succeed? Was analysis `success`, `rejected`, or `error`?
4. If rejected, was the explanation clear?
5. Were the result, confidence, camera guidance, safety disclaimer, and known limitations clear?
6. Choose an issue type and severity if applicable; describe product behavior only.
7. Did you observe a privacy/safety concern? If yes, stop and use the private escalation channel.
8. Suggest an improvement and indicate whether follow-up is needed.

Allowed severity values are `safety_privacy`, `blocker`, `high`, `medium`, `low`, and `none`. Do not attach screenshots/video by default. If requested through an approved channel, first remove personal information and confirm the content follows the beta data policy.
