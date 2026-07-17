# Sprint 10 — Sessions, Database, and History

## Outcome

Sprint 10 adds opt-in persistence of analysis metadata for bodyweight squat and sit-to-stand. A saved session can be listed, reopened, filtered, and deleted through the API and the frontend History page. Analyzer logic, validity gates, rule scoring, ML behavior, and temporary artifact handling are unchanged.

## Local Workflow

```powershell
python scripts/init_database.py
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Set `save_session=true` on either analysis endpoint, or enable **Save session history** on the Analyze page. The returned `session_id` links the result to `GET /api/v1/sessions/{session_id}`.

## Safety Boundary

This sprint stores analysis metadata, not clinical records. Raw uploaded videos are not retained by session persistence. There is no authentication, authorization, consent workflow, tenant isolation, encryption management, audit trail, or production media store. Do not enter names, diagnoses, contact information, or other personally identifiable patient data.

Production use requires authentication, consent, encryption, secure backups and media storage, retention policy, access logging, deletion workflows, and formal privacy/security review.
