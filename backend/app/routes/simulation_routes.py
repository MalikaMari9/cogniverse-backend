from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import asyncio
from app.controllers import simulation_controller
from app.db.database import get_db
from app.db.schemas.simulation_schema import (
    SimulationAdvanceRequest,
    SimulationCreateRequest,
    SimulationFateRequest,
)
from app.services.jwt_service import get_current_user
from app.services.route_logger_helper import log_action, log_error

router = APIRouter(prefix="/simulations", tags=["Simulations"])


# ============================================================
# 🧩 CREATE SIMULATION
# ============================================================
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_simulation(
    payload: SimulationCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            result = await simulation_controller.create_simulation(payload)
            await log_action(
                db,
                request,
                current_user,
                "SIMULATION_CREATE",
                details=f"Created simulation for scenario: {payload.scenario[:80]}",
            )
            return result
        except HTTPException as exc:
            # 🔁 Retry transient errors only
            if exc.status_code in {502, 503, 504} and attempt < max_attempts:
                print(f"[Retry {attempt}/{max_attempts}] Provider error: {exc.detail}")
                await asyncio.sleep(1 * attempt)
                continue
            # Permanent or final failure
            await log_error(
                db,
                request,
                current_user,
                "SIMULATION_CREATE_FAILED",
                exc,
                f"Simulation create failed (attempt {attempt})",
            )
            raise
        except Exception as exc:
            # 🔁 Retry generic error
            if attempt < max_attempts:
                print(f"[Retry {attempt}/{max_attempts}] Generic error: {exc}")
                await asyncio.sleep(1 * attempt)
                continue
            await log_error(
                db,
                request,
                current_user,
                "SIMULATION_CREATE_ERROR",
                exc,
                "Error creating simulation after retries",
            )
            raise HTTPException(status_code=500, detail="Simulation service error") from exc

# ============================================================
# 🧩 GET SIMULATION BY ID
# ============================================================
@router.get("/{simulation_id}", status_code=status.HTTP_200_OK)
async def get_simulation(
    simulation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await simulation_controller.get_simulation(simulation_id)
        await log_action(
            db,
            request,
            current_user,
            "SIMULATION_VIEW",
            details=f"Viewed simulation {simulation_id}",
            dedupe_key=f"simulation_{simulation_id}",
        )

        # --- Debug: pretty print outgoing payload ---
        try:
            import json
            print(f"[DEBUG ROUTE] Outgoing SimulationResponse for {simulation_id}:")
            print(json.dumps(result, indent=2)[:4000])
        except Exception as e:
            print("[DEBUG ROUTE] (could not serialize result)", e)

        return result  # ✅ send everything to frontend untouched
    except HTTPException as exc:
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_VIEW_FAILED",
            exc,
            f"Failed to view simulation {simulation_id}",
        )
        raise
    except Exception as exc:
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_VIEW_ERROR",
            exc,
            f"Error viewing simulation {simulation_id}",
        )
        raise HTTPException(status_code=500, detail="Simulation service error") from exc


# ============================================================
# 🧩 ADVANCE SIMULATION
# ============================================================
@router.post("/{simulation_id}/advance", status_code=status.HTTP_200_OK)
async def advance_simulation(
    simulation_id: str,
    payload: SimulationAdvanceRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await simulation_controller.advance_simulation(simulation_id, payload)
        await log_action(
            db,
            request,
            current_user,
            "SIMULATION_ADVANCE",
            details=f"Advanced simulation {simulation_id} by {payload.steps} step(s)",
        )
        return result  # ✅ direct JSON pass-through
    except HTTPException as exc:
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_ADVANCE_FAILED",
            exc,
            f"Failed to advance simulation {simulation_id}",
        )
        raise
    except Exception as exc:
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_ADVANCE_ERROR",
            exc,
            f"Error advancing simulation {simulation_id}",
        )
        raise HTTPException(status_code=500, detail="Simulation service error") from exc


# ============================================================
# 🧩 TRIGGER FATE
# ============================================================
@router.post("/{simulation_id}/fate", status_code=status.HTTP_200_OK)
async def trigger_simulation_fate(
    simulation_id: str,
    payload: SimulationFateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await simulation_controller.trigger_simulation_fate(simulation_id, payload)
        summary = (
            payload.prompt[:80] if payload.prompt else "No prompt provided (random fate)"
        )
        await log_action(
            db,
            request,
            current_user,
            "SIMULATION_FATE",
            details=f"Triggered fate for simulation {simulation_id}: {summary}",
        )
        return result  # ✅ full data preserved
    except HTTPException as exc:
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_FATE_FAILED",
            exc,
            f"Failed to trigger fate for simulation {simulation_id}",
        )
        raise
    except Exception as exc:
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_FATE_ERROR",
            exc,
            f"Error triggering fate for simulation {simulation_id}",
        )
        raise HTTPException(status_code=500, detail="Simulation service error") from exc


@router.post("/{simulation_id}/pause", status_code=status.HTTP_200_OK)
async def pause_simulation(
    simulation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await simulation_controller.pause_simulation(simulation_id)
        await log_action(
            db,
            request,
            current_user,
            "SIMULATION_PAUSE",
            details=f"Paused simulation {simulation_id}",
        )
        return result
    except HTTPException as exc:
        await log_error(db, request, current_user, "SIMULATION_PAUSE_FAILED", exc)
        raise
    except Exception as exc:
        await log_error(db, request, current_user, "SIMULATION_PAUSE_ERROR", exc)
        raise HTTPException(status_code=500, detail="Simulation service error") from exc


@router.post("/{simulation_id}/stop", status_code=status.HTTP_200_OK)
async def stop_simulation(
    simulation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await simulation_controller.stop_simulation(simulation_id)
        await log_action(
            db,
            request,
            current_user,
            "SIMULATION_STOP",
            details=f"Stopped simulation {simulation_id}",
        )
        return result
    except HTTPException as exc:
        await log_error(db, request, current_user, "SIMULATION_STOP_FAILED", exc)
        raise
    except Exception as exc:
        await log_error(db, request, current_user, "SIMULATION_STOP_ERROR", exc)
        raise HTTPException(status_code=500, detail="Simulation service error") from exc
