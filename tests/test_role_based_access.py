from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from app.core.security import create_access_token,get_password_hash
from app.db.database import Base,create_database_engine,get_db
from app.db.models import User
from app.main import app

def test_therapist_endpoint_rejects_patient_role(tmp_path):
    engine=create_database_engine(f"sqlite:///{(tmp_path/'roles.db').as_posix()}");Base.metadata.create_all(engine);factory=sessionmaker(bind=engine,expire_on_commit=False)
    db=factory();db.add(User(user_id="patient-1",email="p@example.com",password_hash=get_password_hash("StrongPassword123"),role="patient",is_verified=True));db.commit();db.close()
    def override():
        s=factory()
        try:yield s
        finally:s.close()
    app.dependency_overrides[get_db]=override
    try:
        response=TestClient(app).get("/api/v1/therapist/dashboard",headers={"Authorization":f"Bearer {create_access_token('patient-1','patient')}"})
        assert response.status_code==403 and response.json()["error_code"]=="INSUFFICIENT_ROLE"
    finally:app.dependency_overrides.clear()
