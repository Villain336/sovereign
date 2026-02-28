"""Dashboard API router."""

from fastapi import APIRouter

from app.services.state import platform_state

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_dashboard_summary():
    """Get real-time dashboard summary with threat posture and compliance status."""
    return platform_state.get_dashboard_summary()
