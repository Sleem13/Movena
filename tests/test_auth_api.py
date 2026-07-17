from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from app.db.database import Base,create_database_engine,get_db
from app.main import app
from app.db.models import User
from app.core.security import create_access_token, get_password_hash

def test_register_login_me_and_admin_registration_blocked(tmp_path):
    engine=create_database_engine(f"sqlite:///{(tmp_path/'auth.db').as_posix()}");Base.metadata.create_all(engine);factory=sessionmaker(bind=engine,expire_on_commit=False)
    def override():
        db=factory()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db]=override;client=TestClient(app)
    try:
        denied=client.post("/api/v1/auth/register",json={"email":"root@example.com","password":"StrongPassword123","role":"admin"})
        assert denied.status_code==403
        created=client.post("/api/v1/auth/register",json={"email":"person@example.com","password":"StrongPassword123"})
        assert created.status_code==201 and "password_hash" not in created.json()
        logged=client.post("/api/v1/auth/login",json={"email":"person@example.com","password":"StrongPassword123"})
        assert logged.status_code==200 and logged.json()["access_token"]
        assert client.get("/api/v1/auth/me").json()["error_code"]=="AUTH_REQUIRED"
        me=client.get("/api/v1/auth/me",headers={"Authorization":f"Bearer {logged.json()['access_token']}"})
        assert me.status_code==200 and me.json()["role"]=="researcher_demo"
        assert client.get("/api/v1/auth/me",headers={"Authorization":"Bearer invalid"}).json()["error_code"]=="INVALID_TOKEN"
        db=factory();db.add(User(user_id="inactive",email="inactive@example.com",password_hash=get_password_hash("StrongPassword123"),role="patient",is_active=False));db.commit();db.close()
        inactive=client.get("/api/v1/auth/me",headers={"Authorization":f"Bearer {create_access_token('inactive','patient')}"})
        assert inactive.status_code==403 and inactive.json()["error_code"]=="USER_INACTIVE"
    finally: app.dependency_overrides.clear()
