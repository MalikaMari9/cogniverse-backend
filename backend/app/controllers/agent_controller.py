from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import func
from typing import Optional 
from app.db.models.agent_model import Agent, LifecycleStatus
from app.db.schemas.agent_schema import AgentCreate, AgentUpdate
from app.services.utils.config_helper import get_int_config

# =========================================================
# 🔹 GET ALL
# =========================================================
def get_all_agents(db: Session, include_deleted: bool = False):
    """Retrieve all agents (excluding soft-deleted by default)."""
    query = db.query(Agent)
    if not include_deleted:
        query = query.filter(Agent.is_deleted == False)
    return query.all()


# =========================================================
# 🔹 GET BY ID
# =========================================================
def get_agent_by_id(agent_id: int, db: Session):
    """Retrieve a single agent by ID."""
    agent = db.query(Agent).filter(Agent.agentid == agent_id, Agent.is_deleted == False).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found or deleted")
    return agent


# =========================================================
# 🔹 CREATE
# =========================================================
def create_agent(agent_data: AgentCreate, db: Session):
    """Create a new agent."""
    new_agent = Agent(**agent_data.model_dump())
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent


# =========================================================
# 🔹 UPDATE
# =========================================================
def update_agent(agent_id: int, agent_data: AgentUpdate, db: Session):
    """Update agent information."""
    agent = db.query(Agent).filter(Agent.agentid == agent_id, Agent.is_deleted == False).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found or has been deleted")

    for key, value in agent_data.model_dump(exclude_unset=True).items():
        setattr(agent, key, value)

    db.commit()
    db.refresh(agent)
    return agent


# =========================================================
# 🔹 SOFT DELETE
# =========================================================
def delete_agent(agent_id: int, db: Session):
    """Soft delete an agent (mark as deleted)."""
    agent = db.query(Agent).filter(Agent.agentid == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # If already deleted, no need to repeat
    if agent.is_deleted:
        raise HTTPException(status_code=400, detail="Agent already deleted")

    agent.is_deleted = True
    agent.deleted_at = datetime.utcnow()
    agent.status = LifecycleStatus.inactive
    db.commit()
    return {"detail": f"Agent {agent.agentid} marked as deleted"}


# =========================================================
# 🔹 HARD DELETE (for admin cleanup)
# =========================================================
def hard_delete_agent(agent_id: int, db: Session):
    """Permanently delete an agent (admin use only)."""
    agent = db.query(Agent).filter(Agent.agentid == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db.delete(agent)
    db.commit()
    return {"detail": f"Agent {agent.agentid} permanently deleted"}


# =========================================================
# 🔹 GET BY USER
# =========================================================
def get_agents_by_user(user_id: int, db: Session, page: int = 1, include_deleted: bool = False, search_query: Optional[str] = None):
    limit = get_int_config(db, "AgentPaginationLimit", 8)
    offset = (page - 1) * limit

    query = db.query(Agent).filter(Agent.userid == user_id)

    if not include_deleted:
        query = query.filter(Agent.is_deleted == False)

    # 🔍 Add search filtering
    if search_query:
        q = f"%{search_query.lower()}%"
        query = query.filter(
            func.lower(Agent.agentname).like(q) |
            func.lower(Agent.agentpersonality).like(q) |
            func.lower(Agent.agentbiography).like(q)
        )

    total_count = query.count()
    agents = query.order_by(Agent.agentname.asc()).offset(offset).limit(limit).all()

    return {
        "page": page,
        "limit": limit,
        "total_count": total_count,
        "agents": agents,
    }