from api.main import app


def test_root_uvicorn_entrypoint_exposes_fastapi_app():
    assert app.title == "PhysioVision AI"
