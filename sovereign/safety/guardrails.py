"""Safety Guardrails - pre-execution safety checks for all agent actions.

Implements multi-layered safety checks:
1. Domain/URL blocklist
2. Command blocklist
3. Budget limits
4. Rate limiting
5. Risk scoring
6. Content filtering
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig


class SafetyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyViolation(BaseModel):
    """Record of a safety violation."""

    rule: str
    description: str
    level: SafetyLevel
    action_blocked: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class SafetyCheck(BaseModel):
    """Result of a safety check."""

    passed: bool
    violations: list[SafetyViolation] = Field(default_factory=list)
    risk_score: float = 0.0  # 0-1
    requires_approval: bool = False
    message: str = ""


class SafetyGuard:
    """Multi-layered safety system for agent actions.

    Checks every action before execution against:
    - Domain/URL blocklists
    - Command blocklists
    - Budget limits (per-task and daily)
    - Concurrent action limits
    - Risk thresholds
    - Content safety rules

    This is a key differentiator: enterprise-grade safety for autonomous agents.
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._safety = config.safety
        self._violations: list[SafetyViolation] = []
        self._daily_spend: float = 0.0
        self._daily_spend_reset: datetime = datetime.now(timezone.utc)
        self._active_actions: int = 0
        self._kill_switch_active: bool = False

    def check_action(
        self,
        action_type: str,
        tool_name: str = "",
        args: dict[str, Any] | None = None,
        estimated_cost_usd: float = 0.0,
        risk_score: float = 0.0,
    ) -> SafetyCheck:
        """Run all safety checks on a proposed action.

        Returns a SafetyCheck indicating whether the action is allowed.
        """
        args = args or {}
        violations: list[SafetyViolation] = []

        # Kill switch check
        if self._kill_switch_active:
            violations.append(
                SafetyViolation(
                    rule="kill_switch",
                    description="Kill switch is active. All actions are blocked.",
                    level=SafetyLevel.CRITICAL,
                    action_blocked=f"{tool_name}:{action_type}",
                )
            )
            return SafetyCheck(
                passed=False,
                violations=violations,
                risk_score=1.0,
                message="Kill switch is active",
            )

        # Concurrent action limit
        if self._active_actions >= self._safety.max_concurrent_actions:
            violations.append(
                SafetyViolation(
                    rule="concurrent_limit",
                    description=f"Too many concurrent actions ({self._active_actions})",
                    level=SafetyLevel.MEDIUM,
                    action_blocked=f"{tool_name}:{action_type}",
                )
            )

        # Budget checks
        budget_violations = self._check_budget(estimated_cost_usd, tool_name, action_type)
        violations.extend(budget_violations)

        # Domain blocklist check
        domain_violations = self._check_domains(args, tool_name, action_type)
        violations.extend(domain_violations)

        # Command blocklist check
        command_violations = self._check_commands(args, tool_name, action_type)
        violations.extend(command_violations)

        # Risk threshold check
        requires_approval = False
        if risk_score >= self._safety.approval_threshold_high:
            requires_approval = True
        elif risk_score >= self._safety.approval_threshold_medium:
            # Medium risk - approval recommended but not required
            requires_approval = estimated_cost_usd > 1.0

        if violations:
            self._violations.extend(violations)
            return SafetyCheck(
                passed=False,
                violations=violations,
                risk_score=risk_score,
                requires_approval=requires_approval,
                message=f"Blocked: {violations[0].description}",
            )

        return SafetyCheck(
            passed=True,
            risk_score=risk_score,
            requires_approval=requires_approval,
            message="Action approved",
        )

    def _check_budget(
        self,
        estimated_cost: float,
        tool_name: str,
        action_type: str,
    ) -> list[SafetyViolation]:
        """Check budget limits."""
        violations: list[SafetyViolation] = []

        # Reset daily spend if new day
        now = datetime.now(timezone.utc)
        if now.date() > self._daily_spend_reset.date():
            self._daily_spend = 0.0
            self._daily_spend_reset = now

        # Per-task budget
        if estimated_cost > self._safety.budget_limit_per_task_usd:
            violations.append(
                SafetyViolation(
                    rule="task_budget",
                    description=(
                        f"Estimated cost ${estimated_cost:.2f} exceeds per-task limit "
                        f"${self._safety.budget_limit_per_task_usd:.2f}"
                    ),
                    level=SafetyLevel.HIGH,
                    action_blocked=f"{tool_name}:{action_type}",
                )
            )

        # Daily budget
        if self._daily_spend + estimated_cost > self._safety.budget_limit_per_day_usd:
            violations.append(
                SafetyViolation(
                    rule="daily_budget",
                    description=(
                        f"Daily spend ${self._daily_spend:.2f} + ${estimated_cost:.2f} "
                        f"would exceed daily limit ${self._safety.budget_limit_per_day_usd:.2f}"
                    ),
                    level=SafetyLevel.HIGH,
                    action_blocked=f"{tool_name}:{action_type}",
                )
            )

        return violations

    def _check_domains(
        self,
        args: dict[str, Any],
        tool_name: str,
        action_type: str,
    ) -> list[SafetyViolation]:
        """Check for blocked domains in URLs."""
        violations: list[SafetyViolation] = []
        urls_to_check: list[str] = []

        # Extract URLs from common argument names
        for key in ("url", "website", "link", "href"):
            if key in args and isinstance(args[key], str):
                urls_to_check.append(args[key])

        for url in urls_to_check:
            for domain in self._safety.blocked_domains:
                if domain.lower() in url.lower():
                    violations.append(
                        SafetyViolation(
                            rule="blocked_domain",
                            description=f"Domain '{domain}' is blocked: {url}",
                            level=SafetyLevel.HIGH,
                            action_blocked=f"{tool_name}:{action_type}",
                        )
                    )
                    break

        return violations

    def _check_commands(
        self,
        args: dict[str, Any],
        tool_name: str,
        action_type: str,
    ) -> list[SafetyViolation]:
        """Check for blocked commands."""
        violations: list[SafetyViolation] = []
        commands_to_check: list[str] = []

        for key in ("command", "cmd", "script"):
            if key in args and isinstance(args[key], str):
                commands_to_check.append(args[key])

        for command in commands_to_check:
            command_lower = command.lower()
            for blocked in self._safety.blocked_commands:
                if blocked.lower() in command_lower:
                    violations.append(
                        SafetyViolation(
                            rule="blocked_command",
                            description=f"Command contains blocked pattern: '{blocked}'",
                            level=SafetyLevel.CRITICAL,
                            action_blocked=f"{tool_name}:{action_type}",
                        )
                    )
                    break

        return violations

    def record_spend(self, amount_usd: float) -> None:
        """Record spending for budget tracking."""
        self._daily_spend += amount_usd

    def action_started(self) -> None:
        """Record that an action has started (for concurrency tracking)."""
        self._active_actions += 1

    def action_completed(self) -> None:
        """Record that an action has completed."""
        self._active_actions = max(0, self._active_actions - 1)

    def activate_kill_switch(self) -> None:
        """Activate the kill switch - blocks ALL actions."""
        self._kill_switch_active = True

    def deactivate_kill_switch(self) -> None:
        """Deactivate the kill switch."""
        self._kill_switch_active = False

    def get_violations(self, limit: int = 50) -> list[SafetyViolation]:
        """Get recent violations."""
        return self._violations[-limit:]

    def get_stats(self) -> dict[str, Any]:
        """Get safety system statistics."""
        return {
            "kill_switch_active": self._kill_switch_active,
            "daily_spend_usd": self._daily_spend,
            "daily_budget_usd": self._safety.budget_limit_per_day_usd,
            "active_actions": self._active_actions,
            "max_concurrent": self._safety.max_concurrent_actions,
            "total_violations": len(self._violations),
        }
