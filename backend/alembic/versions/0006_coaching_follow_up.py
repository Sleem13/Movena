"""Add recovery coaching reminders and clinical follow-up acknowledgement.

Revision ID: 0006_coaching_follow_up
Revises: 0005_recovery_coaching
"""

from alembic import op
import sqlalchemy as sa

from app.db.database import Base
from app.db import models  # noqa: F401 - register current metadata


revision = "0006_coaching_follow_up"
down_revision = "0005_recovery_coaching"
branch_labels = None
depends_on = None


def _columns(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def _add(table: str, column: sa.Column) -> None:
    if column.name not in _columns(table):
        op.add_column(table, column)


def _index_if_missing(table: str, name: str, columns: list[str]) -> None:
    indexes = {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table)}
    if name not in indexes:
        op.create_index(name, table, columns)


def upgrade() -> None:
    table = "recovery_coaching_check_ins"
    _add(table, sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    _add(table, sa.Column("reviewed_by_user_id", sa.String(36), nullable=True))
    _add(table, sa.Column("review_disposition", sa.String(40), nullable=True))
    _add(table, sa.Column("review_note", sa.Text(), nullable=True))
    _index_if_missing(table, "ix_recovery_coaching_check_ins_reviewed_at", ["reviewed_at"])
    _index_if_missing(table, "ix_recovery_coaching_check_ins_reviewed_by_user_id", ["reviewed_by_user_id"])
    _index_if_missing(table, "ix_recovery_coaching_check_ins_review_disposition", ["review_disposition"])

    Base.metadata.tables["recovery_coaching_reminder_preferences"].create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    op.drop_table("recovery_coaching_reminder_preferences")
    for name in (
        "ix_recovery_coaching_check_ins_review_disposition",
        "ix_recovery_coaching_check_ins_reviewed_by_user_id",
        "ix_recovery_coaching_check_ins_reviewed_at",
    ):
        op.drop_index(name, table_name="recovery_coaching_check_ins")
    for column in ("review_note", "review_disposition", "reviewed_by_user_id", "reviewed_at"):
        op.drop_column("recovery_coaching_check_ins", column)
