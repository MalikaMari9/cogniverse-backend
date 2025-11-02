# ===============================
# app/controllers/result_controller.py — Soft Delete Ready
# ===============================

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.result_model import Result, ResultType
from app.db.schemas.result_schema import ResultCreate, ResultUpdate
import json
from typing import Dict, Any, List
from app.db.models.scenario_model import Scenario
from fastapi import HTTPException

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


# Simulation Results Store



def save_simulation_results(
    db: Session,
    *,
    scenarioid: int,
    projectid: int,
    simulation: Dict[str, Any],
    logs: List[Dict[str, Any]],
    agentLogs: Dict[str, List[Dict[str, Any]]],
    positions: List[Dict[str, Any]] = [],
):
    
    print("💾 Incoming payload:",
      f"scenarioid={scenarioid!r}, projectid={projectid!r},",
      f"logs={len(logs)}, agents={len(agentLogs)}, positions={len(positions)}")

    """
    Persist a finished simulation snapshot into result_tbl.
    Handles system logs, emotions, memories, corrosion, and agent positions.
    """
    # 1️⃣ Validate scenario
    scenario = db.query(Scenario).filter(
        Scenario.scenarioid == scenarioid,
        Scenario.is_deleted == False,
    ).first()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    if int(scenario.projectid) != int(projectid):
        raise HTTPException(status_code=400, detail="Scenario does not belong to this project")

    # 2️⃣ Begin collecting results
    seq = 1
    counts = {
        "system": 0,
        "emotion": 0,
        "memory": 0,
        "corrosion": 0,
        "position": 0,
    }

    try:
        # ---------------------------------------------------------
        # 🧩 System logs (main narration)
        # ---------------------------------------------------------
        for item in logs or []:
            db.add(Result(
                projectagentid=None,
                scenarioid=scenarioid,
                resulttype=ResultType.system,
                sequence_no=seq,
                confidence_score=None,
                resulttext=json.dumps({
                    "turn": item.get("turn"),
                    "who": item.get("who") or "System",
                    "text": item.get("text", ""),
                }),
            ))
            seq += 1
            counts["system"] += 1

        # ---------------------------------------------------------
        # 💭 Agent logs (emotion, memory, corrosion)
        # ---------------------------------------------------------
        for agent_key, entries in (agentLogs or {}).items():
            # Try to interpret key as projectagentid
            try:
                projectagentid = int(agent_key)
            except (ValueError, TypeError):
                projectagentid = None

            for snap in entries or []:
                # Emotion
                if snap.get("emotion"):
                    db.add(Result(
                        projectagentid=projectagentid,
                        scenarioid=scenarioid,
                        resulttype=ResultType.emotion,
                        sequence_no=seq,
                        confidence_score=None,
                        resulttext=json.dumps({
                            "agent": agent_key,
                            "time": snap.get("time"),
                            "emotion": snap.get("emotion"),
                        }),
                    ))
                    seq += 1
                    counts["emotion"] += 1

                # Memory
                if snap.get("memory"):
                    db.add(Result(
                        projectagentid=projectagentid,
                        scenarioid=scenarioid,
                        resulttype=ResultType.memory,
                        sequence_no=seq,
                        confidence_score=None,
                        resulttext=json.dumps({
                            "agent": agent_key,
                            "time": snap.get("time"),
                            "memory": snap.get("memory"),
                        }),
                    ))
                    seq += 1
                    counts["memory"] += 1

                # Corrosion
                if snap.get("corrosion"):
                    db.add(Result(
                        projectagentid=projectagentid,
                        scenarioid=scenarioid,
                        resulttype=ResultType.corrosion,
                        sequence_no=seq,
                        confidence_score=None,
                        resulttext=json.dumps({
                            "agent": agent_key,
                            "time": snap.get("time"),
                            "corrosion": snap.get("corrosion"),
                        }),
                    ))
                    seq += 1
                    counts["corrosion"] += 1

        # 🧭 Agent positions
        for p in positions or []:
            projectagentid = p.get("projectagentid")
            try:
                projectagentid = int(projectagentid) if projectagentid is not None else None
            except (ValueError, TypeError):
                projectagentid = None

            db.add(Result(
                projectagentid=projectagentid,
                scenarioid=scenarioid,
                resulttype=ResultType.position,
                sequence_no=seq,
                confidence_score=None,
                resulttext=json.dumps({
                    "agent": p.get("agent"),
                    "x": p.get("x"),
                    "y": p.get("y"),
                    "facing": p.get("facing"),
                }),
            ))
            seq += 1
            counts["position"] += 1

        # ---------------------------------------------------------
        # 🧾 Optional summary record
        # ---------------------------------------------------------
        db.add(Result(
            projectagentid=None,
            scenarioid=scenarioid,
            resulttype=ResultType.summary,
            sequence_no=seq,
            confidence_score=None,
            resulttext=json.dumps({
                "status": "completed",
                "ended_at": datetime.utcnow().isoformat(),
                "entries": sum(counts.values()),
            }),
        ))

        # 3️⃣ Commit
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            import traceback
            print("💥 Commit failed!")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Commit failed: {str(e)}")


        return {
            "detail": f"Saved {sum(counts.values()) + 1} result rows (including summary) for scenario {scenarioid}",
            "counts": counts,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error while saving simulation: {str(e)}")
    
# ============================================================
# 🔹 GET REPLAY DATA BY SCENARIO
# ============================================================
def get_replay_data(db: Session, scenarioid: int):
    """
    Retrieve all saved simulation results grouped by type,
    so the frontend can replay the simulation visually.
    """
    from app.db.models.result_model import Result

    results = (
        db.query(Result)
        .filter(Result.scenarioid == scenarioid, Result.is_deleted == False)
        .order_by(Result.sequence_no.asc(), Result.created_at.asc())
        .all()
    )

    grouped = {
        "scenarioid": scenarioid,
        "system": [],
        "emotion": [],
        "memory": [],
        "corrosion": [],
        "position": [],
    }

    for r in results:
        try:
            data = json.loads(r.resulttext)
            key = r.resulttype.value if hasattr(r.resulttype, "value") else str(r.resulttype)
            grouped.setdefault(key, []).append(data)
        except Exception as e:
            print(f"⚠️ Failed to parse resulttext for id={r.resultid}: {e}")

    return grouped
