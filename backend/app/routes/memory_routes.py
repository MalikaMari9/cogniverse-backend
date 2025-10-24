# ===============================
# app/routes/memory_routes.py — Soft Delete Ready (No Permission Checks)
# ===============================

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.database import get_db
from app.controllers.memory_controller import (
    create_memory,
    get_memory_by_id,
    list_memories_by_project,
    list_memories_by_agent,
    update_memory,
    delete_memory,
    hard_delete_memory,
)
from app.db.schemas.memory_schema import MemoryCreate, MemoryUpdate, MemoryResponse
from app.services.jwt_service import get_current_user
from app.services.logging_service import system_logger
from app.services.dedupe_service import dedupe_service


router = APIRouter(prefix="/memory", tags=["Memory"])


# ===============================
# 🔹 Create Memory
# ===============================
@router.post("/", response_model=MemoryResponse, status_code=201)
async def create_memory_route(
    request: Request,
    data: MemoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = create_memory(db, data)

        if dedupe_service.should_log_action("MEMORY_CREATE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="MEMORY_CREATE",
                user_id=current_user.userid,
                details=f"Created new memory (Agent ID: {data.agentid}, Project ID: {data.projectid})",
                request=request,
                status="active",
            )

        return result
    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="MEMORY_CREATE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to create memory: {e.detail}",
            request=request,
            status="active",
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="MEMORY_CREATE_ERROR",
            user_id=current_user.userid,
            details=f"Error creating memory: {str(e)}",
            request=request,
            status="active",
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Get Memory by ID
# ===============================
@router.get("/{memoryid}", response_model=MemoryResponse)
async def get_memory_route(
    request: Request,
    memoryid: int,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted memory"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = get_memory_by_id(db, memoryid, include_deleted=include_deleted)

        cache_key = f"memory_view_{memoryid}"
        if dedupe_service.should_log_action("MEMORY_VIEW", current_user.userid, cache_key):
            await system_logger.log_action(
                db=db,
                action_type="MEMORY_VIEW",
                user_id=current_user.userid,
                details=f"Viewed memory ID {memoryid} (include_deleted={include_deleted})",
                request=request,
                status="active",
            )

        return result
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="MEMORY_VIEW_ERROR",
            user_id=current_user.userid,
            details=f"Error viewing memory ID {memoryid}: {str(e)}",
            request=request,
            status="active",
        )
        raise


# ===============================
# 🔹 List Memories by Project
# ===============================
@router.get("/project/{projectid}", response_model=List[MemoryResponse])
async def list_by_project_route(
    request: Request,
    projectid: int,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted memories"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = list_memories_by_project(db, projectid, include_deleted=include_deleted)

        if dedupe_service.should_log_action("MEMORY_LIST_PROJECT", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="MEMORY_LIST_PROJECT",
                user_id=current_user.userid,
                details=f"Listed memories for project {projectid} (include_deleted={include_deleted})",
                request=request,
                status="active",
            )

        return result
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="MEMORY_LIST_PROJECT_ERROR",
            user_id=current_user.userid,
            details=f"Error listing memories for project {projectid}: {str(e)}",
            request=request,
            status="active",
        )
        raise


# ===============================
# 🔹 List Memories by Agent
# ===============================
@router.get("/agent/{agentid}", response_model=List[MemoryResponse])
async def list_by_agent_route(
    request: Request,
    agentid: int,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted memories"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = list_memories_by_agent(db, agentid, include_deleted=include_deleted)

        if dedupe_service.should_log_action("MEMORY_LIST_AGENT", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="MEMORY_LIST_AGENT",
                user_id=current_user.userid,
                details=f"Listed memories for agent {agentid} (include_deleted={include_deleted})",
                request=request,
                status="active",
            )

        return result
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="MEMORY_LIST_AGENT_ERROR",
            user_id=current_user.userid,
            details=f"Error listing memories for agent {agentid}: {str(e)}",
            request=request,
            status="active",
        )
        raise


# ===============================
# 🔹 Update Memory
# ===============================
@router.put("/{memoryid}", response_model=MemoryResponse)
async def update_memory_route(
    request: Request,
    memoryid: int,
    data: MemoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        result = update_memory(db, memoryid, data)

        if dedupe_service.should_log_action("MEMORY_UPDATE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="MEMORY_UPDATE",
                user_id=current_user.userid,
                details=f"Updated memory ID {memoryid}",
                request=request,
                status="active",
            )

        return result
    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="MEMORY_UPDATE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to update memory ID {memoryid}: {e.detail}",
            request=request,
            status="active",
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="MEMORY_UPDATE_ERROR",
            user_id=current_user.userid,
            details=f"Error updating memory ID {memoryid}: {str(e)}",
            request=request,
            status="active",
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Soft Delete Memory
# ===============================
@router.delete("/{memoryid}")
async def delete_memory_route(
    request: Request,
    memoryid: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        memory = get_memory_by_id(db, memoryid)
        result = delete_memory(db, memoryid)

        if dedupe_service.should_log_action("MEMORY_DELETE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="MEMORY_DELETE",
                user_id=current_user.userid,
                details=f"Soft-deleted memory ID {memoryid} (Agent: {memory.agentid}, Project: {memory.projectid})",
                request=request,
                status="inactive",
            )

        return result
    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="MEMORY_DELETE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to delete memory ID {memoryid}: {e.detail}",
            request=request,
            status="active",
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="MEMORY_DELETE_ERROR",
            user_id=current_user.userid,
            details=f"Error deleting memory ID {memoryid}: {str(e)}",
            request=request,
            status="active",
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Hard Delete (Admin Cleanup)
# ===============================
@router.delete("/{memoryid}/purge")
async def hard_delete_memory_route(
    request: Request,
    memoryid: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Permanent deletion for maintenance or admin cleanup (no permission enforced)."""
    try:
        result = hard_delete_memory(db, memoryid)

        await system_logger.log_action(
            db=db,
            action_type="MEMORY_PURGE",
            user_id=current_user.userid,
            details=f"Permanently deleted memory ID {memoryid}",
            request=request,
            status="inactive",
        )

        return result
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="MEMORY_PURGE_ERROR",
            user_id=current_user.userid,
            details=f"Error permanently deleting memory ID {memoryid}: {str(e)}",
            request=request,
            status="active",
        )
        raise HTTPException(status_code=500, detail="Internal server error")
