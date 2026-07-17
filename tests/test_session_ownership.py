from sqlalchemy.orm import sessionmaker
from app.db.crud import list_sessions
from app.db.database import Base,create_database_engine
from app.schemas.analysis_schema import AnalysisResponse
from app.services.session_persistence_service import save_analysis_session

def test_session_list_is_scoped_to_owner(tmp_path):
    engine=create_database_engine(f"sqlite:///{(tmp_path/'owner.db').as_posix()}");Base.metadata.create_all(engine);db=sessionmaker(bind=engine,expire_on_commit=False)()
    save_analysis_session(AnalysisResponse(total_reps=1),db=db,owner_user_id="one",created_by_user_id="one")
    save_analysis_session(AnalysisResponse(total_reps=2),db=db,owner_user_id="two",created_by_user_id="two")
    rows,total=list_sessions(db,owner_user_id="one")
    assert total==1 and rows[0].owner_user_id=="one"
    db.close()
