"""Tree-of-Thought Planner with self-critique and adaptive replanning.

This planner goes beyond simple linear task decomposition. It:
1. Generates multiple candidate plans (branches)
2. Evaluates each branch for feasibility and risk
3. Selects the best plan
4. Supports mid-execution replanning when reflection suggests it
"""

from __future__ import annotations

import json
import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig


class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepType(str, Enum):
    """Types of actions a step can represent."""

    TOOL_CALL = "tool_call"
    LLM_REASONING = "llm_reasoning"
    DELEGATION = "delegation"  # Delegate to another agent
    HUMAN_APPROVAL = "human_approval"
    CONDITIONAL = "conditional"
    PARALLEL_GROUP = "parallel_group"


class PlanStep(BaseModel):
    """A single step in an execution plan."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    step_type: StepType = StepType.TOOL_CALL
    tool_name: str | None = None
    tool_args: dict[str, Any] = Field(default_factory=dict)
    delegate_to_role: str | None = None  # For delegation steps
    depends_on: list[str] = Field(default_factory=list)  # Step IDs
    status: StepStatus = StepStatus.PENDING
    output: str | None = None
    error: str | None = None
    risk_score: float = 0.0  # 0-1, higher = riskier
    estimated_cost_usd: float = 0.0
    estimated_duration_seconds: float = 0.0
    conditions: dict[str, Any] = Field(default_factory=dict)  # For conditional steps
    parallel_steps: list[PlanStep] = Field(default_factory=list)  # For parallel groups
    retry_count: int = 0
    max_retries: int = 2

    @property
    def is_terminal(self) -> bool:
        return self.status in (StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED)

    @property
    def can_retry(self) -> bool:
        return self.status == StepStatus.FAILED and self.retry_count < self.max_retries


class Plan(BaseModel):
    """A complete execution plan with tree-of-thought evaluation."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    steps: list[PlanStep] = Field(default_factory=list)
    confidence_score: float = 0.0  # 0-1, planner's confidence
    total_estimated_cost_usd: float = 0.0
    total_estimated_duration_seconds: float = 0.0
    rationale: str = ""
    alternative_approaches: list[str] = Field(default_factory=list)
    revision_number: int = 0

    @property
    def is_complete(self) -> bool:
        """Plan is complete when all steps are terminal."""
        return all(step.is_terminal for step in self.steps) if self.steps else False

    @property
    def progress(self) -> float:
        """Fraction of steps completed (0-1)."""
        if not self.steps:
            return 0.0
        terminal = sum(1 for s in self.steps if s.is_terminal)
        return terminal / len(self.steps)

    def get_next_step(self) -> PlanStep | None:
        """Get the next step that is ready to execute.

        A step is ready when:
        1. It's still pending
        2. All its dependencies are completed
        """
        completed_ids = {s.id for s in self.steps if s.status == StepStatus.COMPLETED}

        for step in self.steps:
            if step.status == StepStatus.PENDING:
                deps_met = all(dep_id in completed_ids for dep_id in step.depends_on)
                if deps_met:
                    return step
            elif step.can_retry:
                return step

        return None

    def get_parallel_ready_steps(self) -> list[PlanStep]:
        """Get all steps that can be executed in parallel right now."""
        completed_ids = {s.id for s in self.steps if s.status == StepStatus.COMPLETED}
        ready = []

        for step in self.steps:
            if step.status == StepStatus.PENDING:
                deps_met = all(dep_id in completed_ids for dep_id in step.depends_on)
                if deps_met:
                    ready.append(step)

        return ready


class PlanCandidate(BaseModel):
    """A candidate plan generated during tree-of-thought exploration."""

    plan: Plan
    evaluation_score: float = 0.0
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    risk_assessment: str = ""


class Planner:
    """Tree-of-Thought planner that generates, evaluates, and selects plans.

    The planning process:
    1. Generate N candidate plans for the goal
    2. Evaluate each candidate on feasibility, risk, cost, and alignment
    3. Select the best candidate
    4. Support replanning when execution doesn't go as expected
    """

    def __init__(self, config: SovereignConfig, llm_router: Any = None) -> None:
        self.config = config
        self.llm_router = llm_router
        self._num_candidates = 3  # Generate 3 candidate plans

    async def create_plan(
        self,
        goal: str,
        constraints: list[str] | None = None,
        context: dict[str, Any] | None = None,
        agent_role: str = "general",
    ) -> Plan:
        """Create an execution plan using tree-of-thought exploration.

        Generates multiple candidate plans, evaluates them, and returns the best one.
        """
        constraints = constraints or []
        context = context or {}

        # Generate candidate plans
        candidates = await self._generate_candidates(goal, constraints, context, agent_role)

        # Evaluate each candidate
        evaluated = await self._evaluate_candidates(candidates, goal, constraints)

        # Select the best plan
        best = self._select_best(evaluated)
        return best.plan

    async def replan(
        self,
        original_plan: Plan,
        reflection: Any,  # Reflection from reasoning engine
        goal: str,
        context: dict[str, Any] | None = None,
    ) -> Plan:
        """Create a revised plan based on reflection from execution.

        Preserves completed steps and replans remaining work.
        """
        context = context or {}

        # Keep completed steps
        completed_steps = [s for s in original_plan.steps if s.status == StepStatus.COMPLETED]

        # Build context for replanning
        replan_context = {
            **context,
            "completed_steps": [s.model_dump() for s in completed_steps],
            "reflection": reflection.model_dump() if hasattr(reflection, "model_dump") else str(reflection),
            "original_rationale": original_plan.rationale,
            "revision_number": original_plan.revision_number + 1,
        }

        # Generate new plan for remaining work
        remaining_goal = self._refine_goal(goal, completed_steps, reflection)
        new_steps = await self._generate_steps(remaining_goal, replan_context)

        return Plan(
            goal=goal,
            steps=completed_steps + new_steps,
            rationale=f"Revised plan (v{original_plan.revision_number + 1}): "
            f"Adjusted based on reflection - {getattr(reflection, 'reasoning', 'unknown')}",
            revision_number=original_plan.revision_number + 1,
        )

    async def _generate_candidates(
        self,
        goal: str,
        constraints: list[str],
        context: dict[str, Any],
        agent_role: str,
    ) -> list[PlanCandidate]:
        """Generate multiple candidate plans using different strategies."""
        candidates: list[PlanCandidate] = []

        strategies = [
            self._strategy_direct,
            self._strategy_decompose,
            self._strategy_delegate,
        ]

        for strategy in strategies[: self._num_candidates]:
            steps = await strategy(goal, constraints, context, agent_role)
            plan = Plan(
                goal=goal,
                steps=steps,
                rationale=f"Generated via {strategy.__name__}",
            )
            plan.total_estimated_cost_usd = sum(s.estimated_cost_usd for s in steps)
            plan.total_estimated_duration_seconds = sum(
                s.estimated_duration_seconds for s in steps
            )
            candidates.append(PlanCandidate(plan=plan))

        return candidates

    async def _strategy_direct(
        self,
        goal: str,
        constraints: list[str],
        context: dict[str, Any],
        agent_role: str,
    ) -> list[PlanStep]:
        """Direct execution strategy - minimal steps, straightforward approach."""
        return await self._generate_steps(goal, {**context, "strategy": "direct"})

    async def _strategy_decompose(
        self,
        goal: str,
        constraints: list[str],
        context: dict[str, Any],
        agent_role: str,
    ) -> list[PlanStep]:
        """Decomposition strategy - break into sub-goals first."""
        return await self._generate_steps(goal, {**context, "strategy": "decompose"})

    async def _strategy_delegate(
        self,
        goal: str,
        constraints: list[str],
        context: dict[str, Any],
        agent_role: str,
    ) -> list[PlanStep]:
        """Delegation strategy - identify parts that can be delegated."""
        return await self._generate_steps(goal, {**context, "strategy": "delegate"})

    async def _generate_steps(
        self,
        goal: str,
        context: dict[str, Any],
    ) -> list[PlanStep]:
        """Generate plan steps using the LLM.

        Calls the LLM to decompose the goal into actionable steps with tool calls.
        Falls back to a basic plan if no LLM is available.
        """
        strategy = context.get("strategy", "direct")

        # If we have an LLM router, use it for real planning
        if self.llm_router:
            try:
                return await self._generate_steps_with_llm(goal, context, strategy)
            except Exception:
                pass  # Fall back to basic plan on LLM failure

        return self._generate_basic_steps(goal)

    async def _generate_steps_with_llm(
        self,
        goal: str,
        context: dict[str, Any],
        strategy: str,
    ) -> list[PlanStep]:
        """Generate steps by calling the LLM."""
        from sovereign.llm.provider import Message, MessageRole

        system_prompt = (
            "You are a planning engine for an autonomous AI agent called Sovereign. "
            "Given a goal, produce a JSON array of execution steps. "
            "Each step is an object with these fields:\n"
            '  "description": string - what to do\n'
            '  "step_type": "tool_call" or "llm_reasoning"\n'
            '  "tool_name": string or null - one of: web_search, browser, shell, '
            "code_executor, file_read, file_write, file_list, api_request, "
            "database_query, email_send (only if step_type is tool_call)\n"
            '  "tool_args": object - arguments for the tool (only if step_type is tool_call)\n'
            '  "risk_score": number 0.0-1.0\n'
            '  "estimated_duration_seconds": number\n\n'
            f"Strategy to use: {strategy}\n"
            "Respond ONLY with a valid JSON array. No markdown, no explanation."
        )

        user_content = f"GOAL: {goal}"
        if context.get("completed_steps"):
            user_content += "\n\nAlready completed:\n"
            for step in context["completed_steps"]:
                user_content += f"  - {step.get('description', 'unknown')}\n"
        if context.get("reflection"):
            user_content += f"\nReflection: {context['reflection']}"

        messages = [
            Message(role=MessageRole.SYSTEM, content=system_prompt),
            Message(role=MessageRole.USER, content=user_content),
        ]

        response = await self.llm_router.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )

        return self._parse_llm_plan(response.content, goal)

    def _parse_llm_plan(self, content: str, goal: str) -> list[PlanStep]:
        """Parse LLM JSON response into PlanStep objects."""
        try:
            text = content.strip()
            # Handle markdown code blocks
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
            if text.startswith("json"):
                text = text[4:].strip()

            raw_steps = json.loads(text)
            if not isinstance(raw_steps, list):
                if isinstance(raw_steps, dict) and "steps" in raw_steps:
                    raw_steps = raw_steps["steps"]
                else:
                    return self._generate_basic_steps(goal)

            steps: list[PlanStep] = []
            for raw in raw_steps:
                step_type_str = raw.get("step_type", "llm_reasoning")
                try:
                    step_type = StepType(step_type_str)
                except ValueError:
                    step_type = StepType.LLM_REASONING

                step = PlanStep(
                    description=raw.get("description", "Execute step"),
                    step_type=step_type,
                    tool_name=raw.get("tool_name"),
                    tool_args=raw.get("tool_args", {}),
                    risk_score=min(max(float(raw.get("risk_score", 0.2)), 0.0), 1.0),
                    estimated_duration_seconds=float(
                        raw.get("estimated_duration_seconds", 60)
                    ),
                )
                steps.append(step)

            if not steps:
                return self._generate_basic_steps(goal)

            # Set up sequential dependencies
            for i in range(1, len(steps)):
                steps[i].depends_on = [steps[i - 1].id]

            return steps

        except (json.JSONDecodeError, KeyError, TypeError):
            return self._generate_basic_steps(goal)

    def _generate_basic_steps(self, goal: str) -> list[PlanStep]:
        """Generate a basic fallback plan without LLM."""
        steps = [
            PlanStep(
                description=f"Analyze and understand the goal: {goal}",
                step_type=StepType.LLM_REASONING,
                risk_score=0.1,
                estimated_duration_seconds=30,
            ),
            PlanStep(
                description=f"Execute primary action for: {goal}",
                step_type=StepType.LLM_REASONING,
                risk_score=0.3,
                estimated_duration_seconds=120,
            ),
            PlanStep(
                description="Verify and validate results",
                step_type=StepType.LLM_REASONING,
                risk_score=0.1,
                estimated_duration_seconds=30,
            ),
        ]

        for i in range(1, len(steps)):
            steps[i].depends_on = [steps[i - 1].id]

        return steps

    def _build_planning_prompt(
        self, goal: str, context: dict[str, Any], strategy: str
    ) -> str:
        """Build the LLM prompt for plan generation."""
        prompt_parts = [
            "You are a planning agent. Create a detailed execution plan for this goal:",
            f"\nGOAL: {goal}",
            f"\nSTRATEGY: {strategy}",
            "\nFor each step, specify:",
            "- description: What to do",
            "- step_type: tool_call | llm_reasoning | delegation | human_approval",
            "- tool_name: Which tool to use (if tool_call)",
            "- tool_args: Arguments for the tool",
            "- risk_score: 0.0-1.0",
            "- depends_on: Which previous steps must complete first",
        ]

        if context.get("completed_steps"):
            prompt_parts.append("\nAlready completed steps:")
            for step in context["completed_steps"]:
                prompt_parts.append(f"  - {step.get('description', 'unknown')}")

        if context.get("reflection"):
            prompt_parts.append(f"\nReflection from previous attempt: {context['reflection']}")

        return "\n".join(prompt_parts)

    async def _evaluate_candidates(
        self,
        candidates: list[PlanCandidate],
        goal: str,
        constraints: list[str],
    ) -> list[PlanCandidate]:
        """Evaluate candidate plans on multiple criteria."""
        for candidate in candidates:
            score = 0.0

            # Feasibility: Does the plan cover all aspects of the goal?
            step_count = len(candidate.plan.steps)
            if 2 <= step_count <= 15:
                score += 0.3
            elif step_count > 0:
                score += 0.1

            # Risk: Lower average risk is better
            if candidate.plan.steps:
                avg_risk = sum(s.risk_score for s in candidate.plan.steps) / step_count
                score += 0.3 * (1.0 - avg_risk)

            # Cost efficiency
            if candidate.plan.total_estimated_cost_usd < 10.0:
                score += 0.2
            elif candidate.plan.total_estimated_cost_usd < 50.0:
                score += 0.1

            # Has parallel execution opportunities
            parallel_groups = sum(
                1 for s in candidate.plan.steps if s.step_type == StepType.PARALLEL_GROUP
            )
            if parallel_groups > 0:
                score += 0.1

            # Includes verification steps
            verify_steps = sum(
                1
                for s in candidate.plan.steps
                if "verify" in s.description.lower() or "validate" in s.description.lower()
            )
            if verify_steps > 0:
                score += 0.1

            candidate.evaluation_score = min(score, 1.0)
            candidate.plan.confidence_score = candidate.evaluation_score

        return candidates

    def _select_best(self, candidates: list[PlanCandidate]) -> PlanCandidate:
        """Select the highest-scoring candidate plan."""
        return max(candidates, key=lambda c: c.evaluation_score)

    def _refine_goal(
        self,
        original_goal: str,
        completed_steps: list[PlanStep],
        reflection: Any,
    ) -> str:
        """Refine the goal based on what's been completed and reflection."""
        completed_desc = ", ".join(s.description for s in completed_steps)
        suggestion = getattr(reflection, "suggestion", "continue with adjusted approach")
        return (
            f"Continue working on: {original_goal}\n"
            f"Already completed: {completed_desc}\n"
            f"Adjustment: {suggestion}"
        )
