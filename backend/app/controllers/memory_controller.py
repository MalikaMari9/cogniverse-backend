from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.memory_model import Memory
from app.db.schemas.memory_schema import MemoryCreate, MemoryUpdate


# -------------------------------------------
# CREATE MEMORY
# -------------------------------------------
def create_memory(db: Session, data: MemoryCreate):
    new_memory = Memory(
        memorycontent=data.memorycontent,
        agentid=data.agentid,
        projectid=data.projectid,
    )
    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)
    return new_memory


# -------------------------------------------
# GET MEMORY BY ID
# -------------------------------------------
def get_memory_by_id(db: Session, memoryid: int):
    memory = db.query(Memory).filter(Memory.memoryid == memoryid).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


# -------------------------------------------
# LIST MEMORIES BY PROJECT
# -------------------------------------------
def list_memories_by_project(db: Session, projectid: int):
    return db.query(Memory).filter(Memory.projectid == projectid).all()


# -------------------------------------------
# LIST MEMORIES BY AGENT
# -------------------------------------------
def list_memories_by_agent(db: Session, agentid: int):
    return db.query(Memory).filter(Memory.agentid == agentid).all()


# -------------------------------------------
# UPDATE MEMORY
# -------------------------------------------
def update_memory(db: Session, memoryid: int, data: MemoryUpdate):
    memory = get_memory_by_id(db, memoryid)
    if data.memorycontent is not None:
        memory.memorycontent = data.memorycontent
    if data.status is not None:
        memory.status = data.status
    db.commit()
    db.refresh(memory)
    return memory


# -------------------------------------------
# SOFT DELETE MEMORY
# -------------------------------------------
def delete_memory(db: Session, memoryid: int):
    memory = get_memory_by_id(db, memoryid)
    memory.status = "deleted"
    db.commit()
    return {"message": "Memory deleted successfully"}
