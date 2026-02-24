"""Reasoning Engine with self-reflection, critique, and meta-cognition.

This engine provides the agent's ability to:
1. Reflect on execution progress and outcomes
2. Self-critique plans and results
3. Decide when to replan, continue, or abort
4. Extract lessons learned for future improvement
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig
from sovereign.core.planner import Plan


class Reflection(BaseModel):
    """Result of the reasoning engine's reflection on progress."""

    reasoning: str
    goal_progress: float = 0.0  # 0-1, how close to achieving the goal
    should_replan: bool = False
    should_abort: bool = False
    suggestion: str = ""
    confidence: float = 0.5
    issues_identified: list[str] = Field(default_factory=list)
    lessons_learned: list[str] = Field(default_factory=list)
    risk_assessment: str = ""


class Critique(BaseModel):
    """Self-critique of a plan or action."""

    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    overall_score: float = 0.5  # 0-1
    improvement_suggestions: list[str] = Field(default_factory=list)
    missing_considerations: list[str] = Field(default_factory=list)


class LessonLearned(BaseModel):
    """A lesson extracted from task execution for future improvement."""

    context: str
    lesson: str
    applicable_to: list[str] = Field(default_factory=list)  # Tags for when to apply
    confidence: float = 0.5


class ReasoningEngine:
    """Engine for agent self-reflection, critique, and meta-cognition.

    The reasoning engine is what differentiates Sovereign from simpler agents.
    It provides genuine self-awareness of progress, quality, and strategy.
    """

    def __init__(self, config: SovereignConfig, llm_router: Any = None) -> None:
        self.config = config
        self.llm_router = llm_router
        self._lessons: list[LessonLearned] = []

    async def reflect(
        self,
        goal: str,
        plan: Plan,
        last_result: Any,
        history: list[Any],
    ) -> Reflection:
        """Reflect on current progress after executing a step.

        Analyzes:
        - Whether the last action moved us closer to the goal
        - Whether the plan is still viable
        - Whether we should replan, continue, or abort
        - What lessons can be extracted
        """
        # Calculate goal progress
        progress = plan.progress

        # Analyze the last result
        last_success = getattr(last_result, "success", False)
        last_error = getattr(last_result, "error", None)
        last_output = getattr(last_result, "output", "")

        # Count consecutive failures
        recent_failures = 0
        for result in reversed(history):
            if not getattr(result, "success", False):
                recent_failures += 1
            else:
                break

        # Determine if we should replan
        should_replan = False
        should_abort = False
        issues: list[str] = []
        suggestion = ""

        if recent_failures >= 3:
            should_abort = True
            issues.append("Three consecutive failures detected")
            suggestion = "Consider a fundamentally different approach"
        elif recent_failures >= 2:
            should_replan = True
            issues.append("Two consecutive failures - approach may be flawed")
            suggestion = "Replan with alternative strategy"
        elif not last_success and last_error:
            # Single failure - check if retryable
            if self._is_retryable_error(last_error):
                suggestion = f"Retry with adjustment: {self._suggest_fix(last_error)}"
            else:
                should_replan = True
                issues.append(f"Non-retryable error: {last_error}")
                suggestion = "Replan to work around this blocker"

        # Check if we're making progress
        if progress > 0 and progress < 0.3 and len(history) > 5:
            issues.append("Slow progress relative to steps taken")
            if not should_replan:
                should_replan = True
                suggestion = "Consider more efficient approach"

        # Extract lessons
        lessons = self._extract_lessons(goal, last_result, last_success)

        # Build reflection - use LLM if available for deeper reasoning
        reasoning = await self._build_reasoning_with_llm(
            goal=goal,
            progress=progress,
            last_success=last_success,
            last_output=last_output,
            last_error=last_error,
            issues=issues,
            plan=plan,
        )

        return Reflection(
            reasoning=reasoning,
            goal_progress=progress,
            should_replan=should_replan,
            should_abort=should_abort,
            suggestion=suggestion,
            confidence=0.8 if last_success else 0.4,
            issues_identified=issues,
            lessons_learned=[lesson.lesson for lesson in lessons],
            risk_assessment=self._assess_risk(plan, history),
        )

    async def critique_plan(self, plan: Plan, goal: str) -> Critique:
        """Self-critique a plan before or during execution.

        Evaluates the plan for completeness, feasibility, and risk.
        """
        strengths: list[str] = []
        weaknesses: list[str] = []
        improvements: list[str] = []
        missing: list[str] = []

        # Check plan completeness
        if plan.steps:
            strengths.append(f"Plan has {len(plan.steps)} concrete steps")
        else:
            weaknesses.append("Plan has no steps")

        # Check for verification steps
        has_verify = any(
            "verify" in s.description.lower() or "validate" in s.description.lower()
            for s in plan.steps
        )
        if has_verify:
            strengths.append("Includes verification step")
        else:
            missing.append("No verification/validation step")
            improvements.append("Add a verification step to confirm results")

        # Check for error handling
        has_fallback = any(s.max_retries > 0 for s in plan.steps)
        if has_fallback:
            strengths.append("Has retry capability")
        else:
            weaknesses.append("No retry capability for any step")

        # Check risk distribution
        high_risk_steps = [s for s in plan.steps if s.risk_score > 0.7]
        if high_risk_steps:
            weaknesses.append(f"{len(high_risk_steps)} high-risk steps identified")
            improvements.append("Add safety checks before high-risk steps")

        # Check for parallelization opportunities
        no_dep_steps = [s for s in plan.steps if not s.depends_on and s != plan.steps[0]]
        if no_dep_steps:
            improvements.append(
                f"{len(no_dep_steps)} steps could potentially run in parallel"
            )

        # Calculate overall score
        score = 0.5
        score += 0.1 * min(len(strengths), 3)
        score -= 0.1 * min(len(weaknesses), 3)
        score = max(0.0, min(1.0, score))

        return Critique(
            strengths=strengths,
            weaknesses=weaknesses,
            overall_score=score,
            improvement_suggestions=improvements,
            missing_considerations=missing,
        )

    async def meta_reason(
        self,
        goal: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Higher-order reasoning about the agent's own reasoning process.

        This enables the agent to:
        - Assess its own confidence calibration
        - Identify knowledge gaps
        - Determine when to ask for help
        - Evaluate whether it's the right agent for this task
        """
        # Check relevant lessons
        relevant_lessons = self._find_relevant_lessons(goal)

        # Assess confidence
        has_experience = len(relevant_lessons) > 0
        role = context.get("agent_role", "general")

        confidence = 0.5
        if has_experience:
            confidence += 0.2
        if role != "general":
            confidence += 0.1

        knowledge_gaps: list[str] = []
        if not has_experience:
            knowledge_gaps.append("No prior experience with similar tasks")

        return {
            "confidence": confidence,
            "has_relevant_experience": has_experience,
            "relevant_lessons": [lesson.model_dump() for lesson in relevant_lessons],
            "knowledge_gaps": knowledge_gaps,
            "should_ask_for_help": confidence < 0.3,
            "recommended_approach": "delegate" if confidence < 0.3 else "execute",
        }

    def _is_retryable_error(self, error: str) -> bool:
        """Determine if an error is likely retryable."""
        retryable_patterns = [
            "timeout",
            "rate limit",
            "429",
            "503",
            "temporary",
            "connection",
            "network",
        ]
        error_lower = error.lower()
        return any(pattern in error_lower for pattern in retryable_patterns)

    def _suggest_fix(self, error: str) -> str:
        """Suggest a fix for a retryable error."""
        error_lower = error.lower()
        if "timeout" in error_lower:
            return "Increase timeout or retry with simpler request"
        if "rate limit" in error_lower or "429" in error_lower:
            return "Wait and retry with backoff"
        if "connection" in error_lower or "network" in error_lower:
            return "Check connectivity and retry"
        return "Retry with backoff"

    def _extract_lessons(
        self,
        goal: str,
        last_result: Any,
        success: bool,
    ) -> list[LessonLearned]:
        """Extract lessons from the latest execution step."""
        lessons: list[LessonLearned] = []

        if not success:
            error = getattr(last_result, "error", "unknown")
            lesson = LessonLearned(
                context=goal,
                lesson=f"Approach failed with: {error}",
                applicable_to=["error_recovery"],
                confidence=0.6,
            )
            lessons.append(lesson)
            self._lessons.append(lesson)

        return lessons

    async def _build_reasoning_with_llm(
        self,
        goal: str,
        progress: float,
        last_success: bool,
        last_output: str,
        last_error: str | None,
        issues: list[str],
        plan: Plan,
    ) -> str:
        """Build a reasoning summary, using LLM for deeper analysis if available."""
        # Build basic reasoning first
        basic = self._build_reasoning(
            goal, progress, last_success, last_output, last_error, issues
        )

        if not self.llm_router:
            return basic

        try:
            from sovereign.llm.provider import Message, MessageRole

            completed = [s.description for s in plan.steps if s.status.value == "completed"]
            pending = [s.description for s in plan.steps if s.status.value == "pending"]

            messages = [
                Message(
                    role=MessageRole.SYSTEM,
                    content=(
                        "You are the self-reflection module of an autonomous AI agent. "
                        "Analyze the current execution state and provide a brief, "
                        "insightful reflection (2-3 sentences) about progress, "
                        "what's working, and what might need adjustment."
                    ),
                ),
                Message(
                    role=MessageRole.USER,
                    content=(
                        f"Goal: {goal}\n"
                        f"Progress: {progress:.0%}\n"
                        f"Last step: {'succeeded' if last_success else 'failed'}\n"
                        f"Last output: {(last_output or last_error or 'none')[:300]}\n"
                        f"Completed steps: {completed}\n"
                        f"Remaining steps: {pending}\n"
                        f"Issues: {issues}\n"
                        "Provide your reflection:"
                    ),
                ),
            ]

            response = await self.llm_router.generate(
                messages=messages,
                temperature=0.5,
                max_tokens=256,
            )
            return response.content

        except Exception:
            return basic

    def _build_reasoning(
        self,
        goal: str,
        progress: float,
        last_success: bool,
        last_output: str,
        last_error: str | None,
        issues: list[str],
    ) -> str:
        """Build a basic natural language reasoning summary."""
        parts = [f"Goal: {goal}", f"Progress: {progress:.0%}"]

        if last_success:
            parts.append("Last step succeeded.")
            if last_output:
                parts.append(f"Output summary: {last_output[:200]}")
        else:
            parts.append(f"Last step failed: {last_error or 'unknown error'}")

        if issues:
            parts.append(f"Issues: {'; '.join(issues)}")

        return " | ".join(parts)

    def _assess_risk(self, plan: Plan, history: list[Any]) -> str:
        """Assess overall risk of continuing the plan."""
        failure_rate = sum(
            1 for r in history if not getattr(r, "success", False)
        ) / max(len(history), 1)

        remaining_risk = sum(
            s.risk_score for s in plan.steps if s.status == "pending"
        ) / max(sum(1 for s in plan.steps if s.status == "pending"), 1)

        if failure_rate > 0.5 or remaining_risk > 0.7:
            return "HIGH - Consider alternative approach"
        elif failure_rate > 0.2 or remaining_risk > 0.4:
            return "MEDIUM - Proceed with caution"
        return "LOW - On track"

    def _find_relevant_lessons(self, goal: str) -> list[LessonLearned]:
        """Find lessons from past tasks that are relevant to the current goal."""
        goal_lower = goal.lower()
        relevant = []
        for lesson in self._lessons:
            # Simple keyword overlap for now
            # In production, this would use semantic similarity
            context_words = set(lesson.context.lower().split())
            goal_words = set(goal_lower.split())
            overlap = len(context_words & goal_words)
            if overlap >= 2:
                relevant.append(lesson)
        return relevant
