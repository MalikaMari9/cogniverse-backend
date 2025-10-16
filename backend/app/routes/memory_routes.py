from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.controllers.memory_controller import (
    create_memory,
    get_memory_by_id,
    list_memories_by_project,
    list_memories_by_agent,
    update_memory,
    delete_memory,
)
from app.db.schemas.memory_schema import (
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
)
from app.services.jwt_service import get_current_user

router = APIRouter(prefix="/memory", tags=["Memory"])


# -------- CREATE --------
@router.post("/", response_model=MemoryResponse)
def create_memory_route(
    data: MemoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return create_memory(db, data)


# -------- GET BY ID --------
@router.get("/{memoryid}", response_model=MemoryResponse)
def get_memory_route(
    memoryid: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return get_memory_by_id(db, memoryid)


# -------- LIST BY PROJECT --------
@router.get("/project/{projectid}", response_model=list[MemoryResponse])
def list_by_project_route(
    projectid: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return list_memories_by_project(db, projectid)


# -------- LIST BY AGENT --------
@router.get("/agent/{agentid}", response_model=list[MemoryResponse])
def list_by_agent_route(
    agentid: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return list_memories_by_agent(db, agentid)


# -------- UPDATE --------
@router.put("/{memoryid}", response_model=MemoryResponse)
def update_memory_route(
    memoryid: int,
    data: MemoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return update_memory(db, memoryid, data)


# -------- DELETE --------
@router.delete("/{memoryid}")
def delete_memory_route(
    memoryid: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return delete_memory(db, memoryid)
