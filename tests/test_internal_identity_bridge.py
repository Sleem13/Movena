import hashlib
import json
import time
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.db.database import Base, create_database_engine, get_db
from app.db.models import PatientProfile, User
from app.main import app


def assertion(secret, subject, method, path, body=b'', *, version=0, jti=None):
    now = int(time.time())
    return jwt.encode({'sub':subject, 'ver':version, 'iat':now, 'exp':now+20,
        'jti':jti or uuid4().hex, 'iss':'movena-platform', 'aud':'movena-legacy',
        'method':method, 'path':path, 'body_sha256':hashlib.sha256(body).hexdigest()}, secret, algorithm='HS256')


def test_projection_and_one_use_path_bound_principal(tmp_path, monkeypatch):
    secret = 'test-internal-assertion-secret-' + 'x'*32
    monkeypatch.setattr(get_settings(), 'internal_assertion_secret', secret)
    engine = create_database_engine(f"sqlite:///{(tmp_path/'bridge.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    def override():
        with factory() as db:
            yield db
    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    user_id = str(uuid4())
    payload = {'user_id':user_id, 'username':'new.patient', 'email':'new@example.com',
        'full_name':'New Patient', 'role':'patient', 'is_active':True, 'is_verified':True,
        'account_status':'active', 'is_protected':False, 'token_version':3,
        'permissions':['analysis:create']}
    body = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    path = f'/internal/v1/identity/accounts/{user_id}'
    token = assertion(secret, 'identity-projector', 'PUT', path, body)
    try:
        projected = client.put(path, content=body, headers={'Authorization':'MovenaInternal '+token, 'Content-Type':'application/json'})
        assert projected.status_code == 200
        with factory() as db:
            row = db.query(User).filter_by(user_id=user_id).one()
            assert row.identity_owner == 'platform' and row.password_hash == '!platform-owned'
            assert db.query(PatientProfile).filter_by(user_id=user_id).count() == 1

        principal = assertion(secret, user_id, 'GET', '/api/v1/auth/me', version=3)
        me = client.get('/api/v1/auth/me', headers={'Authorization':'MovenaInternal '+principal})
        assert me.status_code == 200 and me.json()['role'] == 'patient'
        replay = client.get('/api/v1/auth/me', headers={'Authorization':'MovenaInternal '+principal})
        assert replay.status_code == 401 and replay.json()['error_code'] == 'INTERNAL_ASSERTION_REPLAYED'
        wrong_path = assertion(secret, user_id, 'GET', '/api/v1/patient/me', version=3)
        denied = client.get('/api/v1/auth/me', headers={'Authorization':'MovenaInternal '+wrong_path})
        assert denied.status_code == 401
        isolated = assertion(secret, user_id, 'POST', '/api/v1/auth/logout', version=3)
        denied = client.post('/api/v1/auth/logout', headers={'Authorization':'MovenaInternal '+isolated})
        assert denied.status_code == 403 and denied.json()['error_code'] == 'IDENTITY_DOMAIN_ISOLATED'

        stale = dict(payload, token_version=2)
        stale_body = json.dumps(stale, sort_keys=True, separators=(',', ':')).encode()
        stale_token = assertion(secret, 'identity-projector', 'PUT', path, stale_body)
        denied = client.put(path, content=stale_body,
            headers={'Authorization':'MovenaInternal '+stale_token, 'Content-Type':'application/json'})
        assert denied.status_code == 409 and denied.json()['error_code'] == 'PROJECTION_REJECTED'
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_internal_bridge_is_disabled_without_secret(tmp_path, monkeypatch):
    monkeypatch.setattr(get_settings(), 'internal_assertion_secret', '')
    response = TestClient(app).get('/api/v1/auth/me', headers={'Authorization':'MovenaInternal opaque'})
    assert response.status_code == 401 and response.json()['error_code'] == 'INTERNAL_AUTH_DISABLED'


def test_explicit_ownership_conversion_replaces_legacy_password_and_version(tmp_path, monkeypatch):
    secret='test-internal-assertion-secret-'+'x'*32
    settings=get_settings(); monkeypatch.setattr(settings,'internal_assertion_secret',secret)
    monkeypatch.setattr(settings,'allow_identity_ownership_transfer',True)
    engine=create_database_engine(f"sqlite:///{(tmp_path/'transfer.db').as_posix()}"); Base.metadata.create_all(engine)
    factory=sessionmaker(bind=engine,expire_on_commit=False)
    user_id=str(uuid4()); legacy_hash='$2b$04$'+'a'*53
    with factory() as db:
        db.add(User(user_id=user_id,username='legacy.patient',email='legacy@example.test',
            full_name='Legacy Patient',password_hash=legacy_hash,role='patient',is_active=True,
            is_verified=True,account_status='active',token_version=4,permissions_json='["analysis:create"]'))
        db.commit()
    def override():
        with factory() as db: yield db
    app.dependency_overrides[get_db]=override; client=TestClient(app)
    account={'user_id':user_id,'username':'legacy.patient','email':'legacy@example.test','full_name':'Legacy Patient',
        'role':'patient','is_active':True,'is_verified':True,'account_status':'active','is_protected':False,
        'token_version':5,'permissions':['analysis:create']}
    envelope={'account':account,'expected_legacy_token_version':4,
        'legacy_password_hash_sha256':hashlib.sha256(legacy_hash.encode()).hexdigest()}
    body=json.dumps(envelope,sort_keys=True,separators=(',',':')).encode(); path=f'/internal/v1/identity/ownership-transfers/{user_id}'
    token=assertion(secret,'identity-transfer','PUT',path,body)
    try:
        response=client.put(path,content=body,headers={'Authorization':'MovenaInternal '+token,'Content-Type':'application/json'})
        assert response.status_code==200
        with factory() as db:
            row=db.query(User).filter_by(user_id=user_id).one()
            assert (row.identity_owner,row.password_hash,row.token_version)==('platform','!platform-owned',5)
    finally:
        app.dependency_overrides.clear(); engine.dispose()
