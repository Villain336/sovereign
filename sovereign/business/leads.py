"""Lead Generation Pipeline - automated lead discovery, qualification, and nurturing.

Manages the full lead lifecycle from discovery to conversion,
tracking interactions and scoring leads for prioritization.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig


class LeadStatus(str, Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    MEETING_SCHEDULED = "meeting_scheduled"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATING = "negotiating"
    WON = "won"
    LOST = "lost"
    NURTURING = "nurturing"


class LeadSource(str, Enum):
    WEB_SEARCH = "web_search"
    SOCIAL_MEDIA = "social_media"
    REFERRAL = "referral"
    INBOUND = "inbound"
    COLD_OUTREACH = "cold_outreach"
    CONTENT = "content"
    EVENT = "event"
    MANUAL = "manual"


class LeadInteraction(BaseModel):
    """Record of an interaction with a lead."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    interaction_type: str  # email, call, meeting, social, etc.
    direction: str = "outbound"  # inbound, outbound
    content_summary: str = ""
    outcome: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class Lead(BaseModel):
    """A potential customer or business contact."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    company: str = ""
    email: str = ""
    phone: str = ""
    title: str = ""
    website: str = ""
    source: LeadSource = LeadSource.MANUAL
    status: LeadStatus = LeadStatus.NEW
    score: float = 0.0  # 0-100 lead score
    tags: list[str] = Field(default_factory=list)
    notes: str = ""
    interactions: list[LeadInteraction] = Field(default_factory=list)
    estimated_value_usd: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class LeadScoringCriteria(BaseModel):
    """Criteria for scoring leads."""

    has_email: float = 10.0
    has_company: float = 10.0
    has_website: float = 5.0
    has_title: float = 5.0
    interaction_count_weight: float = 5.0
    response_bonus: float = 20.0
    meeting_bonus: float = 30.0
    recency_weight: float = 10.0


class LeadPipeline:
    """Manages the lead generation and nurturing pipeline.

    Features:
    - Lead discovery from multiple sources
    - Automatic lead scoring and qualification
    - Interaction tracking and follow-up scheduling
    - Pipeline analytics and conversion tracking
    - CRM-like functionality built for autonomous agents
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._leads: dict[str, Lead] = {}
        self._scoring = LeadScoringCriteria()
        self._store_path = Path(config.data_dir) / "leads.json"
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if self._store_path.exists():
            try:
                data = json.loads(self._store_path.read_text())
                self._leads = {lid: Lead(**ldata) for lid, ldata in data.items()}
            except (json.JSONDecodeError, Exception):
                self._leads = {}

    def _save(self) -> None:
        data = {lid: lead.model_dump(mode="json") for lid, lead in self._leads.items()}
        self._store_path.write_text(json.dumps(data, indent=2, default=str))

    def add_lead(self, lead: Lead) -> Lead:
        """Add a new lead to the pipeline."""
        lead.score = self._calculate_score(lead)
        self._leads[lead.id] = lead
        self._save()
        return lead

    def update_lead(self, lead_id: str, **updates: Any) -> Lead | None:
        """Update lead properties."""
        lead = self._leads.get(lead_id)
        if not lead:
            return None

        for key, value in updates.items():
            if hasattr(lead, key):
                setattr(lead, key, value)

        lead.updated_at = datetime.now(timezone.utc)
        lead.score = self._calculate_score(lead)
        self._save()
        return lead

    def add_interaction(
        self,
        lead_id: str,
        interaction_type: str,
        content_summary: str,
        outcome: str = "",
        direction: str = "outbound",
    ) -> LeadInteraction | None:
        """Record an interaction with a lead."""
        lead = self._leads.get(lead_id)
        if not lead:
            return None

        interaction = LeadInteraction(
            interaction_type=interaction_type,
            direction=direction,
            content_summary=content_summary,
            outcome=outcome,
        )
        lead.interactions.append(interaction)
        lead.updated_at = datetime.now(timezone.utc)

        # Auto-advance status based on interaction
        if direction == "inbound" and lead.status == LeadStatus.CONTACTED:
            lead.status = LeadStatus.RESPONDED

        lead.score = self._calculate_score(lead)
        self._save()
        return interaction

    def get_leads_by_status(self, status: LeadStatus) -> list[Lead]:
        """Get all leads with a specific status."""
        return [lead for lead in self._leads.values() if lead.status == status]

    def get_hot_leads(self, min_score: float = 50.0) -> list[Lead]:
        """Get high-scoring leads ready for action."""
        hot = [lead for lead in self._leads.values() if lead.score >= min_score]
        return sorted(hot, key=lambda x: x.score, reverse=True)

    def get_follow_up_needed(self, days_since_contact: int = 3) -> list[Lead]:
        """Get leads that need follow-up."""
        now = datetime.now(timezone.utc)
        needs_followup: list[Lead] = []

        for lead in self._leads.values():
            if lead.status in (LeadStatus.WON, LeadStatus.LOST):
                continue

            if lead.interactions:
                last = lead.interactions[-1]
                days_elapsed = (now - last.timestamp).days
                if days_elapsed >= days_since_contact:
                    needs_followup.append(lead)
            elif (now - lead.created_at).days >= 1:
                needs_followup.append(lead)

        return sorted(needs_followup, key=lambda x: x.score, reverse=True)

    def get_pipeline_stats(self) -> dict[str, Any]:
        """Get pipeline analytics."""
        total = len(self._leads)
        by_status: dict[str, int] = {}
        total_value = 0.0

        for lead in self._leads.values():
            by_status[lead.status.value] = by_status.get(lead.status.value, 0) + 1
            total_value += lead.estimated_value_usd

        won = by_status.get("won", 0)
        lost = by_status.get("lost", 0)
        conversion_rate = won / max(won + lost, 1)

        return {
            "total_leads": total,
            "by_status": by_status,
            "total_pipeline_value_usd": total_value,
            "conversion_rate": conversion_rate,
            "average_score": sum(lead.score for lead in self._leads.values()) / max(total, 1),
        }

    def _calculate_score(self, lead: Lead) -> float:
        """Calculate lead score based on multiple signals."""
        score = 0.0

        if lead.email:
            score += self._scoring.has_email
        if lead.company:
            score += self._scoring.has_company
        if lead.website:
            score += self._scoring.has_website
        if lead.title:
            score += self._scoring.has_title

        # Interaction-based scoring
        score += min(len(lead.interactions) * self._scoring.interaction_count_weight, 25)

        # Response bonus
        has_response = any(
            i.direction == "inbound" for i in lead.interactions
        )
        if has_response:
            score += self._scoring.response_bonus

        # Meeting bonus
        has_meeting = any(
            "meeting" in i.interaction_type.lower() for i in lead.interactions
        )
        if has_meeting:
            score += self._scoring.meeting_bonus

        # Recency bonus
        if lead.interactions:
            last_interaction = lead.interactions[-1]
            days_since = (datetime.now(timezone.utc) - last_interaction.timestamp).days
            if days_since < 7:
                score += self._scoring.recency_weight

        return min(score, 100.0)

    @property
    def total_leads(self) -> int:
        return len(self._leads)
