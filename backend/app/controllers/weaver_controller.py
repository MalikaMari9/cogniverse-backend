from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.weaver_model import Weaver
from app.db.schemas.weaver_schema import WeaverCreate, WeaverUpdate


# -------------------------------------------
# CREATE WEAVER
# -------------------------------------------
def create_weaver(db: Session, data: WeaverCreate):
    new_weaver = Weaver(
        weavercontent=data.weavercontent,
        agentid=data.agentid,
        projectid=data.projectid,
    )
    db.add(new_weaver)
    db.commit()
    db.refresh(new_weaver)
    return new_weaver


# -------------------------------------------
# GET WEAVER BY ID
# -------------------------------------------
def get_weaver_by_id(db: Session, weaverid: int):
    weaver = db.query(Weaver).filter(Weaver.weaverid == weaverid).first()
    if not weaver:
        raise HTTPException(status_code=404, detail="Weaver not found")
    return weaver


# -------------------------------------------
# LIST WEAVERS BY PROJECT
# -------------------------------------------
def list_weavers_by_project(db: Session, projectid: int):
    return db.query(Weaver).filter(Weaver.projectid == projectid).all()


# -------------------------------------------
# LIST WEAVERS BY AGENT
# -------------------------------------------
def list_weavers_by_agent(db: Session, agentid: int):
    return db.query(Weaver).filter(Weaver.agentid == agentid).all()


# -------------------------------------------
# UPDATE WEAVER
# -------------------------------------------
def update_weaver(db: Session, weaverid: int, data: WeaverUpdate):
    weaver = get_weaver_by_id(db, weaverid)
    if data.weavercontent is not None:
        weaver.weavercontent = data.weavercontent
    if data.status is not None:
        weaver.status = data.status
    db.commit()
    db.refresh(weaver)
    return weaver


# -------------------------------------------
# SOFT DELETE WEAVER
# -------------------------------------------
def delete_weaver(db: Session, weaverid: int):
    weaver = get_weaver_by_id(db, weaverid)
    weaver.status = "deleted"
    db.commit()
    return {"message": "Weaver deleted successfully"}
