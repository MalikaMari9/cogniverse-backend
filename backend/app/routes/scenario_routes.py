from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.controllers import scenario_controller
from app.db.schemas.scenario_schema import ScenarioCreate, ScenarioUpdate, ScenarioResponse
from typing import List

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

@router.get("/", response_model=List[ScenarioResponse])
def get_all(db: Session = Depends(get_db)):
    return scenario_controller.get_all_scenarios(db)

@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_by_id(scenario_id: int, db: Session = Depends(get_db)):
    return scenario_controller.get_scenario_by_id(db, scenario_id)

@router.post("/", response_model=ScenarioResponse)
def create(scenario: ScenarioCreate, db: Session = Depends(get_db)):
    return scenario_controller.create_scenario(db, scenario)

@router.put("/{scenario_id}", response_model=ScenarioResponse)
def update(scenario_id: int, scenario: ScenarioUpdate, db: Session = Depends(get_db)):
    return scenario_controller.update_scenario(db, scenario_id, scenario)

@router.delete("/{scenario_id}")
def delete(scenario_id: int, db: Session = Depends(get_db)):
    return scenario_controller.delete_scenario(db, scenario_id)
