from pathlib import Path
import re


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

    assert 'capacity_provider = var.environment == "production" ? "FARGATE" : "FARGATE_SPOT"' in terraform
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
