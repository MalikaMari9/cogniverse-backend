# app/routes/project_routes.py
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.controllers.project_controller import (
    create_project,
    get_user_projects,
    get_project_by_id,
    update_project,
    delete_project,
)
from app.services.jwt_service import get_current_user
from app.services.utils.permissions_helper import enforce_permission_auto
from app.db.schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

# ============================================================
# 🔹 CREATE PROJECT (requires WRITE access)
# ============================================================
@router.post("/", response_model=ProjectResponse, status_code=201)
def create_new_project(
    project_data: ProjectCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_permission_auto(db, current_user, "PROJECTS", request)
    return create_project(db, current_user.userid, project_data)


# ============================================================
# 🔹 GET ALL USER PROJECTS (requires READ access)
# ============================================================
@router.get("/", response_model=List[ProjectResponse])
def get_all_projects(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_permission_auto(db, current_user, "PROJECTS", request)
    return get_user_projects(db, current_user.userid)


# ============================================================
# 🔹 GET SINGLE PROJECT (requires READ access)
# ============================================================
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_permission_auto(db, current_user, "PROJECTS", request)
    return get_project_by_id(db, project_id, current_user.userid)


# ============================================================
# 🔹 UPDATE PROJECT (requires WRITE access)
# ============================================================
@router.put("/{project_id}", response_model=ProjectResponse)
def update_existing_project(
    project_id: int,
    project_data: ProjectUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_permission_auto(db, current_user, "PROJECTS", request)
    return update_project(db, project_id, current_user.userid, project_data)


# ============================================================
# 🔹 DELETE PROJECT (requires WRITE access)
# ============================================================
@router.delete("/{project_id}")
def remove_project(
    project_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_permission_auto(db, current_user, "PROJECTS", request)
    return delete_project(db, project_id, current_user.userid)
