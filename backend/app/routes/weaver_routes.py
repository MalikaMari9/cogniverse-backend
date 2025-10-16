from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.controllers.weaver_controller import (
    create_weaver,
    get_weaver_by_id,
    list_weavers_by_project,
    list_weavers_by_agent,
    update_weaver,
    delete_weaver,
)
from app.db.schemas.weaver_schema import (
    WeaverCreate,
    WeaverUpdate,
    WeaverResponse,
)
from app.services.jwt_service import get_current_user

router = APIRouter(prefix="/weaver", tags=["Weaver"])


# -------- CREATE --------
@router.post("/", response_model=WeaverResponse)
def create_weaver_route(
    data: WeaverCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return create_weaver(db, data)


# -------- GET BY ID --------
@router.get("/{weaverid}", response_model=WeaverResponse)
def get_weaver_route(
    weaverid: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return get_weaver_by_id(db, weaverid)


# -------- LIST BY PROJECT --------
@router.get("/project/{projectid}", response_model=list[WeaverResponse])
def list_by_project_route(
    projectid: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return list_weavers_by_project(db, projectid)


# -------- LIST BY AGENT --------
@router.get("/agent/{agentid}", response_model=list[WeaverResponse])
def list_by_agent_route(
    agentid: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return list_weavers_by_agent(db, agentid)


# -------- UPDATE --------
@router.put("/{weaverid}", response_model=WeaverResponse)
def update_weaver_route(
    weaverid: int,
    data: WeaverUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return update_weaver(db, weaverid, data)


# -------- DELETE --------
@router.delete("/{weaverid}")
def delete_weaver_route(
    weaverid: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return delete_weaver(db, weaverid)
