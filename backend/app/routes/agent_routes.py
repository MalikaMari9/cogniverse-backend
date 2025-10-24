# ===============================
# app/routes/agent_routes.py — With Universal Route Logger
# ===============================

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.schemas.agent_schema import AgentCreate, AgentUpdate, AgentResponse
from app.controllers import agent_controller
from app.db.database import get_db
from app.services.utils.permissions_helper import enforce_permission_auto
from app.services.jwt_service import get_current_user
from app.services.route_logger_helper import log_action, log_error

router = APIRouter(prefix="/agents", tags=["Agents"])


# ============================================================
# 🔹 GET ALL AGENTS (requires READ access)
# ============================================================
@router.get("/", response_model=List[AgentResponse])
async def get_all_agents(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "AGENTS", request)
        result = agent_controller.get_all_agents(db)

        await log_action(
            db, request, current_user,
            "AGENT_LIST_VIEW",
            details=f"Viewed all agents ({len(result)} records)"
        )

        return result

    except Exception as e:
        await log_error(db, request, current_user, "AGENT_LIST_ERROR", e, "Error viewing all agents")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 GET SINGLE AGENT (requires READ access)
# ============================================================
@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "AGENTS", request)
        agent = agent_controller.get_agent_by_id(agent_id, db)

        await log_action(
            db, request, current_user,
            "AGENT_VIEW",
            details=f"Viewed agent ID {agent_id} ('{agent.agentname}')",
            dedupe_key=f"agent_{agent_id}"
        )

        return agent

    except HTTPException as e:
        await log_error(db, request, current_user, "AGENT_VIEW_FAILED", e, f"Failed to view agent {agent_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "AGENT_VIEW_ERROR", e, f"Error viewing agent {agent_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 CREATE AGENT (requires WRITE access)
# ============================================================
@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent: AgentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "AGENTS", request)
        agent.userid = current_user.userid
        result = agent_controller.create_agent(agent, db)

        await log_action(
            db, request, current_user,
            "AGENT_CREATE",
            details=f"Created agent '{agent.agentname}' (User ID {current_user.userid})"
        )

        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "AGENT_CREATE_FAILED", e, "Failed to create agent")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "AGENT_CREATE_ERROR", e, "Error creating agent")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 UPDATE AGENT (requires WRITE access)
# ============================================================
@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent: AgentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "AGENTS", request)
        old_data = agent_controller.get_agent_by_id(agent_id, db)
        if not old_data:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        result = agent_controller.update_agent(agent_id, agent, db)

        await log_action(
            db, request, current_user,
            "AGENT_UPDATE",
            details=f"Updated agent ID {agent_id} ('{old_data.agentname}')"
        )

        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "AGENT_UPDATE_FAILED", e, f"Failed to update agent {agent_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "AGENT_UPDATE_ERROR", e, f"Error updating agent {agent_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 DELETE AGENT (requires WRITE access)
# ============================================================
@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "AGENTS", request)
        agent_controller.delete_agent(agent_id, db)

        await log_action(
            db, request, current_user,
            "AGENT_DELETE",
            details=f"Deleted agent ID {agent_id}"
        )

        return {"message": f"Agent {agent_id} deleted successfully"}

    except HTTPException as e:
        await log_error(db, request, current_user, "AGENT_DELETE_FAILED", e, f"Failed to delete agent {agent_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "AGENT_DELETE_ERROR", e, f"Error deleting agent {agent_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 GET AGENTS BY USER (requires READ access)
# ============================================================
@router.get("/user/{user_id}", response_model=List[AgentResponse])
async def get_agents_by_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "AGENTS", request)

        # ✅ Restrict access unless admin or self
        if current_user.role != "admin" and current_user.userid != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden")

        result = agent_controller.get_agents_by_user(user_id, db)

        await log_action(
            db, request, current_user,
            "AGENT_LIST_BY_USER",
            details=f"Viewed agents belonging to user ID {user_id}"
        )

        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "AGENT_LIST_BY_USER_FAILED", e, f"Failed to fetch agents for user {user_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "AGENT_LIST_BY_USER_ERROR", e, f"Error fetching agents for user {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")
