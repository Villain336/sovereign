"""CRM Tool - Customer Relationship Management pipeline.

Manages the full sales pipeline:
- Lead tracking (new → contacted → qualified → proposal → closed)
- Outreach sequences (automated follow-ups)
- Deal management
- Customer data persistence
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sovereign.tools.base import Tool, ToolParameter, ToolResult


def _get_crm_path() -> Path:
    """Get the CRM data storage path."""
    crm_dir = Path.home() / ".sovereign" / "crm"
    crm_dir.mkdir(parents=True, exist_ok=True)
    return crm_dir


def _load_leads() -> list[dict[str, Any]]:
    """Load leads from disk."""
    path = _get_crm_path() / "leads.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def _save_leads(leads: list[dict[str, Any]]) -> None:
    """Save leads to disk."""
    path = _get_crm_path() / "leads.json"
    path.write_text(json.dumps(leads, indent=2, default=str), encoding="utf-8")


def _load_deals() -> list[dict[str, Any]]:
    """Load deals from disk."""
    path = _get_crm_path() / "deals.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def _save_deals(deals: list[dict[str, Any]]) -> None:
    """Save deals to disk."""
    path = _get_crm_path() / "deals.json"
    path.write_text(json.dumps(deals, indent=2, default=str), encoding="utf-8")


class CRMAddLeadTool(Tool):
    """Add a new lead to the CRM pipeline."""

    name = "crm_add_lead"
    description = (
        "Add a new lead to the sales pipeline. Tracks company name, contact info, "
        "source, and pipeline stage. Use this after finding leads to start tracking them."
    )
    parameters = [
        ToolParameter(
            name="company",
            description="Company/business name",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="contact_name",
            description="Primary contact person name",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="email",
            description="Contact email",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="phone",
            description="Contact phone",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="website",
            description="Company website URL",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="source",
            description="Where this lead came from (e.g., web_scrape, referral, inbound)",
            param_type="string",
            required=False,
            default="manual",
        ),
        ToolParameter(
            name="notes",
            description="Additional notes about this lead",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="deal_value",
            description="Estimated deal value in USD",
            param_type="number",
            required=False,
        ),
    ]
    category = "business"
    risk_level = 0.1

    async def execute(self, **kwargs: Any) -> ToolResult:
        company = kwargs.get("company", "")
        if not company:
            return ToolResult(success=False, error="Company name is required")

        lead = {
            "id": str(uuid.uuid4()),
            "company": company,
            "contact_name": kwargs.get("contact_name", ""),
            "email": kwargs.get("email", ""),
            "phone": kwargs.get("phone", ""),
            "website": kwargs.get("website", ""),
            "source": kwargs.get("source", "manual"),
            "notes": kwargs.get("notes", ""),
            "deal_value": kwargs.get("deal_value", 0),
            "stage": "new",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "interactions": [],
            "score": 0,
            "tags": [],
        }

        leads = _load_leads()
        leads.append(lead)
        _save_leads(leads)

        return ToolResult(
            success=True,
            output=f"Lead added: {company} (ID: {lead['id'][:8]})",
            metadata={"lead_id": lead["id"], "company": company, "stage": "new"},
        )


class CRMUpdateStageTool(Tool):
    """Move a lead through the sales pipeline."""

    name = "crm_update_stage"
    description = (
        "Update a lead's pipeline stage. Stages: new → contacted → qualified → "
        "proposal → negotiation → closed_won / closed_lost. Use this to track "
        "progress through the sales funnel."
    )
    parameters = [
        ToolParameter(
            name="lead_id",
            description="Lead ID (or partial ID match)",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="stage",
            description="New pipeline stage",
            param_type="string",
            required=True,
            enum=[
                "new", "contacted", "qualified", "proposal",
                "negotiation", "closed_won", "closed_lost",
            ],
        ),
        ToolParameter(
            name="notes",
            description="Notes about this stage change",
            param_type="string",
            required=False,
        ),
    ]
    category = "business"
    risk_level = 0.1

    async def execute(self, **kwargs: Any) -> ToolResult:
        lead_id = kwargs.get("lead_id", "")
        stage = kwargs.get("stage", "")
        notes = kwargs.get("notes", "")

        if not lead_id or not stage:
            return ToolResult(success=False, error="lead_id and stage are required")

        leads = _load_leads()
        found = None
        for lead in leads:
            if lead["id"].startswith(lead_id) or lead["id"] == lead_id:
                found = lead
                break

        if not found:
            return ToolResult(success=False, error=f"Lead not found: {lead_id}")

        old_stage = found["stage"]
        found["stage"] = stage
        found["updated_at"] = datetime.now(timezone.utc).isoformat()
        found["interactions"].append({
            "type": "stage_change",
            "from": old_stage,
            "to": stage,
            "notes": notes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Create a deal if moved to closed_won
        if stage == "closed_won" and found.get("deal_value", 0) > 0:
            deals = _load_deals()
            deals.append({
                "id": str(uuid.uuid4()),
                "lead_id": found["id"],
                "company": found["company"],
                "value": found["deal_value"],
                "closed_at": datetime.now(timezone.utc).isoformat(),
                "status": "won",
            })
            _save_deals(deals)

        _save_leads(leads)

        return ToolResult(
            success=True,
            output=f"Lead {found['company']} moved: {old_stage} → {stage}",
            metadata={
                "lead_id": found["id"],
                "company": found["company"],
                "old_stage": old_stage,
                "new_stage": stage,
            },
        )


class CRMListLeadsTool(Tool):
    """List and filter leads in the CRM."""

    name = "crm_list_leads"
    description = (
        "List all leads in the CRM pipeline, optionally filtered by stage. "
        "Shows company name, contact, stage, and deal value. Use this to "
        "review your pipeline and decide on next actions."
    )
    parameters = [
        ToolParameter(
            name="stage",
            description="Filter by pipeline stage (optional)",
            param_type="string",
            required=False,
            enum=[
                "new", "contacted", "qualified", "proposal",
                "negotiation", "closed_won", "closed_lost", "all",
            ],
        ),
        ToolParameter(
            name="sort_by",
            description="Sort field: created_at, deal_value, score",
            param_type="string",
            required=False,
            default="created_at",
        ),
    ]
    category = "business"
    risk_level = 0.0

    async def execute(self, **kwargs: Any) -> ToolResult:
        stage_filter = kwargs.get("stage", "all")
        sort_by = kwargs.get("sort_by", "created_at")

        leads = _load_leads()

        if stage_filter and stage_filter != "all":
            leads = [lead for lead in leads if lead["stage"] == stage_filter]

        # Sort
        if sort_by == "deal_value":
            leads.sort(key=lambda x: x.get("deal_value", 0), reverse=True)
        elif sort_by == "score":
            leads.sort(key=lambda x: x.get("score", 0), reverse=True)
        else:
            leads.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        if not leads:
            return ToolResult(
                success=True,
                output="No leads found.",
                metadata={"lead_count": 0},
            )

        # Format output
        lines: list[str] = [f"=== CRM Pipeline ({len(leads)} leads) ===\n"]

        # Pipeline summary
        stages = {}
        all_leads = _load_leads()
        for ld in all_leads:
            s = ld["stage"]
            stages[s] = stages.get(s, 0) + 1

        pipeline_str = " → ".join(
            f"{s}: {stages.get(s, 0)}"
            for s in ["new", "contacted", "qualified", "proposal",
                       "negotiation", "closed_won", "closed_lost"]
            if stages.get(s, 0) > 0
        )
        lines.append(f"Pipeline: {pipeline_str}\n")

        for lead in leads:
            value = f"${lead.get('deal_value', 0):,.0f}" if lead.get("deal_value") else "N/A"
            lines.append(
                f"[{lead['stage'].upper()}] {lead['company']}\n"
                f"  Contact: {lead.get('contact_name', 'N/A')} | "
                f"Email: {lead.get('email', 'N/A')} | "
                f"Value: {value}\n"
                f"  ID: {lead['id'][:8]}\n"
            )

        total_pipeline_value = sum(
            ld.get("deal_value", 0) for ld in all_leads
            if ld["stage"] not in ("closed_won", "closed_lost")
        )
        total_won = sum(
            ld.get("deal_value", 0) for ld in all_leads
            if ld["stage"] == "closed_won"
        )
        lines.append(f"\nPipeline Value: ${total_pipeline_value:,.0f}")
        lines.append(f"Total Won: ${total_won:,.0f}")

        return ToolResult(
            success=True,
            output="\n".join(lines),
            metadata={
                "lead_count": len(leads),
                "total_pipeline_value": total_pipeline_value,
                "total_won": total_won,
                "stages": stages,
            },
        )


class CRMLogInteractionTool(Tool):
    """Log an interaction with a lead."""

    name = "crm_log_interaction"
    description = (
        "Log a sales interaction (email, call, meeting, demo) with a lead. "
        "Use this after every touchpoint to maintain a complete history."
    )
    parameters = [
        ToolParameter(
            name="lead_id",
            description="Lead ID (or partial ID match)",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="interaction_type",
            description="Type of interaction",
            param_type="string",
            required=True,
            enum=["email", "call", "sms", "meeting", "demo", "proposal", "follow_up", "note"],
        ),
        ToolParameter(
            name="summary",
            description="Summary of what happened",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="outcome",
            description="Outcome: positive, neutral, negative",
            param_type="string",
            required=False,
            default="neutral",
        ),
        ToolParameter(
            name="next_action",
            description="What to do next",
            param_type="string",
            required=False,
        ),
    ]
    category = "business"
    risk_level = 0.1

    async def execute(self, **kwargs: Any) -> ToolResult:
        lead_id = kwargs.get("lead_id", "")
        interaction_type = kwargs.get("interaction_type", "")
        summary = kwargs.get("summary", "")

        if not lead_id or not interaction_type or not summary:
            return ToolResult(
                success=False,
                error="lead_id, interaction_type, and summary are required",
            )

        leads = _load_leads()
        found = None
        for lead in leads:
            if lead["id"].startswith(lead_id) or lead["id"] == lead_id:
                found = lead
                break

        if not found:
            return ToolResult(success=False, error=f"Lead not found: {lead_id}")

        interaction = {
            "id": str(uuid.uuid4()),
            "type": interaction_type,
            "summary": summary,
            "outcome": kwargs.get("outcome", "neutral"),
            "next_action": kwargs.get("next_action", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        found["interactions"].append(interaction)
        found["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Update lead score based on interaction outcome
        outcome = kwargs.get("outcome", "neutral")
        if outcome == "positive":
            found["score"] = min(found.get("score", 0) + 2, 10)
        elif outcome == "negative":
            found["score"] = max(found.get("score", 0) - 1, 0)

        _save_leads(leads)

        return ToolResult(
            success=True,
            output=(
                f"Interaction logged for {found['company']}: "
                f"{interaction_type} - {summary[:80]}"
            ),
            metadata={
                "lead_id": found["id"],
                "company": found["company"],
                "interaction_type": interaction_type,
                "total_interactions": len(found["interactions"]),
            },
        )
