"""Threats API router."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.state import platform_state

router = APIRouter(prefix="/api/threats", tags=["threats"])


class ThreatResponseRequest(BaseModel):
    action: str  # contain, investigate, remediate, false_positive


@router.get("")
async def list_threats(status: Optional[str] = None, severity: Optional[str] = None):
    """List all detected threats with optional filtering."""
    threats = platform_state.get_threats(status=status, severity=severity)
    return {"threats": [t.model_dump() for t in threats], "total": len(threats)}


@router.get("/{threat_id}")
async def get_threat(threat_id: str):
    """Get detailed information about a specific threat."""
    threat = platform_state.get_threat(threat_id)
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    return threat.model_dump()


@router.post("/{threat_id}/respond")
async def respond_to_threat(threat_id: str, request: ThreatResponseRequest):
    """Execute a response action against a threat."""
    result = platform_state.respond_to_threat(threat_id, request.action)
    if not result:
        raise HTTPException(status_code=404, detail="Threat not found")
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
