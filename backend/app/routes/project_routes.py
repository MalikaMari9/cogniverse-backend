# ===============================
# app/routes/project_routes.py — Soft Delete Integrated
# ===============================

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.controllers.project_controller import (
    create_project,
    get_user_projects,
    get_project_by_id,
    update_project,
    delete_project,
    hard_delete_project,
)
from app.db.schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.jwt_service import get_current_user
from app.services.utils.permissions_helper import enforce_permission_auto
from app.services.route_logger_helper import log_action, log_error

router = APIRouter(prefix="/projects", tags=["Projects"])


# ============================================================
# 🔹 CREATE PROJECT (requires WRITE access)
# ============================================================
@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_new_project(
    project_data: ProjectCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        enforce_permission_auto(db, current_user, "PROJECTS", request)
        result = create_project(db, current_user.userid, project_data)

        await log_action(
            db, request, current_user,
            "PROJECT_CREATE",
            details=f"Created project '{project_data.projectname}' (User ID {current_user.userid})"
        )
        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "PROJECT_CREATE_FAILED", e, "Failed to create project")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "PROJECT_CREATE_ERROR", e, "Error creating project")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 GET ALL USER PROJECTS (requires READ access)
# ============================================================
@router.get("/", response_model=List[ProjectResponse])
async def get_all_projects(
    request: Request,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted projects"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        enforce_permission_auto(db, current_user, "PROJECTS", request)
        result = get_user_projects(db, current_user.userid, include_deleted=include_deleted)

        await log_action(
            db, request, current_user,
            "PROJECT_LIST_VIEW",
            details=f"Viewed all projects for user ID {current_user.userid} (include_deleted={include_deleted})"
        )
        return result

    except Exception as e:
        await log_error(db, request, current_user, "PROJECT_LIST_ERROR", e, "Error viewing project list")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 GET SINGLE PROJECT (requires READ access)
# ============================================================
@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    request: Request,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted project"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        enforce_permission_auto(db, current_user, "PROJECTS", request)
        project = get_project_by_id(db, project_id, current_user.userid, include_deleted=include_deleted)

        await log_action(
            db, request, current_user,
            "PROJECT_VIEW",
            details=f"Viewed project ID {project_id} ('{project.projectname}', include_deleted={include_deleted})",
            dedupe_key=f"project_{project_id}"
        )
        return project

    except HTTPException as e:
        await log_error(db, request, current_user, "PROJECT_VIEW_FAILED", e, f"Failed to view project {project_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "PROJECT_VIEW_ERROR", e, f"Error viewing project {project_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 UPDATE PROJECT (requires WRITE access)
# ============================================================
@router.put("/{project_id}", response_model=ProjectResponse)
async def update_existing_project(
    project_id: int,
    project_data: ProjectUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        enforce_permission_auto(db, current_user, "PROJECTS", request)
        old_project = get_project_by_id(db, project_id, current_user.userid)
        if not old_project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        result = update_project(db, project_id, current_user.userid, project_data)

        await log_action(
            db, request, current_user,
            "PROJECT_UPDATE",
            details=f"Updated project ID {project_id} ('{old_project.projectname}')"
        )
        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "PROJECT_UPDATE_FAILED", e, f"Failed to update project {project_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "PROJECT_UPDATE_ERROR", e, f"Error updating project {project_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 SOFT DELETE PROJECT (requires WRITE access)
# ============================================================
@router.delete("/{project_id}")
async def remove_project(
    project_id: int,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        enforce_permission_auto(db, current_user, "PROJECTS", request)
        result = delete_project(db, project_id, current_user.userid)

        await log_action(
            db, request, current_user,
            "PROJECT_DELETE",
            details=f"Soft-deleted project ID {project_id}"
        )
        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "PROJECT_DELETE_FAILED", e, f"Failed to delete project {project_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "PROJECT_DELETE_ERROR", e, f"Error deleting project {project_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 HARD DELETE (Admin / Maintenance Cleanup)
# ============================================================
@router.delete("/{project_id}/purge")
async def hard_remove_project(
    project_id: int,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permanently delete a project (admin cleanup only)."""
    try:
        enforce_permission_auto(db, current_user, "PROJECTS", request, admin_only=True)
        result = hard_delete_project(db, project_id, current_user.userid)

        await log_action(
            db, request, current_user,
            "PROJECT_PURGE",
            details=f"Permanently deleted project ID {project_id}"
        )
        return result

    except Exception as e:
        await log_error(db, request, current_user, "PROJECT_PURGE_ERROR", e, f"Error purging project {project_id}")
        raise HTTPException(status_code=500, detail="Internal server error")
