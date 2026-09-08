from backend.app.core.config import (
    DEFAULT_ACTIVE_FRAME_RECOGNITION_MODEL_ID,
    DEFAULT_ACTIVE_SEQUENCE_RECOGNITION_MODEL_ID,
    DEFAULT_CORS_ORIGINS,
    Settings,
)


def test_config_loads_safe_defaults(monkeypatch):
    for name in ("APP_ENV", "APP_VERSION", "CORS_ALLOWED_ORIGINS", "MAX_UPLOAD_SIZE_MB", "ARTIFACT_RETENTION_HOURS"):
        monkeypatch.delenv(name, raising=False)
    settings = Settings.from_environment()
    assert settings.app_env == "development"
    assert settings.version == "0.12.0"
    assert settings.max_upload_size_mb == 100
    assert settings.artifact_retention_hours == 24
    assert settings.cors_allowed_origins == DEFAULT_CORS_ORIGINS
    assert settings.active_sequence_recognition_model_id == DEFAULT_ACTIVE_SEQUENCE_RECOGNITION_MODEL_ID
    assert settings.active_frame_recognition_model_id == DEFAULT_ACTIVE_FRAME_RECOGNITION_MODEL_ID
    assert settings.enable_subject_continuity_guard is True
    assert settings.enabled_features["subject_continuity_guard"] is True


def test_config_pins_recognition_models_from_environment(monkeypatch):
    monkeypatch.setenv("ACTIVE_SEQUENCE_RECOGNITION_MODEL_ID", "sequence_v2")
    monkeypatch.setenv("ACTIVE_FRAME_RECOGNITION_MODEL_ID", "frame_v2")
    settings = Settings.from_environment()
    assert settings.active_sequence_recognition_model_id == "sequence_v2"
    assert settings.active_frame_recognition_model_id == "frame_v2"


def test_exercise_recognition_defaults_to_ml_runtime_setting(monkeypatch):
    monkeypatch.delenv("ENABLE_EXERCISE_RECOGNITION", raising=False)
    monkeypatch.setenv("ENABLE_ML_SECOND_OPINION", "false")

    settings = Settings.from_environment()

    assert settings.enable_exercise_recognition is False
    assert settings.enabled_features["exercise_recognition"] is False


def test_exercise_recognition_has_an_explicit_override(monkeypatch):
    monkeypatch.setenv("ENABLE_ML_SECOND_OPINION", "false")
    monkeypatch.setenv("ENABLE_EXERCISE_RECOGNITION", "true")

    assert Settings.from_environment().enable_exercise_recognition is True


def test_config_reads_required_ml_exercises(monkeypatch):
    monkeypatch.setenv("REQUIRED_ML_EXERCISES", "sit_to_stand,knee_extension")

    assert Settings.from_environment().required_ml_exercises == ["sit_to_stand", "knee_extension"]


def test_config_parses_origins_and_blocks_production_wildcard(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*,https://app.example.com")
    settings = Settings.from_environment()
    assert settings.effective_cors_origins == ["https://app.example.com"]


def test_config_reads_app_version(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "0.12.9-test")
    assert Settings.from_environment().version == "0.12.9-test"


def test_production_requires_subject_continuity_guard():
    settings = Settings(
        app_env="production",
        cors_allowed_origins=["https://app.example.com"],
        require_auth_for_analysis=True,
        enable_public_demo_mode=False,
        enable_subject_continuity_guard=False,
        secret_key="production-secret-key-that-is-long-enough",
    )

    try:
        settings.validate_deployment_safety()
    except RuntimeError as exc:
        assert "ENABLE_SUBJECT_CONTINUITY_GUARD must be true" in str(exc)
    else:
        raise AssertionError("Production must fail closed without the subject continuity guard.")
