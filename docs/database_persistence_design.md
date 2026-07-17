# Database Persistence Design

## Configuration

SQLAlchemy 2.x is used with SQLite at `backend/physiovision_dev.db` by default. `DATABASE_URL` can select a future PostgreSQL deployment, for example `postgresql+psycopg://user:password@host/database`; a PostgreSQL driver is intentionally not part of the current local core environment.

The database initializes tables safely on backend startup and through `python scripts/init_database.py`. Tests create isolated temporary SQLite engines and do not depend on the developer database.

## Data Model

- `analysis_sessions`: normalized session identity, exercise/status, core scores/confidence, summaries, JSON snapshots, and artifact links.
- `session_metrics`: queryable numeric/text metrics such as angles, reps, and movement score.
- `detected_issues`: queryable issue codes with optional future severity/message fields.
- `uploaded_media`: upload metadata only; `stored_path` remains null because raw videos are deleted after analysis.

Relationships use session UUIDs and ORM delete cascades. Deleting a saved session removes metadata rows only; it does not delete independently managed report or overlay artifacts.

## Failure Isolation

Persistence is opt-in. Database errors are rolled back, logged, and converted to `Session could not be saved.` in the analysis response. The movement result still returns unless a future explicitly strict mode is introduced.

JSON snapshots keep evolving analysis structures backward-compatible while separate tables preserve useful filtering targets. A production migration system such as Alembic is deferred.
