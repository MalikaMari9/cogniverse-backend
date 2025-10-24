# ===============================
# app/controllers/project_controller.py — Soft Delete Ready
# ===============================

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.project_model import Project
from app.db.schemas.project_schema import ProjectCreate, ProjectUpdate


# ============================================================
# 🔹 CREATE PROJECT
# ============================================================
def create_project(db: Session, user_id: int, project_data: ProjectCreate):
    """Create a new project for the given user."""
    try:
        new_project = Project(
            projectname=project_data.projectname,
            project_desc=project_data.project_desc,
            userid=user_id,
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return new_project
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================
# 🔹 GET USER PROJECTS
# ============================================================
def get_user_projects(db: Session, user_id: int, include_deleted: bool = False):
    """Get all projects for a user (exclude deleted by default)."""
    query = db.query(Project).filter(Project.userid == user_id)
    if not include_deleted:
        query = query.filter(Project.is_deleted == False)
    return query.order_by(Project.created_at.desc()).all()


# ============================================================
# 🔹 GET PROJECT BY ID
# ============================================================
def get_project_by_id(db: Session, project_id: int, user_id: int, include_deleted: bool = False):
    """Retrieve a project by ID (only if it belongs to the user)."""
    project = (
        db.query(Project)
        .filter(Project.projectid == project_id, Project.userid == user_id)
        .first()
    )
    if not project or (project.is_deleted and not include_deleted):
        raise HTTPException(status_code=404, detail="Project not found or deleted")
    return project


# ============================================================
# 🔹 UPDATE PROJECT
# ============================================================
def update_project(db: Session, project_id: int, user_id: int, project_data: ProjectUpdate):
    """Update an existing project."""
    project = db.query(Project).filter(Project.projectid == project_id, Project.userid == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.is_deleted:
        raise HTTPException(status_code=400, detail="Cannot update a deleted project")

    update_fields = project_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


# ============================================================
# 🔹 SOFT DELETE PROJECT
# ============================================================
def delete_project(db: Session, project_id: int, user_id: int):
    """Soft delete a project (mark as deleted instead of removing)."""
    project = db.query(Project).filter(Project.projectid == project_id, Project.userid == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.is_deleted:
        raise HTTPException(status_code=400, detail="Project already deleted")

    project.is_deleted = True
    project.deleted_at = datetime.utcnow()

    db.commit()
    return {"detail": f"Project {project_id} soft-deleted successfully"}


# ============================================================
# 🔹 HARD DELETE PROJECT (Admin Only)
# ============================================================
def hard_delete_project(db: Session, project_id: int, user_id: int):
    """Permanently delete a project (admin cleanup only)."""
    project = db.query(Project).filter(Project.projectid == project_id, Project.userid == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"detail": f"Project {project_id} permanently deleted"}
