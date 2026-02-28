"""Audit trail API router."""

from fastapi import APIRouter

from app.services.state import platform_state

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/trail")
async def get_audit_trail(limit: int = 50, offset: int = 0):
    """Get the cryptographic audit trail with pagination."""
    entries = platform_state.get_audit_trail(limit=limit, offset=offset)
    return {
        "entries": [e.model_dump() for e in entries],
        "total": len(platform_state.audit_trail),
        "limit": limit,
        "offset": offset,
    }


@router.get("/integrity")
async def verify_audit_integrity():
    """Verify the integrity of the entire audit trail chain."""
    from app.core.security import verify_chain_hash
    import json

    entries = platform_state.audit_trail
    if not entries:
        return {"verified": True, "entries_checked": 0, "message": "Empty audit trail"}

    broken_links = []
    for i, entry in enumerate(entries):
        expected_previous = entries[i - 1].hash if i > 0 else "GENESIS"
        if entry.previous_hash != expected_previous:
            broken_links.append({
                "index": i,
                "entry_id": entry.id,
                "expected_previous": expected_previous,
                "actual_previous": entry.previous_hash,
            })

    verified = len(broken_links) == 0
    return {
        "verified": verified,
        "entries_checked": len(entries),
        "broken_links": broken_links,
        "message": "Audit trail integrity verified" if verified else f"Found {len(broken_links)} broken chain links",
    }
