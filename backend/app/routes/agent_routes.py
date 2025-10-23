from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app.db.schemas.agent_schema import AgentCreate, AgentUpdate, AgentResponse
from app.controllers import agent_controller
from app.db.database import get_db
from app.services.jwt_service import get_current_user
from app.services.utils.permissions_helper import enforce_permission_auto

router = APIRouter(prefix="/agents", tags=["Agents"])

# ============================================================
# 🔹 GET ALL AGENTS (requires READ access)
# ============================================================
@router.get("/", response_model=List[AgentResponse])
def get_all_agents(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "AGENTS", request)
    return agent_controller.get_all_agents(db)


# ============================================================
# 🔹 GET SINGLE AGENT (requires READ access)
# ============================================================
@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "AGENTS", request)
    return agent_controller.get_agent_by_id(agent_id, db)


# ============================================================
# 🔹 CREATE AGENT (requires WRITE access)
# ============================================================
@router.post("/", response_model=AgentResponse, status_code=201)
def create_agent(
    agent: AgentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "AGENTS", request)
    # ✅ Link the new agent to the current user
    agent.userid = current_user.userid
    return agent_controller.create_agent(agent, db)


# ============================================================
# 🔹 UPDATE AGENT (requires WRITE access)
# ============================================================
@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    agent: AgentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "AGENTS", request)
    return agent_controller.update_agent(agent_id, agent, db)


# ============================================================
# 🔹 DELETE AGENT (requires WRITE access)
# ============================================================
@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "AGENTS", request)
    return agent_controller.delete_agent(agent_id, db)


# ============================================================
# 🔹 GET AGENTS BY USER (requires READ access)
# ============================================================
@router.get("/user/{user_id}", response_model=List[AgentResponse])
def get_agents_by_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "AGENTS", request)

    # ✅ Ensure users can only access their own agents unless admin
    if current_user.role != "admin" and current_user.userid != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    return agent_controller.get_agents_by_user(user_id, db)
