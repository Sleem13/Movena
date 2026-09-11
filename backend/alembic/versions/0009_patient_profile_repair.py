"""Backfill patient profiles missing after legacy account migration."""
from datetime import datetime, timezone
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "0009_patient_profile_repair"
down_revision = "0008_care_connections"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    users = sa.table(
        "users",
        sa.column("user_id", sa.String),
        sa.column("username", sa.String),
        sa.column("email", sa.String),
        sa.column("full_name", sa.String),
        sa.column("role", sa.String),
    )
    profiles = sa.table(
        "patient_profiles",
        sa.column("patient_id", sa.String),
        sa.column("user_id", sa.String),
        sa.column("display_name", sa.String),
        sa.column("preferred_locale", sa.String),
        sa.column("timezone_name", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    missing = bind.execute(
        sa.select(users.c.user_id, users.c.username, users.c.email, users.c.full_name)
        .where(users.c.role == "patient")
        .where(~sa.select(profiles.c.user_id).where(profiles.c.user_id == users.c.user_id).exists())
    ).mappings().all()
    now = datetime.now(timezone.utc)
    for user in missing:
        display_name = user.full_name or user.username or (user.email or "").split("@", 1)[0] or "Patient"
        bind.execute(profiles.insert().values(
            patient_id=str(uuid4()), user_id=user.user_id, display_name=display_name,
            preferred_locale="ar", timezone_name="Africa/Cairo", created_at=now, updated_at=now,
        ))


def downgrade():
    # Repaired clinical identities are retained because they may gain clinical data.
    pass
