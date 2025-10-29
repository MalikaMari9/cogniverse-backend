from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.controllers import simulation_controller
from app.db.database import get_db
from app.db.schemas.simulation_schema import (
    SimulationAdvanceRequest,
    SimulationCreateRequest,
    SimulationFateRequest,
    SimulationResponse,
)
from app.services.jwt_service import get_current_user
from app.services.route_logger_helper import log_action, log_error

router = APIRouter(prefix="/simulations", tags=["Simulations"])


@router.post("/", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
async def create_simulation(
    payload: SimulationCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await simulation_controller.create_simulation(payload)
        await log_action(
            db,
            request,
            current_user,
            "SIMULATION_CREATE",
            details=f"Created simulation for scenario: {payload.scenario[:80]}",
        )
        return SimulationResponse.model_validate(result)
    except HTTPException as exc:
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_CREATE_FAILED",
            exc,
            "Failed to create simulation",
        )
        raise exc
    except Exception as exc:  # pragma: no cover - defensive
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_CREATE_ERROR",
            exc,
            "Error creating simulation",
        )
        raise HTTPException(status_code=500, detail="Simulation service error") from exc


@router.get(
    "/{simulation_id}",
    response_model=SimulationResponse,
    status_code=status.HTTP_200_OK,
)
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
        return SimulationResponse.model_validate(result)
    except HTTPException as exc:
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_VIEW_FAILED",
            exc,
            f"Failed to view simulation {simulation_id}",
        )
        raise exc
    except Exception as exc:  # pragma: no cover - defensive
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_VIEW_ERROR",
            exc,
            f"Error viewing simulation {simulation_id}",
        )
        raise HTTPException(status_code=500, detail="Simulation service error") from exc


@router.post(
    "/{simulation_id}/advance",
    response_model=SimulationResponse,
    status_code=status.HTTP_200_OK,
)
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
        return SimulationResponse.model_validate(result)
    except HTTPException as exc:
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_ADVANCE_FAILED",
            exc,
            f"Failed to advance simulation {simulation_id}",
        )
        raise exc
    except Exception as exc:  # pragma: no cover - defensive
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_ADVANCE_ERROR",
            exc,
            f"Error advancing simulation {simulation_id}",
        )
        raise HTTPException(status_code=500, detail="Simulation service error") from exc


@router.post(
    "/{simulation_id}/fate",
    response_model=SimulationResponse,
    status_code=status.HTTP_200_OK,
)
async def trigger_simulation_fate(
    simulation_id: str,
    payload: SimulationFateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await simulation_controller.trigger_simulation_fate(
            simulation_id, payload
        )
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
        return SimulationResponse.model_validate(result)
    except HTTPException as exc:
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_FATE_FAILED",
            exc,
            f"Failed to trigger fate for simulation {simulation_id}",
        )
        raise exc
    except Exception as exc:  # pragma: no cover - defensive
        await log_error(
            db,
            request,
            current_user,
            "SIMULATION_FATE_ERROR",
            exc,
            f"Error triggering fate for simulation {simulation_id}",
        )
        raise HTTPException(status_code=500, detail="Simulation service error") from exc
