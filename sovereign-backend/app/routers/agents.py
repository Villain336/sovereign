"""Agent management API router."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.base import AgentStatus
from app.services.state import platform_state

router = APIRouter(prefix="/api/agents", tags=["agents"])


class AgentActionRequest(BaseModel):
    action: str  # start, stop


@router.get("")
async def list_agents():
    """List all agents and their current status."""
    agents = platform_state.get_agents()
    return {
        "agents": [a.model_dump() for a in agents],
        "total": len(agents),
        "running": sum(1 for a in agents if a.status == AgentStatus.RUNNING),
    }


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get detailed information about a specific agent."""
    agent = platform_state.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.model_dump()


@router.post("/{agent_id}/action")
async def agent_action(agent_id: str, request: AgentActionRequest):
    """Start or stop an agent."""
    if request.action == "start":
        new_status = AgentStatus.RUNNING
    elif request.action == "stop":
        new_status = AgentStatus.STOPPED
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")

    agent = platform_state.update_agent_status(agent_id, new_status)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "ok", "agent_id": agent_id, "new_status": agent.status.value}
