from pathlib import Path


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
