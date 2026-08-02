import pytest
from sqlalchemy.orm import sessionmaker
from app.db.database import Base,create_database_engine
from scripts.seed_admin_user import seed_admin,seed_admin_from_environment,validate_admin_password

def test_seed_admin_is_safe_and_idempotent(tmp_path):
    engine=create_database_engine(f"sqlite:///{(tmp_path/'seed.db').as_posix()}");Base.metadata.create_all(engine);db=sessionmaker(bind=engine,expire_on_commit=False)()
    with pytest.raises(ValueError):validate_admin_password("1234567")
    first,changed=seed_admin("admin@example.com","TestPass1","Dev Admin",db=db)
    second,changed_again=seed_admin("admin@example.com","TestPass1","Dev Admin",db=db)
    assert changed and not changed_again and first.user_id==second.user_id and first.role=="admin" and first.is_verified
    db.close()

def test_environment_seed_is_explicit_and_supports_eight_character_password(tmp_path):
    engine=create_database_engine(f"sqlite:///{(tmp_path/'env-seed.db').as_posix()}");Base.metadata.create_all(engine);db=sessionmaker(bind=engine,expire_on_commit=False)()
    assert seed_admin_from_environment(db=db,environ={}) is None
    user,changed=seed_admin_from_environment(reset=True,db=db,environ={"SEED_ADMIN_ON_START":"true","ADMIN_EMAIL":"admin","ADMIN_PASSWORD":"TestPass1","ADMIN_FULL_NAME":"Admin"})
    assert changed and user.email=="admin" and user.role=="admin" and user.is_active and user.is_verified
    db.close()
