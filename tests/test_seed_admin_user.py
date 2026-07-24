import pytest
from sqlalchemy.orm import sessionmaker
from app.db.database import Base,create_database_engine
from scripts.seed_admin_user import seed_admin,validate_admin_password

def test_seed_admin_is_safe_and_idempotent(tmp_path):
    engine=create_database_engine(f"sqlite:///{(tmp_path/'seed.db').as_posix()}");Base.metadata.create_all(engine);db=sessionmaker(bind=engine,expire_on_commit=False)()
    with pytest.raises(ValueError):validate_admin_password("weak")
    first,changed=seed_admin("admin@example.com","StrongAdminPassword123","Dev Admin",db=db)
    second,changed_again=seed_admin("admin@example.com","StrongAdminPassword123","Dev Admin",db=db)
    assert changed and not changed_again and first.user_id==second.user_id and first.role=="admin" and first.is_verified
    db.close()
