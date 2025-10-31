from __future__ import annotations
from typing import Any, Dict, Optional
import httpx, json
from fastapi import HTTPException, status
from app.core.config import settings

# ───────────────────────────────────────────────
# 🧠 In-memory cache for user-submitted agent names
# ───────────────────────────────────────────────
payload_agents_cache: dict[str, list[str]] = {}


def _build_url(path: str) -> str:
    base = settings.simulation_service_base_url.rstrip("/")
    segment = path.lstrip("/")
    return f"{base}/{segment}"


def _build_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if settings.simulation_service_api_key:
        headers["Authorization"] = f"Bearer {settings.simulation_service_api_key}"
    return headers


async def _forward_request(
    method: str, path: str, payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    url = _build_url(path)
    headers = _build_headers()

    try:
        async with httpx.AsyncClient(
            timeout=settings.simulation_service_timeout_seconds
        ) as client:
            response = await client.request(
                method=method.upper(),
                url=url,
                json=payload,
                headers=headers,
            )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json()
        except ValueError:
            detail = exc.response.text or exc.response.reason_phrase
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Simulation provider unreachable: {exc}",
        ) from exc

    try:
        return response.json()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Simulation provider returned invalid JSON payload",
        )


# ───────────────────────────────────────────────
# 🧩 CREATE SIMULATION
# ───────────────────────────────────────────────
async def create_simulation(payload: Dict[str, Any]) -> Dict[str, Any]:
    agents = payload.get("custom_agents") or []
    max_agents = 5
    if len(agents) > max_agents:
        agents = agents[:max_agents]

    for a in agents:
        for k in ["id", "agentid", "projectagentid"]:
            a.pop(k, None)

    payload["custom_agents"] = agents
    payload["strict_agent_mode"] = True
    payload["force_agent_count"] = len(agents)
    payload["allow_background_npcs"] = False
    payload["interaction_schema"] = {
        "mode": "closed_cast",
        "fallback": "ignore_unlisted",
    }

    # 🧠 Cache agent names for later filtering
    agent_names = [a.get("name") for a in agents if a.get("name")]
    scenario_key = payload.get("scenario") or "unknown_scenario"
    payload_agents_cache[scenario_key] = agent_names

    print("[DEBUG] Final simulation payload before POST:")
    print(json.dumps(payload, indent=2)[:1000])

    return await _forward_request("POST", "/simulations", payload)

# =====================================================
# Simulation Service — get_simulation()
# =====================================================

async def get_simulation(simulation_id: str, slim: bool = False) -> Dict[str, Any]:
    """
    Fetch a simulation from the provider, optionally slimmed down
    to remove unnecessary NPCs, verbose event history, and duplicate data.
    """
    data = await _forward_request("GET", f"/simulations/{simulation_id}")

    # ───────────────────────────────────────────────
    # 🔹 Full version (used by internal calls or admin)
    # ───────────────────────────────────────────────
    if not slim:
        return data

    # ───────────────────────────────────────────────
    # 🔹 Slim mode (frontend-friendly)
    # ───────────────────────────────────────────────
    sim = data.get("simulation", {})
    events = sim.get("events", [])
    agents = sim.get("agents", [])

    # 🎯 Trim only the last few events to reduce payload
    trimmed_events = events[-3:] if len(events) > 3 else events

    # 🎯 Determine allowed agent names (from scenario cache)
    allowed_names = set()
    scenario_text = sim.get("scenario", "")
    for key, cached_names in payload_agents_cache.items():
        if key.lower() in scenario_text.lower():
            allowed_names.update(cached_names)
    if not allowed_names:
        # fallback in case scenario cache misses
        allowed_names.update(["Carlos", "Lady Banica", "Lady Banics"])

    # ───────────────────────────────────────────────
    # 🔹 Build detailed filtered agent list
    #     → preserves full mental/cognitive attributes
    # ───────────────────────────────────────────────
    filtered_agents = []
    for a in agents:
        if a.get("name") not in allowed_names:
            continue

        filtered_agents.append({
            "id": a.get("id"),
            "name": a.get("name"),
            "role": a.get("role"),
            "persona": a.get("persona"),
            "mbti": a.get("mbti"),
            "cognitive_bias": a.get("cognitive_bias"),
            "motivation": a.get("motivation"),
            "secret_agenda": a.get("secret_agenda"),
            "agenda_progress": a.get("agenda_progress"),
            "memory": a.get("memory"),
            "corroded_memory": a.get("corroded_memory"),
            "traits": a.get("traits"),
            "skills": a.get("skills"),
            "quirks": a.get("quirks"),
            "constraints": a.get("constraints"),
            "biography": a.get("biography"),
            "emotional_state": a.get("emotional_state"),
            "last_action": a.get("last_action"),
            "turn_count": a.get("turn_count"),
            "position": a.get("position"),
        })

    # 🧠 Build set of allowed agent IDs for event filtering
    allowed_agent_ids = {a.get("id") for a in filtered_agents}

    # ───────────────────────────────────────────────
    # 🔹 Filter out NPC events & redundant system logs
    # ───────────────────────────────────────────────
    filtered_events = []
    for e in trimmed_events:
        actor_id = e.get("actor_id")
        event_type = e.get("type", "")
        summary = e.get("summary", "")

        # skip ghost NPCs
        if actor_id and actor_id not in allowed_agent_ids:
            continue

        # skip redundant system messages
        if event_type == "system" and (
            "Agents initialized" in summary or
            "Simulation created" in summary or
            "entered the scenario" in e.get("details", "")
        ):
            continue

        filtered_events.append(e)

    # ───────────────────────────────────────────────
    # 🔹 Build trimmed simulation structure
    # ───────────────────────────────────────────────
    slim_sim = {
        "id": sim.get("id"),
        "scenario": sim.get("scenario"),
        "status": sim.get("status"),
        "created_at": sim.get("created_at"),
        "updated_at": sim.get("updated_at"),
        "active_agent_index": sim.get("active_agent_index"),
        "agents": filtered_agents,
        "events": filtered_events,
    }

    print(
        f"[DEBUG] Slimmed simulation response → {len(filtered_agents)} agents, "
        f"{len(filtered_events)} filtered events"
    )
    return {"simulation": slim_sim}

# ───────────────────────────────────────────────
# 🧩 ADVANCE & FATE (unchanged)
# ───────────────────────────────────────────────
async def advance_simulation(simulation_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _forward_request(
        "POST", f"/simulations/{simulation_id}/advance", payload
    )


async def trigger_fate(simulation_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _forward_request(
        "POST", f"/simulations/{simulation_id}/fate", payload
    )
