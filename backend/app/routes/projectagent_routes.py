from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.controllers import projectagent_controller
from app.db.schemas.projectagent_schema import ProjectAgentCreate, ProjectAgentUpdate, ProjectAgentResponse

router = APIRouter(prefix="/project-agents", tags=["Project Agents"])


@router.get("/", response_model=List[ProjectAgentResponse])
def get_all(db: Session = Depends(get_db)):
    return projectagent_controller.get_all_project_agents(db)


@router.get("/{projAgentID}", response_model=ProjectAgentResponse)
def get_by_id(projAgentID: int, db: Session = Depends(get_db)):
    return projectagent_controller.get_project_agent_by_id(db, projAgentID)


@router.post("/", response_model=ProjectAgentResponse, status_code=201)
def create(project_agent: ProjectAgentCreate, db: Session = Depends(get_db)):
    return projectagent_controller.create_project_agent(db, project_agent)


@router.put("/{projAgentID}", response_model=ProjectAgentResponse)
def update(projAgentID: int, project_agent: ProjectAgentUpdate, db: Session = Depends(get_db)):
    return projectagent_controller.update_project_agent(db, projAgentID, project_agent)


@router.delete("/{projAgentID}")
def delete(projAgentID: int, db: Session = Depends(get_db)):
    return projectagent_controller.delete_project_agent(db, projAgentID)
