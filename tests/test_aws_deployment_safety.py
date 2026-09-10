from pathlib import Path
import re
from configparser import ConfigParser


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_container_applies_migrations_before_starting_api():
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "COPY alembic.ini /app/alembic.ini" in dockerfile
    command = next(line for line in dockerfile.splitlines() if line.startswith("CMD "))
    assert command.index("alembic") < command.index("uvicorn")
    assert "upgrade head" in command


def test_frontend_is_published_only_after_backend_is_stable():
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "deploy-aws.yml").read_text(
        encoding="utf-8"
    )

    wait_step = workflow.index("- name: Wait for backend and verify readiness")
    publish_step = workflow.index("- name: Publish frontend")
    assert wait_step < publish_step


def test_staging_uses_reversible_cost_controls_without_downsizing_video_compute():
    terraform = (PROJECT_ROOT / "infra" / "aws" / "main.tf").read_text(encoding="utf-8")

    assert 'launch_type                        = "FARGATE"' in terraform
    assert 'value = var.environment == "production" ? "enabled" : "disabled"' in terraform
    assert 'retention_in_days = var.environment == "production" ? 90 : 7' in terraform
    assert 'backup_retention_period     = var.environment == "production" ? 14 : 1' in terraform
    assert 'countNumber = var.environment == "production" ? 15 : 5' in terraform
    assert 'noncurrent_days = var.environment == "production" ? 30 : 7' in terraform
    assert 'var.environment == "staging" ? [' in terraform
    assert 'CLINICAL_ESCALATION_CONTACT' in terraform
    assert 'This staging service is not monitored for emergencies.' in terraform

    variables = (PROJECT_ROOT / "infra" / "aws" / "variables.tf").read_text(encoding="utf-8")
    assert re.search(r'variable "ecs_cpu"[\s\S]*?default\s*=\s*2048', variables)
    assert re.search(r'variable "ecs_memory"[\s\S]*?default\s*=\s*4096', variables)


def test_alembic_escapes_percent_characters_in_managed_database_urls():
    alembic_env = (PROJECT_ROOT / "backend" / "alembic" / "env.py").read_text(encoding="utf-8")
    assert '.replace("%", "%%")' in alembic_env

    database_url = "postgresql+psycopg://user:p%ss@example.test/app"
    parser = ConfigParser()
    parser.add_section("alembic")
    parser.set("alembic", "sqlalchemy.url", database_url.replace("%", "%%"))
    assert parser.get("alembic", "sqlalchemy.url") == database_url


def test_rehabilitation_migration_adopts_existing_postgres_foreign_keys():
    migration = (
        PROJECT_ROOT / "backend" / "alembic" / "versions" / "0004_rehabilitation_phase1.py"
    ).read_text(encoding="utf-8")

    assert 'get_foreign_keys("adherence_entries")' in migration
    assert 'if "fk_adherence_entries_analysis_session" not in adherence_foreign_keys:' in migration
    assert 'get_foreign_keys("analysis_sessions")' in migration
    assert 'if "fk_analysis_sessions_plan_item" not in analysis_foreign_keys:' in migration


def test_staging_schedules_are_opt_in_and_deployments_leave_service_available():
    terraform = (PROJECT_ROOT / "infra" / "aws" / "main.tf").read_text(encoding="utf-8")
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "deploy-aws.yml").read_text(
        encoding="utf-8"
    )

    assert terraform.count('schedule_expression_timezone = var.staging_schedule_timezone') == 4
    assert 'schedule_expression          = "cron(45 7 ? * MON-FRI *)"' in terraform
    assert 'schedule_expression          = "cron(0 8 ? * MON-FRI *)"' in terraform
    assert 'schedule_expression          = "cron(0 20 ? * * *)"' in terraform
    assert 'schedule_expression          = "cron(15 20 ? * * *)"' in terraform
    assert 'arn      = "arn:aws:scheduler:::aws-sdk:rds:stopDBInstance"' in terraform
    assert 'arn      = "arn:aws:scheduler:::aws-sdk:ecs:updateService"' in terraform
    assert 'DesiredCount = 0' in terraform
    assert "- name: Ensure staging is awake for deployment" in workflow
    assert "Restore scheduled staging state" not in workflow
    assert "stop-db-instance" not in workflow
    assert "--desired-count 0" not in workflow
    assert 'TF_VAR_enable_staging_schedule: "false"' in workflow
    variables = (PROJECT_ROOT / "infra" / "aws" / "variables.tf").read_text(encoding="utf-8")
    schedule = variables.split('variable "enable_staging_schedule" {', 1)[1].split("}", 1)[0]
    assert re.search(r'default\s*=\s*false', schedule)
    assert "var.desired_count >= 1 && floor(var.desired_count) == var.desired_count" in variables
