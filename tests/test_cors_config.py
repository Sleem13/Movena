from backend.app.core.config import Settings


def test_cors_origins_parse_cleanly(monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173, https://mobile.example")
    assert Settings.from_environment().cors_allowed_origins == [
        "http://localhost:5173", "https://mobile.example"
    ]
