"""Incidents API router."""

from typing import Optional

from fastapi import APIRouter, HTTPException

from app.services.state import platform_state

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("")
async def list_incidents(status: Optional[str] = None):
    """List all incidents with optional status filtering."""
    incidents = platform_state.get_incidents(status=status)
    return {"incidents": [i.model_dump() for i in incidents], "total": len(incidents)}


@router.get("/{incident_id}")
async def get_incident(incident_id: str):
    """Get detailed information about a specific incident."""
    incident = platform_state.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident.model_dump()
