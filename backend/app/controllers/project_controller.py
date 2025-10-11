# app/controllers/project_controller.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.project_model import Project
from app.db.schemas.project_schema import ProjectCreate, ProjectUpdate

def create_project(db: Session, user_id: int, project_data: ProjectCreate):
    new_project = Project(
        projectname=project_data.projectname,
        project_desc=project_data.project_desc,
        userid=user_id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

def get_user_projects(db: Session, user_id: int):
    return db.query(Project).filter(Project.userid == user_id).all()

def get_project_by_id(db: Session, project_id: int, user_id: int):
    project = db.query(Project).filter(Project.projectid == project_id, Project.userid == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def update_project(db: Session, project_id: int, user_id: int, project_data: ProjectUpdate):
    project = get_project_by_id(db, project_id, user_id)
    
    # Update only provided fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    return project

def delete_project(db: Session, project_id: int, user_id: int):
    project = get_project_by_id(db, project_id, user_id)
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}