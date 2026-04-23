"""Approval Workflow - human-in-the-loop for high-risk actions.

Provides a structured approval system for actions that exceed
risk thresholds or budget limits. Supports multiple approval channels.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    AUTO_APPROVED = "auto_approved"


class ApprovalRequest(BaseModel):
    """A request for human approval."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    description: str
    risk_score: float = 0.0
    estimated_cost_usd: float = 0.0
    tool_name: str = ""
    args_summary: str = ""
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decided_at: datetime | None = None
    decided_by: str = ""
    reason: str = ""
    timeout_seconds: int = 3600  # 1 hour default
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApprovalWorkflow:
    """Manages human-in-the-loop approval workflows.

    When an action exceeds risk/cost thresholds, it's queued for approval.
    The workflow supports:
    - Queuing approval requests
    - Multiple notification channels (Slack, Discord, email)
    - Auto-approval rules for low-risk patterns
    - Timeout handling
    - Audit trail
    """

    def __init__(self) -> None:
        self._pending: dict[str, ApprovalRequest] = {}
        self._history: list[ApprovalRequest] = []
        self._auto_approve_patterns: list[str] = []
        self._approval_events: dict[str, asyncio.Event] = {}

    async def request_approval(
        self,
        action_type: str,
        description: str,
        risk_score: float = 0.0,
        estimated_cost_usd: float = 0.0,
        tool_name: str = "",
        args_summary: str = "",
        timeout_seconds: int = 3600,
    ) -> ApprovalRequest:
        """Submit an action for approval and wait for a decision."""
        # Check auto-approval patterns
        for pattern in self._auto_approve_patterns:
            if pattern.lower() in description.lower():
                request = ApprovalRequest(
                    action_type=action_type,
                    description=description,
                    risk_score=risk_score,
                    estimated_cost_usd=estimated_cost_usd,
                    tool_name=tool_name,
                    args_summary=args_summary,
                    status=ApprovalStatus.AUTO_APPROVED,
                    decided_at=datetime.now(timezone.utc),
                    decided_by="auto_approve_rule",
                    timeout_seconds=timeout_seconds,
                )
                self._history.append(request)
                return request

        request = ApprovalRequest(
            action_type=action_type,
            description=description,
            risk_score=risk_score,
            estimated_cost_usd=estimated_cost_usd,
            tool_name=tool_name,
            args_summary=args_summary,
            timeout_seconds=timeout_seconds,
        )

        self._pending[request.id] = request
        self._approval_events[request.id] = asyncio.Event()

        # Wait for approval or timeout
        try:
            await asyncio.wait_for(
                self._approval_events[request.id].wait(),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            request.status = ApprovalStatus.EXPIRED
            request.decided_at = datetime.now(timezone.utc)

        # Clean up
        self._pending.pop(request.id, None)
        self._approval_events.pop(request.id, None)
        self._history.append(request)

        return request

    def approve(self, request_id: str, by: str = "human", reason: str = "") -> bool:
        """Approve a pending request."""
        request = self._pending.get(request_id)
        if not request:
            return False

        request.status = ApprovalStatus.APPROVED
        request.decided_at = datetime.now(timezone.utc)
        request.decided_by = by
        request.reason = reason

        event = self._approval_events.get(request_id)
        if event:
            event.set()

        return True

    def deny(self, request_id: str, by: str = "human", reason: str = "") -> bool:
        """Deny a pending request."""
        request = self._pending.get(request_id)
        if not request:
            return False

        request.status = ApprovalStatus.DENIED
        request.decided_at = datetime.now(timezone.utc)
        request.decided_by = by
        request.reason = reason

        event = self._approval_events.get(request_id)
        if event:
            event.set()

        return True

    def add_auto_approve_pattern(self, pattern: str) -> None:
        """Add a pattern for automatic approval."""
        self._auto_approve_patterns.append(pattern)

    def get_pending(self) -> list[ApprovalRequest]:
        """Get all pending approval requests."""
        return list(self._pending.values())

    def get_history(self, limit: int = 50) -> list[ApprovalRequest]:
        """Get approval history."""
        return self._history[-limit:]

    def get_stats(self) -> dict[str, Any]:
        """Get approval workflow statistics."""
        total = len(self._history)
        approved = sum(
            1
            for r in self._history
            if r.status in (ApprovalStatus.APPROVED, ApprovalStatus.AUTO_APPROVED)
        )
        denied = sum(1 for r in self._history if r.status == ApprovalStatus.DENIED)
        expired = sum(1 for r in self._history if r.status == ApprovalStatus.EXPIRED)

        return {
            "pending": len(self._pending),
            "total_processed": total,
            "approved": approved,
            "denied": denied,
            "expired": expired,
            "approval_rate": approved / max(total, 1),
        }
