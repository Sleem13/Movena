"""Create the care-platform schema safely on new or existing databases."""

from alembic import op
import sqlalchemy as sa

from app.db.database import Base
from app.db import models  # noqa: F401

revision = "0001_care_platform"
down_revision = None
branch_labels = None
depends_on = None


CARE_TABLES = (
    "patient_health_profiles", "therapist_patient_assignments", "adherence_entries",
    "therapist_availability", "appointments", "clinical_session_notes", "notifications",
    "service_offerings", "package_offerings", "orders", "payments", "refunds",
    "platform_settings",
    "progress_reports",
)


def _add_column_if_missing(table: str, column: sa.Column) -> None:
    bind = op.get_bind()
    names = {item["name"] for item in sa.inspect(bind).get_columns(table)}
    if column.name not in names:
        op.add_column(table, column)


def upgrade() -> None:
    bind = op.get_bind()
    # The repository predates Alembic. create_all is intentionally used once as
    # a non-destructive baseline so both an empty database and the deployed
    # legacy schema converge before additive columns are applied below.
    Base.metadata.create_all(bind)
    _add_column_if_missing("patient_profiles", sa.Column("user_id", sa.String(36), nullable=True))
    _add_column_if_missing("patient_profiles", sa.Column("preferred_locale", sa.String(8), nullable=False, server_default="ar"))
    _add_column_if_missing("patient_profiles", sa.Column("timezone_name", sa.String(64), nullable=False, server_default="Africa/Cairo"))
    _add_column_if_missing("exercise_plan_items", sa.Column("duration_minutes", sa.Integer(), nullable=True))
    _add_column_if_missing("exercise_plan_items", sa.Column("precautions", sa.Text(), nullable=True))
    _add_column_if_missing("exercise_plan_items", sa.Column("schedule_days_json", sa.Text(), nullable=False, server_default="[]"))
    _add_column_if_missing("exercise_plan_items", sa.Column("requested_media_upload", sa.Boolean(), nullable=False, server_default=sa.false()))
    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("patient_profiles")}
    if "ux_patient_profiles_user_id" not in indexes:
        op.create_index("ux_patient_profiles_user_id", "patient_profiles", ["user_id"], unique=True)
    if bind.dialect.name == "postgresql":
        foreign_keys = {fk.get("name") for fk in inspector.get_foreign_keys("patient_profiles")}
        if "fk_patient_profiles_user_id_users" not in foreign_keys:
            op.create_foreign_key(
                "fk_patient_profiles_user_id_users", "patient_profiles", "users",
                ["user_id"], ["user_id"], ondelete="SET NULL",
            )
        roles = {row[0] for row in bind.execute(sa.text("select rolname from pg_roles where rolname in ('anon','authenticated')"))}
        for table in Base.metadata.tables:
            op.execute(sa.text(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY'))
            for role in roles:
                op.execute(sa.text(f'REVOKE ALL ON TABLE "{table}" FROM "{role}"'))


def downgrade() -> None:
    # Production healthcare data is never dropped automatically. Rollback is
    # performed with a reviewed forward migration after backup verification.
    pass
