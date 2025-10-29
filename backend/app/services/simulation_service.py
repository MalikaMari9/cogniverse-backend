from __future__ import annotations

from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


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
        detail: Any
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
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Simulation provider returned invalid JSON payload",
        ) from exc


async def create_simulation(payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _forward_request("POST", "/simulations", payload)


async def get_simulation(simulation_id: str) -> Dict[str, Any]:
    return await _forward_request("GET", f"/simulations/{simulation_id}")


async def advance_simulation(simulation_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _forward_request(
        "POST", f"/simulations/{simulation_id}/advance", payload
    )


async def trigger_fate(simulation_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _forward_request(
        "POST", f"/simulations/{simulation_id}/fate", payload
    )
