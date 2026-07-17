# Sprint 11 — Therapist Dashboard MVP

Sprint 11 adds development-only placeholder profiles, assignment of saved analysis sessions, aggregate progress summaries, therapist review APIs, and a lightweight frontend workspace. It does not add authentication, clinical records, diagnosis, or automated clinical decision-making.

The dashboard summarizes saved squat and sit-to-stand sessions, issue codes, confidence warnings, scores, and artifact links. Rule-based analysis remains primary; squat ML remains experimental and sit-to-stand ML remains unavailable.

```powershell
python scripts/init_database.py
python -m pytest
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Use placeholder names such as `Demo Profile A`. Do not enter real patient identifiers, diagnoses, or health information. Production use requires authentication, authorization, consent, encryption, secure storage, audit logs, retention controls, and formal privacy/security review.
