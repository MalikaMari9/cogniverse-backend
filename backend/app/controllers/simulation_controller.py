from typing import Any, Dict

from app.db.schemas.simulation_schema import (
    SimulationAdvanceRequest,
    SimulationCreateRequest,
    SimulationFateRequest,
)
from app.services import simulation_service


def _serialize(model) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_none=True, by_alias=True)
    elif isinstance(model, dict):
        return model
    else:
        return {}


async def create_simulation(payload: SimulationCreateRequest) -> Dict[str, Any]:
    print("DEBUG create_simulation payload type:", type(payload))

    return await simulation_service.create_simulation(_serialize(payload))


async def get_simulation(simulation_id: str) -> Dict[str, Any]:
    result = await simulation_service.get_simulation(simulation_id, slim=True)

    print(f"[DEBUG] Controller get_simulation result keys: {list(result.keys())}")
    if "simulation" in result:
        sim = result["simulation"]
        print(f"[DEBUG] Simulation id: {sim.get('id')} | status: {sim.get('status')}")
        print(f"[DEBUG] Event count: {len(sim.get('events', []))}")
        for i, e in enumerate(sim.get("events", [])[:5]):
            print(f"   [{i}] type={e.get('type')} actor={e.get('actor')} text={e.get('text') or e.get('summary')}")
    return result


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
