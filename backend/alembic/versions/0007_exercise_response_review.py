"""Add closed-loop exercise response review.

Revision ID: 0007_exercise_response
Revises: 0006_coaching_follow_up
"""

from alembic import op
import sqlalchemy as sa


revision = "0007_exercise_response"
down_revision = "0006_coaching_follow_up"
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
    table = "adherence_entries"
    _add(table, sa.Column("perceived_exertion", sa.Integer(), nullable=True))
    _add(table, sa.Column("symptoms_changed", sa.Boolean(), nullable=False, server_default=sa.false()))
    _add(table, sa.Column("stopped_due_to_symptoms", sa.Boolean(), nullable=False, server_default=sa.false()))
    _add(table, sa.Column("symptom_flags_json", sa.Text(), nullable=False, server_default="[]"))
    _add(table, sa.Column("response_state", sa.String(32), nullable=False, server_default="not_assessed"))
    _add(table, sa.Column("supportive_instruction", sa.Text(), nullable=True))
    _add(table, sa.Column("clinician_review_required", sa.Boolean(), nullable=False, server_default=sa.false()))
    _add(table, sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    _add(table, sa.Column("reviewed_by_user_id", sa.String(36), nullable=True))
    _add(table, sa.Column("review_disposition", sa.String(40), nullable=True))
    _add(table, sa.Column("review_note", sa.Text(), nullable=True))
    _index_if_missing(table, "ix_adherence_entries_response_state", ["response_state"])
    _index_if_missing(table, "ix_adherence_entries_clinician_review_required", ["clinician_review_required"])
    _index_if_missing(table, "ix_adherence_entries_reviewed_by_user_id", ["reviewed_by_user_id"])
    _index_if_missing(table, "ix_adherence_entries_review_disposition", ["review_disposition"])
    if op.get_bind().dialect.name == "postgresql":
        checks = {constraint["name"] for constraint in sa.inspect(op.get_bind()).get_check_constraints(table)}
        if "ck_perceived_exertion" not in checks:
            op.create_check_constraint(
                "ck_perceived_exertion", table,
                "perceived_exertion IS NULL OR (perceived_exertion >= 0 AND perceived_exertion <= 10)",
            )


def downgrade() -> None:
    table = "adherence_entries"
    if op.get_bind().dialect.name == "postgresql":
        checks = {constraint["name"] for constraint in sa.inspect(op.get_bind()).get_check_constraints(table)}
        if "ck_perceived_exertion" in checks:
            op.drop_constraint("ck_perceived_exertion", table, type_="check")
    for name in (
        "ix_adherence_entries_review_disposition", "ix_adherence_entries_reviewed_by_user_id",
        "ix_adherence_entries_clinician_review_required", "ix_adherence_entries_response_state",
    ):
        op.drop_index(name, table_name=table)
    for column in (
        "review_note", "review_disposition", "reviewed_by_user_id", "reviewed_at",
        "clinician_review_required", "supportive_instruction", "response_state",
        "symptom_flags_json", "stopped_due_to_symptoms", "symptoms_changed", "perceived_exertion",
    ):
        op.drop_column(table, column)
