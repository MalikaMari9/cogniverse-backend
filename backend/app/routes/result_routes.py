# ===============================
# app/routes/result_routes.py — Soft Delete + Logging (No Permissions)
# ===============================

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.controllers import result_controller
from app.db.schemas.result_schema import ResultCreate, ResultUpdate, ResultResponse
from app.services.jwt_service import get_current_user
from app.services.route_logger_helper import log_action, log_error

router = APIRouter(prefix="/results", tags=["Results"])


# ============================================================
# 🔹 Get All Results
# ============================================================
@router.get("/", response_model=List[ResultResponse])
async def get_all_results(
    request: Request,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted results"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = result_controller.get_all_results(db, include_deleted=include_deleted)
        await log_action(
            db, request, current_user,
            "RESULT_LIST_VIEW",
            details=f"Viewed all results (include_deleted={include_deleted})"
        )
        return result
    except Exception as e:
        await log_error(db, request, current_user, "RESULT_LIST_ERROR", e, "Error listing results")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Get Result by ID
# ============================================================
@router.get("/{result_id}", response_model=ResultResponse)
async def get_result_by_id(
    result_id: int,
    request: Request,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted result"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = result_controller.get_result_by_id(db, result_id, include_deleted=include_deleted)
        await log_action(
            db, request, current_user,
            "RESULT_VIEW",
            details=f"Viewed result ID {result_id} (include_deleted={include_deleted})",
            dedupe_key=f"result_{result_id}"
        )
        return result
    except HTTPException as e:
        await log_error(db, request, current_user, "RESULT_VIEW_FAILED", e, f"Failed to view result {result_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "RESULT_VIEW_ERROR", e, f"Error viewing result {result_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Create Result
# ============================================================
@router.post("/", response_model=ResultResponse, status_code=201)
async def create_result(
    result: ResultCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        new_result = result_controller.create_result(db, result)
        await log_action(
            db, request, current_user,
            "RESULT_CREATE",
            details=f"Created result (Type: {result.resulttype}, Scenario ID: {result.scenarioid})"
        )
        return new_result
    except HTTPException as e:
        await log_error(db, request, current_user, "RESULT_CREATE_FAILED", e, "Failed to create result")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "RESULT_CREATE_ERROR", e, "Error creating result")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Update Result
# ============================================================
@router.put("/{result_id}", response_model=ResultResponse)
async def update_result(
    result_id: int,
    result: ResultUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        updated = result_controller.update_result(db, result_id, result)
        await log_action(
            db, request, current_user,
            "RESULT_UPDATE",
            details=f"Updated result ID {result_id}"
        )
        return updated
    except HTTPException as e:
        await log_error(db, request, current_user, "RESULT_UPDATE_FAILED", e, f"Failed to update result {result_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "RESULT_UPDATE_ERROR", e, f"Error updating result {result_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Soft Delete Result
# ============================================================
@router.delete("/{result_id}")
async def delete_result(
    result_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = result_controller.delete_result(db, result_id)
        await log_action(
            db, request, current_user,
            "RESULT_DELETE",
            details=f"Soft-deleted result ID {result_id}"
        )
        return result
    except HTTPException as e:
        await log_error(db, request, current_user, "RESULT_DELETE_FAILED", e, f"Failed to delete result {result_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "RESULT_DELETE_ERROR", e, f"Error deleting result {result_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 List by Agent + Scenario + Type
# ============================================================
@router.get("/agent/{projectagentid}/scenario/{scenarioid}/type/{resulttype}", response_model=List[ResultResponse])
async def get_results_by_agent_scenario_type(
    projectagentid: int,
    scenarioid: int,
    resulttype: str,
    request: Request,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted results"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        results = result_controller.list_results_by_agent_scenario_type(
            db, projectagentid, scenarioid, resulttype, include_deleted=include_deleted
        )
        await log_action(
            db, request, current_user,
            "RESULT_LIST_AGENT_SCENARIO_TYPE",
            details=(
                f"Listed results for Agent {projectagentid}, Scenario {scenarioid}, "
                f"Type '{resulttype}' (include_deleted={include_deleted})"
            ),
        )
        return results
    except HTTPException as e:
        await log_error(
            db, request, current_user,
            "RESULT_LIST_AGENT_SCENARIO_TYPE_FAILED", e,
            f"Failed to list results for Agent {projectagentid}, Scenario {scenarioid}, Type {resulttype}"
        )
        raise e
    except Exception as e:
        await log_error(
            db, request, current_user,
            "RESULT_LIST_AGENT_SCENARIO_TYPE_ERROR", e,
            f"Error listing results for Agent {projectagentid}, Scenario {scenarioid}, Type {resulttype}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")
