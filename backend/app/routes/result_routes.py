from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.controllers import result_controller
from app.db.schemas.result_schema import ResultCreate, ResultUpdate, ResultResponse
from typing import List

router = APIRouter(prefix="/results", tags=["Results"])

@router.get("/", response_model=List[ResultResponse])
def get_all(db: Session = Depends(get_db)):
    return result_controller.get_all_results(db)

@router.get("/{result_id}", response_model=ResultResponse)
def get_by_id(result_id: int, db: Session = Depends(get_db)):
    return result_controller.get_result_by_id(db, result_id)

@router.post("/", response_model=ResultResponse)
def create(result: ResultCreate, db: Session = Depends(get_db)):
    return result_controller.create_result(db, result)

@router.put("/{result_id}", response_model=ResultResponse)
def update(result_id: int, result: ResultUpdate, db: Session = Depends(get_db)):
    return result_controller.update_result(db, result_id, result)

@router.delete("/{result_id}")
def delete(result_id: int, db: Session = Depends(get_db)):
    return result_controller.delete_result(db, result_id)
@router.get("/agent/{projectagentid}/scenario/{scenarioid}/type/{resulttype}", response_model=List[ResultResponse])
def get_results_by_agent_scenario_type(
    projectagentid: int,
    scenarioid: int,
    resulttype: str,
    db: Session = Depends(get_db),
):
    return result_controller.list_results_by_agent_scenario_type(db, projectagentid, scenarioid, resulttype)
