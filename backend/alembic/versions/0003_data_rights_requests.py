"""Add auditable privacy-rights requests.

Revision ID: 0003_data_rights
Revises: 0002_notification_queue
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_data_rights"
down_revision = "0002_notification_queue"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "data_rights_requests" not in inspector.get_table_names():
        op.create_table(
            "data_rights_requests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("request_id", sa.String(36), nullable=False),
            sa.Column("user_id", sa.String(36), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
            sa.Column("request_type", sa.String(24), nullable=False),
            sa.Column("status", sa.String(24), nullable=False, server_default="pending"),
            sa.Column("details", sa.Text()),
            sa.Column("resolution_note", sa.Text()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("completed_at", sa.DateTime(timezone=True)),
        )
        op.create_index("ix_data_rights_requests_request_id", "data_rights_requests", ["request_id"], unique=True)
        op.create_index("ix_data_rights_requests_user_id", "data_rights_requests", ["user_id"])
        op.create_index("ix_data_rights_requests_request_type", "data_rights_requests", ["request_type"])
        op.create_index("ix_data_rights_requests_status", "data_rights_requests", ["status"])


def downgrade() -> None:
    # Privacy-request records are audit evidence and are intentionally retained.
    pass
