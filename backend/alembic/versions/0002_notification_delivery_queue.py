"""Add durable email retry state to notifications.

Revision ID: 0002_notification_queue
Revises: 0001_care_platform
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_notification_queue"
down_revision = "0001_care_platform"
branch_labels = None
depends_on = None


def _columns(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    existing = _columns("notifications")
    additions = (
        ("email_required", sa.Boolean(), False, "1"),
        ("email_attempts", sa.Integer(), False, "0"),
        ("next_email_attempt_at", sa.DateTime(timezone=True), True, None),
        ("last_email_error", sa.Text(), True, None),
    )
    for name, column_type, nullable, default in additions:
        if name not in existing:
            op.add_column("notifications", sa.Column(name, column_type, nullable=nullable, server_default=default))
    op.create_index(
        "ix_notifications_next_email_attempt_at", "notifications", ["next_email_attempt_at"],
        unique=False, if_not_exists=True,
    )


def downgrade() -> None:
    # Delivery history is operational evidence; do not destructively remove it.
    pass
