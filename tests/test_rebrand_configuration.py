import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_staging_examples_use_aws():
    staging_example = read_text(".env.staging.example")
    backend_staging_example = read_text("backend/.env.staging.example")

    assert "VITE_API_BASE_URL=https://your-application.cloudfront.net" in staging_example
    assert "name-physiovision-api-staging" not in staging_example
    assert "name-physiovision-api-staging" not in backend_staging_example
    assert "physio-vision-ai" not in staging_example
    assert "physio-vision-ai" not in backend_staging_example
    assert "CORS_ALLOWED_ORIGINS=https://your-application.cloudfront.net" in staging_example
    assert "FRONTEND_URL=https://your-application.cloudfront.net" in backend_staging_example


def test_alembic_and_docker_prefer_movena_database_names_with_legacy_volume_compatibility():
    alembic_config = read_text("alembic.ini")
    compose_config = read_text("docker-compose.yml")

    assert "sqlalchemy.url = sqlite:///backend/movena_dev.db" in alembic_config
    assert "sqlite:///backend/physiovision_dev.db" not in alembic_config
    assert "DATABASE_URL: sqlite:////app/backend/data/movena_dev.db" in compose_config
    assert "movena_data:/app/backend/data" in compose_config
    assert "physiovision_data:/app/backend/legacy-data:ro" in compose_config
    assert "for suffix in '' '-wal' '-shm'" in compose_config
    assert "/app/backend/legacy-data/physiovision_dev.db$$suffix" in compose_config
    assert "/app/backend/data/movena_dev.db$$suffix" in compose_config


def test_unified_sample_schema_metadata_is_rebranded():
    schema = json.loads(read_text("data/processed/registry/unified_sample_schema.json"))

    assert schema["title"] == "Movena Unified Sample Metadata"
