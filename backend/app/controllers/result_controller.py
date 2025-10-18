from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.result_model import Result
from app.db.schemas.result_schema import ResultCreate, ResultUpdate

def get_all_results(db: Session):
    return db.query(Result).all()

def get_result_by_id(db: Session, resultid: int):
    result = db.query(Result).filter(Result.resultid == resultid).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result

def create_result(db: Session, result_data: ResultCreate):
    new_result = Result(**result_data.dict())
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    return new_result

def update_result(db: Session, resultid: int, result_data: ResultUpdate):
    result = db.query(Result).filter(Result.resultid == resultid).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    for key, value in result_data.dict(exclude_unset=True).items():
        setattr(result, key, value)
    db.commit()
    db.refresh(result)
    return result

def delete_result(db: Session, resultid: int):
    result = db.query(Result).filter(Result.resultid == resultid).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    db.delete(result)
    db.commit()
    return {"message": "Result deleted successfully"}

# -------------------------------------------
# LIST RESULTS BY PROJECT AGENT + SCENARIO + TYPE
# -------------------------------------------
def list_results_by_agent_scenario_type(db: Session, projectagentid: int, scenarioid: int, resulttype: str):
    results = (
        db.query(Result)
        .filter(
            Result.projectagentid == projectagentid,
            Result.scenarioid == scenarioid,
            Result.resulttype == resulttype,
        )
        .order_by(Result.sequence_no.asc())
        .all()
    )
    if not results:
        raise HTTPException(status_code=404, detail="No matching results found")
    return results
