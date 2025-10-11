from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.agent_model import Agent
from app.db.schemas.agent_schema import AgentCreate, AgentUpdate


def get_all_agents(db: Session):
    """Retrieve all agents."""
    return db.query(Agent).all()


def get_agent_by_id(agent_id: int, db: Session):
    """Retrieve a single agent by ID."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


def create_agent(agent_data: AgentCreate, db: Session):
    """Create a new agent, ensuring name is unique."""
    existing = db.query(Agent).filter(Agent.name == agent_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent with this name already exists"
        )

    new_agent = Agent(**agent_data.dict())
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent


def update_agent(agent_id: int, agent_data: AgentUpdate, db: Session):
    """Update agent information."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if agent_data.name:
        # Prevent duplicate name conflicts
        existing = db.query(Agent).filter(Agent.name == agent_data.name, Agent.id != agent_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Agent name already taken")

    for key, value in agent_data.dict(exclude_unset=True).items():
        setattr(agent, key, value)

    db.commit()
    db.refresh(agent)
    return agent


def delete_agent(agent_id: int, db: Session):
    """Delete an agent by ID."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db.delete(agent)
    db.commit()
    return {"detail": "Agent deleted successfully"}
