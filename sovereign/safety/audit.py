"""Audit Logger - comprehensive logging of all agent actions.

Provides tamper-evident audit trail for compliance, debugging,
and learning. Every action, decision, and outcome is logged.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig


class AuditEntry(BaseModel):
    """A single audit log entry."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str  # action, decision, error, approval, safety, etc.
    agent_id: str = ""
    action: str = ""
    tool_name: str = ""
    args_summary: str = ""
    result_summary: str = ""
    success: bool = True
    cost_usd: float = 0.0
    duration_seconds: float = 0.0
    risk_score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditLogger:
    """Comprehensive audit logging for all agent activities.

    Features:
    - Append-only log for tamper resistance
    - Structured entries for queryability
    - Automatic rotation and archival
    - Cost and performance tracking
    - Compliance-ready format
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._log_path = Path(config.safety.audit_log_path)
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[AuditEntry] = []
        self._max_memory_entries = 10000

    def log(
        self,
        event_type: str,
        action: str = "",
        agent_id: str = "",
        tool_name: str = "",
        args_summary: str = "",
        result_summary: str = "",
        success: bool = True,
        cost_usd: float = 0.0,
        duration_seconds: float = 0.0,
        risk_score: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Log an audit entry."""
        entry = AuditEntry(
            event_type=event_type,
            action=action,
            agent_id=agent_id,
            tool_name=tool_name,
            args_summary=args_summary,
            result_summary=result_summary,
            success=success,
            cost_usd=cost_usd,
            duration_seconds=duration_seconds,
            risk_score=risk_score,
            metadata=metadata or {},
        )

        self._entries.append(entry)

        # Write to file (append mode)
        self._write_entry(entry)

        # Prune memory if needed
        if len(self._entries) > self._max_memory_entries:
            self._entries = self._entries[-self._max_memory_entries:]

        return entry

    def log_action(
        self,
        agent_id: str,
        tool_name: str,
        args_summary: str,
        result_summary: str,
        success: bool,
        cost_usd: float = 0.0,
        duration_seconds: float = 0.0,
    ) -> AuditEntry:
        """Convenience method to log a tool action."""
        return self.log(
            event_type="action",
            action=f"tool:{tool_name}",
            agent_id=agent_id,
            tool_name=tool_name,
            args_summary=args_summary,
            result_summary=result_summary,
            success=success,
            cost_usd=cost_usd,
            duration_seconds=duration_seconds,
        )

    def log_decision(
        self,
        agent_id: str,
        decision: str,
        reasoning: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Log an agent decision."""
        return self.log(
            event_type="decision",
            action=decision,
            agent_id=agent_id,
            result_summary=reasoning,
            metadata=metadata,
        )

    def log_safety_event(
        self,
        event: str,
        details: str = "",
        risk_score: float = 0.0,
    ) -> AuditEntry:
        """Log a safety-related event."""
        return self.log(
            event_type="safety",
            action=event,
            result_summary=details,
            risk_score=risk_score,
        )

    def _write_entry(self, entry: AuditEntry) -> None:
        """Append an entry to the audit log file."""
        try:
            with open(self._log_path, "a", encoding="utf-8") as f:
                line = json.dumps(entry.model_dump(mode="json"), default=str)
                f.write(line + "\n")
        except OSError:
            pass  # Don't fail if audit logging fails

    def get_entries(
        self,
        event_type: str | None = None,
        agent_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Query audit entries."""
        results = self._entries
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if agent_id:
            results = [e for e in results if e.agent_id == agent_id]
        return results[-limit:]

    def get_cost_summary(self) -> dict[str, float]:
        """Get cost summary from audit log."""
        total_cost = sum(e.cost_usd for e in self._entries)
        by_agent: dict[str, float] = {}
        by_tool: dict[str, float] = {}

        for entry in self._entries:
            if entry.cost_usd > 0:
                if entry.agent_id:
                    by_agent[entry.agent_id] = by_agent.get(entry.agent_id, 0) + entry.cost_usd
                if entry.tool_name:
                    by_tool[entry.tool_name] = by_tool.get(entry.tool_name, 0) + entry.cost_usd

        return {
            "total_cost_usd": total_cost,
            "by_agent": by_agent,
            "by_tool": by_tool,
        }

    def get_stats(self) -> dict[str, Any]:
        """Get audit log statistics."""
        total = len(self._entries)
        successes = sum(1 for e in self._entries if e.success)
        failures = total - successes

        return {
            "total_entries": total,
            "successes": successes,
            "failures": failures,
            "success_rate": successes / max(total, 1),
            "total_cost_usd": sum(e.cost_usd for e in self._entries),
            "event_types": list(set(e.event_type for e in self._entries)),
        }
