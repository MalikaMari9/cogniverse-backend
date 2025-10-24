from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.memory_model import Memory
from app.db.schemas.memory_schema import MemoryCreate, MemoryUpdate


# ============================================================
# 🔹 CREATE MEMORY
# ============================================================
def create_memory(db: Session, data: MemoryCreate):
    """Create a new memory entry."""
    try:
        new_memory = Memory(
            memorycontent=data.memorycontent,
            agentid=data.agentid,
            projectid=data.projectid,
        )
        db.add(new_memory)
        db.commit()
        db.refresh(new_memory)
        return new_memory
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================
# 🔹 GET MEMORY BY ID
# ============================================================
def get_memory_by_id(db: Session, memoryid: int, include_deleted: bool = False):
    """Retrieve a memory by ID (excluding deleted unless include_deleted=True)."""
    memory = db.query(Memory).filter(Memory.memoryid == memoryid).first()
    if not memory or (memory.is_deleted and not include_deleted):
        raise HTTPException(status_code=404, detail="Memory not found or deleted")
    return memory


# ============================================================
# 🔹 LIST MEMORIES BY PROJECT
# ============================================================
def list_memories_by_project(db: Session, projectid: int, include_deleted: bool = False):
    """List all memories under a given project."""
    query = db.query(Memory).filter(Memory.projectid == projectid)
    if not include_deleted:
        query = query.filter(Memory.is_deleted == False)
    return query.order_by(Memory.created_at.desc()).all()


# ============================================================
# 🔹 LIST MEMORIES BY AGENT
# ============================================================
def list_memories_by_agent(db: Session, agentid: int, include_deleted: bool = False):
    """List all memories created by a specific agent."""
    query = db.query(Memory).filter(Memory.agentid == agentid)
    if not include_deleted:
        query = query.filter(Memory.is_deleted == False)
    return query.order_by(Memory.created_at.desc()).all()


# ============================================================
# 🔹 UPDATE MEMORY
# ============================================================
def update_memory(db: Session, memoryid: int, data: MemoryUpdate):
    """Update an existing memory entry."""
    memory = db.query(Memory).filter(Memory.memoryid == memoryid).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    if memory.is_deleted:
        raise HTTPException(status_code=400, detail="Cannot update a deleted memory")

    update_fields = data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(memory, key, value)

    db.commit()
    db.refresh(memory)
    return memory


# ============================================================
# 🔹 SOFT DELETE MEMORY
# ============================================================
def delete_memory(db: Session, memoryid: int):
    """Soft delete a memory instead of removing it permanently."""
    memory = db.query(Memory).filter(Memory.memoryid == memoryid).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    if memory.is_deleted:
        raise HTTPException(status_code=400, detail="Memory already deleted")

    memory.is_deleted = True
    memory.deleted_at = datetime.utcnow()

    db.commit()
    return {"detail": f"Memory {memoryid} soft-deleted successfully"}


# ============================================================
# 🔹 HARD DELETE MEMORY (Admin Only)
# ============================================================
def hard_delete_memory(db: Session, memoryid: int):
    """Permanently delete a memory (admin cleanup only)."""
    memory = db.query(Memory).filter(Memory.memoryid == memoryid).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    db.delete(memory)
    db.commit()
    return {"detail": f"Memory {memoryid} permanently deleted"}
