from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, get_password_hash
from app.db.database import Base, create_database_engine, get_db
from app.db.models import DataRightsRequest, User
from app.main import app


def test_super_admin_reviews_canonical_data_rights_queue(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'privacy.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db:
        db.add_all([
            User(user_id='root', email='root@example.test', password_hash=get_password_hash('Password123!'), role='super_admin', is_verified=True),
            User(user_id='patient', email='patient@example.test', full_name='Patient Example', password_hash=get_password_hash('Password123!'), role='patient', is_verified=True),
            User(user_id='admin', email='admin@example.test', password_hash=get_password_hash('Password123!'), role='admin', is_verified=True),
            DataRightsRequest(request_id='request-one', user_id='patient', request_type='deletion', status='pending', details='Please close my account'),
        ])
        db.commit()

    def override():
        with factory() as db:
            yield db
    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    try:
        admin = {'Authorization': f"Bearer {create_access_token('admin', 'admin')}"}
        assert client.get('/api/v1/admin/platform/data-rights-requests', headers=admin).status_code == 403
        root = {'Authorization': f"Bearer {create_access_token('root', 'super_admin')}"}
        queue = client.get('/api/v1/admin/platform/data-rights-requests', headers=root)
        assert queue.status_code == 200
        assert queue.json()[0]['account_email'] == 'patient@example.test'
        reviewed = client.patch('/api/v1/admin/platform/data-rights-requests/request-one', headers=root,
            json={'decision': 'approve', 'reason': 'Identity verified'})
        assert reviewed.status_code == 200
        assert reviewed.json()['status'] == 'approved'
        assert reviewed.json()['retention_until'] is None
        with factory() as db:
            patient = db.scalar(select(User).where(User.user_id == 'patient'))
            assert patient.is_active is False
            assert patient.account_status == 'suspended'
            assert patient.token_version == 1
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
