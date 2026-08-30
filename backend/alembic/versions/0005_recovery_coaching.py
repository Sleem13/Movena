"""Add bounded recovery and lifestyle coaching records.

Revision ID: 0005_recovery_coaching
Revises: 0004_rehab_phase1
"""

from alembic import op
import sqlalchemy as sa

from app.db.database import Base
from app.db import models  # noqa: F401 - register the current table metadata

revision = "0005_recovery_coaching"
down_revision = "0004_rehab_phase1"
branch_labels = None
depends_on = None


COACHING_TABLES = (
    "recovery_coaching_goals",
    "recovery_coaching_check_ins",
    "recovery_coaching_action_plans",
)


def _create_tables_explicitly() -> None:
    op.create_table(
        "recovery_coaching_goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("goal_id", sa.String(36), nullable=False, unique=True),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by_user_id", sa.String(36), nullable=False),
        sa.Column("domain", sa.String(32), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("specific_action", sa.Text(), nullable=False),
        sa.Column("measurement", sa.String(160), nullable=False),
        sa.Column("why_important", sa.Text(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(24), nullable=False, server_default="proposed"),
        sa.Column("patient_agreed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("confidence >= 1 AND confidence <= 5", name="ck_coaching_goal_confidence"),
        sa.CheckConstraint("progress_percent >= 0 AND progress_percent <= 100", name="ck_coaching_goal_progress"),
    )
    op.create_table(
        "recovery_coaching_check_ins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("check_in_id", sa.String(36), nullable=False, unique=True),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by_user_id", sa.String(36), nullable=False),
        sa.Column("check_in_date", sa.Date(), nullable=False),
        sa.Column("energy", sa.Integer(), nullable=False),
        sa.Column("sleep_quality", sa.Integer(), nullable=False),
        sa.Column("stress", sa.Integer(), nullable=False),
        sa.Column("recovery_confidence", sa.Integer(), nullable=False),
        sa.Column("activity_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("barrier_category", sa.String(32), nullable=False, server_default="none"),
        sa.Column("barrier_note", sa.Text()),
        sa.Column("symptoms_changed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("urgent_concern", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("coaching_state", sa.String(24), nullable=False),
        sa.Column("supportive_prompt", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("patient_id", "check_in_date", name="uq_recovery_coaching_daily_check_in"),
        sa.CheckConstraint("energy >= 1 AND energy <= 5", name="ck_coaching_checkin_energy"),
        sa.CheckConstraint("sleep_quality >= 1 AND sleep_quality <= 5", name="ck_coaching_checkin_sleep"),
        sa.CheckConstraint("stress >= 1 AND stress <= 5", name="ck_coaching_checkin_stress"),
        sa.CheckConstraint("recovery_confidence >= 1 AND recovery_confidence <= 5", name="ck_coaching_checkin_confidence"),
        sa.CheckConstraint("activity_minutes >= 0 AND activity_minutes <= 1440", name="ck_coaching_checkin_activity"),
    )
    op.create_table(
        "recovery_coaching_action_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("action_plan_id", sa.String(36), nullable=False, unique=True),
        sa.Column("goal_id", sa.String(36), sa.ForeignKey("recovery_coaching_goals.goal_id", ondelete="CASCADE"), nullable=False),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by_user_id", sa.String(36), nullable=False),
        sa.Column("action_step", sa.Text(), nullable=False),
        sa.Column("frequency", sa.String(120), nullable=False),
        sa.Column("support_needed", sa.Text()),
        sa.Column("review_date", sa.Date(), nullable=False),
        sa.Column("patient_agreed", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    for table, columns in {
        "recovery_coaching_goals": ["goal_id", "patient_id", "created_by_user_id", "domain", "target_date", "status"],
        "recovery_coaching_check_ins": ["check_in_id", "patient_id", "created_by_user_id", "check_in_date", "barrier_category", "coaching_state"],
        "recovery_coaching_action_plans": ["action_plan_id", "goal_id", "patient_id", "created_by_user_id", "review_date", "status"],
    }.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column])


def upgrade() -> None:
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())
    if existing.isdisjoint(COACHING_TABLES):
        _create_tables_explicitly()
        return

    # Revision 0001 is a legacy-safe baseline that calls metadata.create_all.
    # A database first created from the current model set therefore already has
    # these tables by the time revision 0005 runs. checkfirst also lets a
    # partially applied disposable migration converge without duplicate DDL.
    for table_name in COACHING_TABLES:
        Base.metadata.tables[table_name].create(bind, checkfirst=True)


def downgrade() -> None:
    op.drop_table("recovery_coaching_action_plans")
    op.drop_table("recovery_coaching_check_ins")
    op.drop_table("recovery_coaching_goals")
