import pytest
from types import SimpleNamespace
from app.api.dependencies.auth import AuthError, analysis_current_user, require_any_role
from app.core.config import get_settings

def test_role_dependency_allows_admin_and_rejects_patient():
    dependency=require_any_role({"admin","therapist"})
    assert dependency(SimpleNamespace(role="admin")).role=="admin"
    with pytest.raises(AuthError) as exc: dependency(SimpleNamespace(role="patient"))
    assert exc.value.status_code==403 and exc.value.error_code=="INSUFFICIENT_ROLE"


def test_analysis_auth_switch(monkeypatch):
    monkeypatch.setattr(get_settings(), "require_auth_for_analysis", True)
    with pytest.raises(AuthError) as exc:
        analysis_current_user(None)
    assert exc.value.error_code == "AUTH_REQUIRED"
