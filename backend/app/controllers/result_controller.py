# ===============================
# app/controllers/result_controller.py — Soft Delete Ready
# ===============================

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.result_model import Result
from app.db.schemas.result_schema import ResultCreate, ResultUpdate


# ============================================================
# 🔹 GET ALL RESULTS
# ============================================================
def get_all_results(db: Session, include_deleted: bool = False):
    """Retrieve all results (exclude soft-deleted by default)."""
    query = db.query(Result)
    if not include_deleted:
        query = query.filter(Result.is_deleted == False)
    return query.order_by(Result.created_at.desc()).all()


# ============================================================
# 🔹 GET SINGLE RESULT
# ============================================================
def get_result_by_id(db: Session, resultid: int, include_deleted: bool = False):
    """Retrieve a single result by ID."""
    result = db.query(Result).filter(Result.resultid == resultid).first()
    if not result or (result.is_deleted and not include_deleted):
        raise HTTPException(status_code=404, detail="Result not found or deleted")
    return result


# ============================================================
# 🔹 CREATE RESULT
# ============================================================
def create_result(db: Session, result_data: ResultCreate):
    """Create a new result entry."""
    try:
        new_result = Result(**result_data.model_dump())
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        return new_result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================
# 🔹 UPDATE RESULT
# ============================================================
def update_result(db: Session, resultid: int, result_data: ResultUpdate):
    """Update an existing result."""
    result = db.query(Result).filter(Result.resultid == resultid).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    if result.is_deleted:
        raise HTTPException(status_code=400, detail="Cannot update a deleted result")

    for key, value in result_data.model_dump(exclude_unset=True).items():
        setattr(result, key, value)

    db.commit()
    db.refresh(result)
    return result


# ============================================================
# 🔹 SOFT DELETE RESULT
# ============================================================
def delete_result(db: Session, resultid: int):
    """Soft delete a result instead of removing it permanently."""
    result = db.query(Result).filter(Result.resultid == resultid).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    if result.is_deleted:
        raise HTTPException(status_code=400, detail="Result already deleted")

    result.is_deleted = True
    result.deleted_at = datetime.utcnow()

    db.commit()
    return {"detail": f"Result {resultid} soft-deleted successfully"}


# ============================================================
# 🔹 HARD DELETE RESULT (Admin Only)
# ============================================================
def hard_delete_result(db: Session, resultid: int):
    """Permanently delete a result (admin cleanup only)."""
    result = db.query(Result).filter(Result.resultid == resultid).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    db.delete(result)
    db.commit()
    return {"detail": f"Result {resultid} permanently deleted"}


# ============================================================
# 🔹 LIST RESULTS BY PROJECT AGENT + SCENARIO + TYPE
# ============================================================
def list_results_by_agent_scenario_type(
    db: Session, projectagentid: int, scenarioid: int, resulttype: str, include_deleted: bool = False
):
    """List all results for a given agent + scenario + result type."""
    query = (
        db.query(Result)
        .filter(
            Result.projectagentid == projectagentid,
            Result.scenarioid == scenarioid,
            Result.resulttype == resulttype,
        )
    )
    if not include_deleted:
        query = query.filter(Result.is_deleted == False)

    results = query.order_by(Result.sequence_no.asc()).all()
    if not results:
        raise HTTPException(status_code=404, detail="No matching results found")

    return results

# ============================================================
# 🔹 GET RESULTS BY SCENARIO
# ============================================================
def get_results_by_scenario(db: Session, scenarioid: int):
    """Retrieve all results linked to a given scenario."""
    from app.db.models.result_model import Result  # adjust if needed

    results = (
        db.query(Result)
        .filter(Result.scenarioid == scenarioid)
        .order_by(Result.sequence_no.asc(), Result.created_at.asc())
        .all()
    )
    return results
