from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.projectagent_model import ProjectAgent
from app.db.schemas.projectagent_schema import ProjectAgentCreate, ProjectAgentUpdate


def get_all_project_agents(db: Session):
    return db.query(ProjectAgent).all()


def get_project_agent_by_id(db: Session, projagentid: int):
    project_agent = db.query(ProjectAgent).filter(ProjectAgent.projagentid == projagentid).first()
    if not project_agent:
        raise HTTPException(status_code=404, detail="ProjectAgent not found")
    return project_agent


def create_project_agent(db: Session, project_agent_data: ProjectAgentCreate):
    existing = (
        db.query(ProjectAgent)
        .filter(
            ProjectAgent.projectid == project_agent_data.projectid,
            ProjectAgent.agentid == project_agent_data.agentid,
        )
        .first()
    )

    # ✅ If already exists, just update its snapshot + status instead of throwing
    if existing:
        existing.agentsnapshot = project_agent_data.agentsnapshot
        existing.status = project_agent_data.status
        db.commit()
        db.refresh(existing)
        return existing

    # ✅ Otherwise, create a new one
    new_project_agent = ProjectAgent(**project_agent_data.dict())
    db.add(new_project_agent)
    db.commit()
    db.refresh(new_project_agent)
    return new_project_agent



def update_project_agent(db: Session, projagentid: int, project_agent_data: ProjectAgentUpdate):
    project_agent = db.query(ProjectAgent).filter(ProjectAgent.projagentid == projagentid).first()
    if not project_agent:
        raise HTTPException(status_code=404, detail="ProjectAgent not found")

    for key, value in project_agent_data.dict(exclude_unset=True).items():
        setattr(project_agent, key, value)

    db.commit()
    db.refresh(project_agent)
    return project_agent


def delete_project_agent(db: Session, projagentid: int):
    project_agent = db.query(ProjectAgent).filter(ProjectAgent.projagentid == projagentid).first()
    if not project_agent:
        raise HTTPException(status_code=404, detail="ProjectAgent not found")

    db.delete(project_agent)
    db.commit()
    return {"detail": "ProjectAgent deleted successfully"}