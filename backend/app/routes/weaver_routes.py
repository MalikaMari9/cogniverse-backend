# ===============================
# app/routes/weaver_routes.py — Soft Delete + Logging (No Permissions)
# ===============================

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.controllers.weaver_controller import (
    create_weaver,
    get_weaver_by_id,
    list_weavers_by_project,
    list_weavers_by_agent,
    update_weaver,
    delete_weaver,
)
from app.db.schemas.weaver_schema import WeaverCreate, WeaverUpdate, WeaverResponse
from app.services.jwt_service import get_current_user
from app.services.route_logger_helper import log_action, log_error

router = APIRouter(prefix="/weavers", tags=["Weavers"])


# ============================================================
# 🔹 CREATE WEAVER
# ============================================================
@router.post("/", response_model=WeaverResponse, status_code=201)
async def create_weaver_route(
    data: WeaverCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = create_weaver(db, data)
        await log_action(
            db, request, current_user,
            "WEAVER_CREATE",
            details=f"Created new weaver for Project {data.projectid}, Agent {data.agentid}"
        )
        return result
    except Exception as e:
        await log_error(db, request, current_user, "WEAVER_CREATE_ERROR", e, "Error creating weaver")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 GET WEAVER BY ID
# ============================================================
@router.get("/{weaverid}", response_model=WeaverResponse)
async def get_weaver_route(
    weaverid: int,
    request: Request,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted weavers"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        weaver = get_weaver_by_id(db, weaverid, include_deleted=include_deleted)
        await log_action(
            db, request, current_user,
            "WEAVER_VIEW",
            details=f"Viewed weaver ID {weaverid} (include_deleted={include_deleted})",
            dedupe_key=f"weaver_{weaverid}"
        )
        return weaver
    except HTTPException as e:
        await log_error(db, request, current_user, "WEAVER_VIEW_FAILED", e, f"Failed to view weaver {weaverid}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "WEAVER_VIEW_ERROR", e, f"Error viewing weaver {weaverid}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 LIST WEAVERS BY PROJECT
# ============================================================
@router.get("/project/{projectid}", response_model=List[WeaverResponse])
async def list_by_project_route(
    projectid: int,
    request: Request,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted weavers"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = list_weavers_by_project(db, projectid, include_deleted=include_deleted)
        await log_action(
            db, request, current_user,
            "WEAVER_LIST_PROJECT",
            details=f"Listed weavers under Project {projectid} (include_deleted={include_deleted})"
        )
        return result
    except Exception as e:
        await log_error(db, request, current_user, "WEAVER_LIST_PROJECT_ERROR", e, f"Error listing weavers for Project {projectid}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 LIST WEAVERS BY AGENT
# ============================================================
@router.get("/agent/{agentid}", response_model=List[WeaverResponse])
async def list_by_agent_route(
    agentid: int,
    request: Request,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted weavers"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = list_weavers_by_agent(db, agentid, include_deleted=include_deleted)
        await log_action(
            db, request, current_user,
            "WEAVER_LIST_AGENT",
            details=f"Listed weavers for Agent {agentid} (include_deleted={include_deleted})"
        )
        return result
    except Exception as e:
        await log_error(db, request, current_user, "WEAVER_LIST_AGENT_ERROR", e, f"Error listing weavers for Agent {agentid}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 UPDATE WEAVER
# ============================================================
@router.put("/{weaverid}", response_model=WeaverResponse)
async def update_weaver_route(
    weaverid: int,
    data: WeaverUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = update_weaver(db, weaverid, data)
        await log_action(
            db, request, current_user,
            "WEAVER_UPDATE",
            details=f"Updated weaver ID {weaverid}"
        )
        return result
    except HTTPException as e:
        await log_error(db, request, current_user, "WEAVER_UPDATE_FAILED", e, f"Failed to update weaver {weaverid}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "WEAVER_UPDATE_ERROR", e, f"Error updating weaver {weaverid}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 SOFT DELETE WEAVER
# ============================================================
@router.delete("/{weaverid}")
async def delete_weaver_route(
    weaverid: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = delete_weaver(db, weaverid)
        await log_action(
            db, request, current_user,
            "WEAVER_DELETE",
            details=f"Soft-deleted weaver ID {weaverid}"
        )
        return result
    except HTTPException as e:
        await log_error(db, request, current_user, "WEAVER_DELETE_FAILED", e, f"Failed to delete weaver {weaverid}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "WEAVER_DELETE_ERROR", e, f"Error deleting weaver {weaverid}")
        raise HTTPException(status_code=500, detail="Internal server error")
