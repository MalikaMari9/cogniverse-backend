# app/controllers/project_controller.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.project_model import Project
from app.db.schemas.project_schema import ProjectCreate, ProjectUpdate

def create_project(db: Session, user_id: int, project_data: ProjectCreate):
    new_project = Project(
        projectName=project_data.projectName,
        project_desc=project_data.project_desc,
        userID=user_id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


def get_user_projects(db: Session, user_id: int):
    return db.query(Project).filter(Project.userID == user_id).all()


def get_project_by_id(db: Session, project_id: int, user_id: int):
    project = db.query(Project).filter(Project.projectID == project_id, Project.userID == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def update_project(db: Session, project_id: int, user_id: int, project_data: ProjectUpdate):
    project = get_project_by_id(db, project_id, user_id)
    if project_data.projectName:
        project.projectName = project_data.projectName
    if project_data.project_desc:
        project.project_desc = project_data.project_desc
    if project_data.status:
        project.status = project_data.status

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int, user_id: int):
    project = get_project_by_id(db, project_id, user_id)
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
