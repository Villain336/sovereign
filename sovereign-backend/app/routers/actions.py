"""Pending actions (human-in-the-loop) API router."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.state import platform_state

router = APIRouter(prefix="/api/actions", tags=["actions"])


class ActionDecision(BaseModel):
    decision: str  # approve, reject
    decided_by: str = "user"


@router.get("/pending")
async def list_pending_actions():
    """List all actions pending human approval."""
    actions = platform_state.get_pending_actions()
    return {"actions": [a.model_dump() for a in actions], "total": len(actions)}


@router.post("/{action_id}/decide")
async def decide_action(action_id: str, request: ActionDecision):
    """Approve or reject a pending action."""
    if request.decision == "approve":
        result = platform_state.approve_action(action_id, request.decided_by)
    elif request.decision == "reject":
        result = platform_state.reject_action(action_id, request.decided_by)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown decision: {request.decision}")

    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result.model_dump()
