"""Compliance monitoring API router."""

from typing import Optional

from fastapi import APIRouter, HTTPException

from app.compliance.nist_controls import CONTROL_FAMILIES
from app.services.state import platform_state

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


@router.get("/status")
async def get_compliance_status():
    """Get overall compliance status summary."""
    controls = platform_state.get_controls()
    total = len(controls)
    compliant = sum(1 for c in controls if c.status.value == "compliant")
    partial = sum(1 for c in controls if c.status.value == "partially_compliant")
    non_compliant = sum(1 for c in controls if c.status.value == "non_compliant")
    not_assessed = sum(1 for c in controls if c.status.value == "not_assessed")

    # Calculate by family
    families = {}
    for ctrl in controls:
        fid = ctrl.family_id
        if fid not in families:
            families[fid] = {
                "family_id": fid,
                "family": ctrl.family,
                "total": 0,
                "compliant": 0,
                "partially_compliant": 0,
                "non_compliant": 0,
                "not_assessed": 0,
            }
        families[fid]["total"] += 1
        families[fid][ctrl.status.value] += 1

    family_list = []
    for fid in sorted(families.keys()):
        f = families[fid]
        score = (f["compliant"] / f["total"] * 100) if f["total"] > 0 else 0
        f["score"] = round(score, 1)
        family_list.append(f)

    return {
        "overall_score": round(compliant / total * 100, 1) if total > 0 else 0,
        "total_controls": total,
        "compliant": compliant,
        "partially_compliant": partial,
        "non_compliant": non_compliant,
        "not_assessed": not_assessed,
        "cmmc_level": 2,
        "framework": "NIST 800-171 Rev 2",
        "families": family_list,
    }


@router.get("/controls")
async def list_controls(family_id: Optional[str] = None, status: Optional[str] = None):
    """List all 110 NIST 800-171 controls with optional filtering."""
    controls = platform_state.get_controls(family_id=family_id, status=status)
    return {"controls": [c.model_dump() for c in controls], "total": len(controls)}


@router.get("/controls/{control_id}")
async def get_control(control_id: str):
    """Get detailed information about a specific control."""
    control = platform_state.get_control(control_id)
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    return control.model_dump()


@router.get("/families")
async def list_families():
    """List all NIST 800-171 control families."""
    return {"families": [{"id": k, "name": v} for k, v in CONTROL_FAMILIES.items()]}


@router.post("/assess")
async def trigger_assessment():
    """Trigger a new compliance assessment cycle."""
    result = platform_state.run_compliance_assessment()
    return result
