"""Add platform-owned account projections and durable assertion replay protection."""
from alembic import op
import sqlalchemy as sa

revision = "0010_identity_projection"
down_revision = "0009_patient_profile_repair"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "identity_owner" not in {column["name"] for column in inspector.get_columns("users")}:
        op.add_column("users", sa.Column("identity_owner", sa.String(16), nullable=False, server_default="legacy"))
    if "internal_principal_nonces" not in inspector.get_table_names():
        op.create_table("internal_principal_nonces",
            sa.Column("jti", sa.String(64), primary_key=True),
            sa.Column("subject", sa.String(64), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=False))
        op.create_index("ix_internal_principal_nonces_expires_at", "internal_principal_nonces", ["expires_at"])


def downgrade():
    op.drop_index("ix_internal_principal_nonces_expires_at", table_name="internal_principal_nonces")
    op.drop_table("internal_principal_nonces")
    op.drop_column("users", "identity_owner")
