# ===============================
# app/routes/scenario_routes.py — Soft Delete + Logging (No Permissions)
# ===============================

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.controllers import scenario_controller
from app.db.schemas.scenario_schema import ScenarioCreate, ScenarioUpdate, ScenarioResponse
from app.services.jwt_service import get_current_user
from app.services.route_logger_helper import log_action, log_error

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


# ============================================================
# 🔹 Get All Scenarios
# ============================================================
@router.get("/", response_model=List[ScenarioResponse])
async def get_all_scenarios(
    request: Request,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted scenarios"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = scenario_controller.get_all_scenarios(db, include_deleted=include_deleted)

        await log_action(
            db, request, current_user,
            "SCENARIO_LIST_VIEW",
            details=f"Viewed all scenarios (include_deleted={include_deleted})"
        )

        return result
    except Exception as e:
        await log_error(db, request, current_user, "SCENARIO_LIST_ERROR", e, "Error viewing scenarios list")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Get Scenario by ID
# ============================================================
@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario_by_id(
    scenario_id: int,
    request: Request,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted scenario"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        scenario = scenario_controller.get_scenario_by_id(db, scenario_id, include_deleted=include_deleted)

        await log_action(
            db, request, current_user,
            "SCENARIO_VIEW",
            details=f"Viewed scenario ID {scenario_id} (include_deleted={include_deleted})",
            dedupe_key=f"scenario_{scenario_id}"
        )

        return scenario
    except HTTPException as e:
        await log_error(db, request, current_user, "SCENARIO_VIEW_FAILED", e, f"Failed to view scenario {scenario_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "SCENARIO_VIEW_ERROR", e, f"Error viewing scenario {scenario_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Create Scenario
# ============================================================
@router.post("/", response_model=ScenarioResponse, status_code=201)
async def create_scenario(
    scenario: ScenarioCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = scenario_controller.create_scenario(db, scenario)

        await log_action(
            db, request, current_user,
            "SCENARIO_CREATE",
            details=f"Created new scenario '{scenario.name if hasattr(scenario, 'name') else 'Unnamed'}'"
        )

        return result
    except HTTPException as e:
        await log_error(db, request, current_user, "SCENARIO_CREATE_FAILED", e, "Failed to create scenario")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "SCENARIO_CREATE_ERROR", e, "Error creating scenario")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Update Scenario
# ============================================================
@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: int,
    scenario: ScenarioUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        updated = scenario_controller.update_scenario(db, scenario_id, scenario)

        await log_action(
            db, request, current_user,
            "SCENARIO_UPDATE",
            details=f"Updated scenario ID {scenario_id}"
        )

        return updated
    except HTTPException as e:
        await log_error(db, request, current_user, "SCENARIO_UPDATE_FAILED", e, f"Failed to update scenario {scenario_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "SCENARIO_UPDATE_ERROR", e, f"Error updating scenario {scenario_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Soft Delete Scenario
# ============================================================
@router.delete("/{scenario_id}")
async def delete_scenario(
    scenario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = scenario_controller.delete_scenario(db, scenario_id)

        await log_action(
            db, request, current_user,
            "SCENARIO_DELETE",
            details=f"Soft-deleted scenario ID {scenario_id}"
        )

        return result
    except HTTPException as e:
        await log_error(db, request, current_user, "SCENARIO_DELETE_FAILED", e, f"Failed to delete scenario {scenario_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "SCENARIO_DELETE_ERROR", e, f"Error deleting scenario {scenario_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Hard Delete (Admin Cleanup)
# ============================================================
@router.delete("/{scenario_id}/purge")
async def hard_delete_scenario(
    scenario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Permanently delete a scenario (no permission enforcement)."""
    try:
        result = scenario_controller.hard_delete_scenario(db, scenario_id)

        await log_action(
            db, request, current_user,
            "SCENARIO_PURGE",
            details=f"Permanently deleted scenario ID {scenario_id}"
        )

        return result
    except Exception as e:
        await log_error(db, request, current_user, "SCENARIO_PURGE_ERROR", e, f"Error purging scenario {scenario_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/quick", response_model=ScenarioResponse)
async def quick_create_scenario(
    scenario: ScenarioCreate,
    db: Session = Depends(get_db),
):
    """Create a scenario without user context/logging — used by simulation auto-save."""
    try:
        result = scenario_controller.create_scenario(db, scenario)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
