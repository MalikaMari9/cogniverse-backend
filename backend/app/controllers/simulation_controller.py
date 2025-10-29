from typing import Any, Dict

from app.db.schemas.simulation_schema import (
    SimulationAdvanceRequest,
    SimulationCreateRequest,
    SimulationFateRequest,
)
from app.services import simulation_service


def _serialize(model) -> Dict[str, Any]:
    return model.model_dump(exclude_none=True, by_alias=True)


async def create_simulation(payload: SimulationCreateRequest) -> Dict[str, Any]:
    return await simulation_service.create_simulation(_serialize(payload))


async def get_simulation(simulation_id: str) -> Dict[str, Any]:
    return await simulation_service.get_simulation(simulation_id)


async def advance_simulation(
    simulation_id: str, payload: SimulationAdvanceRequest
) -> Dict[str, Any]:
    return await simulation_service.advance_simulation(
        simulation_id, _serialize(payload)
    )


async def trigger_simulation_fate(
    simulation_id: str, payload: SimulationFateRequest
) -> Dict[str, Any]:
    data = _serialize(payload)
    # Ensure an empty body is still sent as {} instead of None
    return await simulation_service.trigger_fate(simulation_id, data or {})
