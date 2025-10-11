# app/routes/project_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.controllers.project_controller import (
    create_project,
    get_user_projects,
    get_project_by_id,
    update_project,
    delete_project,
)
from app.services.jwt_service import get_current_user
from app.db.schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectResponse
from typing import List

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse)
def create_new_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_project(db, current_user.userid, project_data)


@router.get("/", response_model=List[ProjectResponse])
def get_all_projects(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_projects(db, current_user.userid)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_project_by_id(db, project_id, current_user.userid)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_existing_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_project(db, project_id, current_user.userid, project_data)


@router.delete("/{project_id}")
def remove_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return delete_project(db, project_id, current_user.userid)
