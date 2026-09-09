"""Add connection lifecycle and invitations without rewriting existing assignments."""
from alembic import op
import sqlalchemy as sa

revision = "0008_care_connections"
down_revision = "0007_exercise_response"
branch_labels = None
depends_on = None


def upgrade():
    from app.db.models import CareInvitation
    bind = op.get_bind()
    CareInvitation.__table__.create(bind, checkfirst=True)
    existing = {c["name"] for c in sa.inspect(bind).get_columns("therapist_patient_assignments")}
    for column in (
        sa.Column("source", sa.String(24), nullable=False, server_default="legacy"),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("ended_by_user_id", sa.String(36)),
        sa.Column("end_reason", sa.Text()),
    ):
        if column.name not in existing:
            op.add_column("therapist_patient_assignments", column)
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE care_invitations ENABLE ROW LEVEL SECURITY")
        roles = bind.execute(sa.text("SELECT rolname FROM pg_roles WHERE rolname IN ('anon', 'authenticated')"))
        for role in roles.scalars():
            op.execute(sa.text(f'REVOKE ALL ON TABLE care_invitations FROM "{role}"'))


def downgrade():
    # Clinical and connection history is retained on rollback.
    pass
