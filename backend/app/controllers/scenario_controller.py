from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.scenario_model import Scenario
from app.db.schemas.scenario_schema import ScenarioCreate, ScenarioUpdate

def get_all_scenarios(db: Session):
    return db.query(Scenario).all()

def get_scenario_by_id(db: Session, scenarioid: int):
    scenario = db.query(Scenario).filter(Scenario.scenarioid == scenarioid).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

def create_scenario(db: Session, scenario_data: ScenarioCreate):
    new_scenario = Scenario(**scenario_data.dict())
    db.add(new_scenario)
    db.commit()
    db.refresh(new_scenario)
    return new_scenario

def update_scenario(db: Session, scenarioid: int, scenario_data: ScenarioUpdate):
    scenario = db.query(Scenario).filter(Scenario.scenarioid == scenarioid).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    for key, value in scenario_data.dict(exclude_unset=True).items():
        setattr(scenario, key, value)
    db.commit()
    db.refresh(scenario)
    return scenario

def delete_scenario(db: Session, scenarioid: int):
    scenario = db.query(Scenario).filter(Scenario.scenarioid == scenarioid).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(scenario)
    db.commit()
    return {"message": "Scenario deleted successfully"}