# ===============================
# app/controllers/scenario_controller.py — Soft Delete Ready
# ===============================

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.scenario_model import Scenario
from app.db.schemas.scenario_schema import ScenarioCreate, ScenarioUpdate


# ============================================================
# 🔹 GET ALL SCENARIOS
# ============================================================
def get_all_scenarios(db: Session, include_deleted: bool = False):
    """Retrieve all scenarios (exclude deleted by default)."""
    query = db.query(Scenario)
    if not include_deleted:
        query = query.filter(Scenario.is_deleted == False)
    return query.order_by(Scenario.created_at.desc()).all()


# ============================================================
# 🔹 GET SINGLE SCENARIO
# ============================================================
def get_scenario_by_id(db: Session, scenarioid: int, include_deleted: bool = False):
    """Retrieve a single scenario by ID."""
    scenario = db.query(Scenario).filter(Scenario.scenarioid == scenarioid).first()
    if not scenario or (scenario.is_deleted and not include_deleted):
        raise HTTPException(status_code=404, detail="Scenario not found or deleted")
    return scenario


# ============================================================
# 🔹 CREATE SCENARIO — also activates Project
# ============================================================
def create_scenario(db: Session, scenario_data: ScenarioCreate):
    """Create a new scenario entry and mark its project as active."""
    try:
        scenarioname = scenario_data.scenarioname or "Untitled Scenario"
        if len(scenarioname) > 100:
            scenarioname = scenarioname[:97] + "..."

        new_scenario = Scenario(
            scenarioname=scenarioname,
            scenarioprompt=scenario_data.scenarioprompt,
            projectid=int(scenario_data.projectid),
            status=scenario_data.status,
        )

        db.add(new_scenario)
        db.commit()
        db.refresh(new_scenario)

        # ====================================================
        # 🟢 Activate the related project
        # ====================================================
        from app.db.models.project_model import Project, ProjectStatus

        project = db.query(Project).filter(
            Project.projectid == new_scenario.projectid,
            Project.is_deleted == False
        ).first()

        if project and project.status != ProjectStatus.active:
            project.status = ProjectStatus.active
            db.commit()
            db.refresh(project)
            print(f"✅ Project {project.projectid} set to ACTIVE")

        return new_scenario

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ============================================================
# 🔹 UPDATE SCENARIO
# ============================================================
def update_scenario(db: Session, scenarioid: int, scenario_data: ScenarioUpdate):
    """Update an existing scenario."""
    scenario = db.query(Scenario).filter(Scenario.scenarioid == scenarioid).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    if scenario.is_deleted:
        raise HTTPException(status_code=400, detail="Cannot update a deleted scenario")

    for key, value in scenario_data.model_dump(exclude_unset=True).items():
        setattr(scenario, key, value)

    db.commit()
    db.refresh(scenario)
    return scenario


# ============================================================
# 🔹 SOFT DELETE SCENARIO
# ============================================================
def delete_scenario(db: Session, scenarioid: int):
    """Soft delete a scenario instead of removing it permanently."""
    scenario = db.query(Scenario).filter(Scenario.scenarioid == scenarioid).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    if scenario.is_deleted:
        raise HTTPException(status_code=400, detail="Scenario already deleted")

    scenario.is_deleted = True
    scenario.deleted_at = datetime.utcnow()

    db.commit()
    return {"detail": f"Scenario {scenarioid} soft-deleted successfully"}


# ============================================================
# 🔹 HARD DELETE SCENARIO (Admin Only)
# ============================================================
def hard_delete_scenario(db: Session, scenarioid: int):
    """Permanently delete a scenario (admin cleanup only)."""
    scenario = db.query(Scenario).filter(Scenario.scenarioid == scenarioid).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    db.delete(scenario)
    db.commit()
    return {"detail": f"Scenario {scenarioid} permanently deleted"}

