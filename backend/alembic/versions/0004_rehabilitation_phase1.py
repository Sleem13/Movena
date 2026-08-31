"""Complete Phase 1 rehabilitation dosage and analysis linkage.

Revision ID: 0004_rehab_phase1
Revises: 0003_data_rights
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_rehab_phase1"
down_revision = "0003_data_rights"
branch_labels = None
depends_on = None


def _columns(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def _add(table: str, column: sa.Column) -> None:
    if column.name not in _columns(table):
        op.add_column(table, column)


def upgrade() -> None:
    _add("exercise_plan_items", sa.Column("rest_interval_seconds", sa.Integer(), nullable=True))
    _add("exercise_plan_items", sa.Column("tempo", sa.String(64), nullable=True))
    _add("exercise_plan_items", sa.Column("target_rom_degrees", sa.Float(), nullable=True))
    _add("exercise_plan_items", sa.Column("target_score", sa.Float(), nullable=True))
    _add("exercise_plan_items", sa.Column("requires_ai_analysis", sa.Boolean(), nullable=False, server_default=sa.false()))
    _add("exercise_plan_items", sa.Column("status", sa.String(24), nullable=False, server_default="active"))
    _add("adherence_entries", sa.Column("fatigue", sa.Integer(), nullable=True))
    _add("adherence_entries", sa.Column("analysis_session_id", sa.String(36), nullable=True))
    _add("analysis_sessions", sa.Column("plan_item_id", sa.String(36), nullable=True))

    inspector = sa.inspect(op.get_bind())
    indexes = {index["name"] for index in inspector.get_indexes("analysis_sessions")}
    if "ix_analysis_sessions_plan_item_id" not in indexes:
        op.create_index("ix_analysis_sessions_plan_item_id", "analysis_sessions", ["plan_item_id"])
    indexes = {index["name"] for index in sa.inspect(op.get_bind()).get_indexes("adherence_entries")}
    if "ix_adherence_entries_analysis_session_id" not in indexes:
        op.create_index("ix_adherence_entries_analysis_session_id", "adherence_entries", ["analysis_session_id"])
    indexes = {index["name"] for index in sa.inspect(op.get_bind()).get_indexes("exercise_plan_items")}
    if "ix_exercise_plan_items_status" not in indexes:
        op.create_index("ix_exercise_plan_items_status", "exercise_plan_items", ["status"])

    if op.get_bind().dialect.name == "postgresql":
        adherence_foreign_keys = {
            constraint.get("name")
            for constraint in sa.inspect(op.get_bind()).get_foreign_keys("adherence_entries")
        }
        if "fk_adherence_entries_analysis_session" not in adherence_foreign_keys:
            op.create_foreign_key(
                "fk_adherence_entries_analysis_session", "adherence_entries", "analysis_sessions",
                ["analysis_session_id"], ["session_id"], ondelete="SET NULL",
            )
        analysis_foreign_keys = {
            constraint.get("name")
            for constraint in sa.inspect(op.get_bind()).get_foreign_keys("analysis_sessions")
        }
        if "fk_analysis_sessions_plan_item" not in analysis_foreign_keys:
            op.create_foreign_key(
                "fk_analysis_sessions_plan_item", "analysis_sessions", "exercise_plan_items",
                ["plan_item_id"], ["item_id"], ondelete="SET NULL",
            )


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "postgresql":
        op.drop_constraint("fk_analysis_sessions_plan_item", "analysis_sessions", type_="foreignkey")
        op.drop_constraint("fk_adherence_entries_analysis_session", "adherence_entries", type_="foreignkey")
    op.drop_index("ix_exercise_plan_items_status", table_name="exercise_plan_items")
    op.drop_index("ix_adherence_entries_analysis_session_id", table_name="adherence_entries")
    op.drop_index("ix_analysis_sessions_plan_item_id", table_name="analysis_sessions")
    for column in ("status", "requires_ai_analysis", "target_score", "target_rom_degrees", "tempo", "rest_interval_seconds"):
        op.drop_column("exercise_plan_items", column)
    if dialect == "sqlite":
        inspector = sa.inspect(op.get_bind())
        adherence_fks = {constraint.get("name") for constraint in inspector.get_foreign_keys("adherence_entries")}
        adherence_checks = {constraint.get("name") for constraint in inspector.get_check_constraints("adherence_entries")}
        with op.batch_alter_table("adherence_entries", recreate="always") as batch:
            if "fk_adherence_entries_analysis_session" in adherence_fks:
                batch.drop_constraint("fk_adherence_entries_analysis_session", type_="foreignkey")
            if "ck_fatigue" in adherence_checks:
                batch.drop_constraint("ck_fatigue", type_="check")
            batch.drop_column("analysis_session_id")
            batch.drop_column("fatigue")
        analysis_fks = {constraint.get("name") for constraint in sa.inspect(op.get_bind()).get_foreign_keys("analysis_sessions")}
        with op.batch_alter_table("analysis_sessions", recreate="always") as batch:
            if "fk_analysis_sessions_plan_item" in analysis_fks:
                batch.drop_constraint("fk_analysis_sessions_plan_item", type_="foreignkey")
            batch.drop_column("plan_item_id")
    else:
        op.drop_column("adherence_entries", "analysis_session_id")
        op.drop_column("adherence_entries", "fatigue")
        op.drop_column("analysis_sessions", "plan_item_id")
