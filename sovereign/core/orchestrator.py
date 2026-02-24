"""Multi-Agent Orchestrator - the Director that coordinates specialized agents.

This is Sovereign's key differentiator over OpenClaw and Manus:
- Hierarchical task decomposition and delegation
- Specialized agent routing based on capabilities
- Parallel agent execution with result aggregation
- Inter-agent communication and collaboration
- Dynamic agent spawning based on workload
"""

from __future__ import annotations

import asyncio
import uuid

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig
from sovereign.core.agent import (
    Agent,
    AgentMessage,
    AgentRole,
    TaskContext,
)
from sovereign.core.executor import ActionResult


class TaskDecomposition(BaseModel):
    """A goal decomposed into sub-tasks for different agents."""

    original_goal: str
    sub_tasks: list[SubTask] = Field(default_factory=list)
    dependencies: dict[str, list[str]] = Field(default_factory=dict)  # task_id -> [dep_task_ids]
    aggregation_strategy: str = "sequential"  # sequential, parallel, map_reduce


class SubTask(BaseModel):
    """A sub-task assigned to a specific agent."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    assigned_role: AgentRole
    assigned_agent_id: str | None = None
    priority: int = 5
    estimated_complexity: float = 0.5
    requires_output_from: list[str] = Field(default_factory=list)
    status: str = "pending"
    result: ActionResult | None = None


class OrchestratorState(BaseModel):
    """Current state of the orchestrator."""

    active_tasks: int = 0
    agents_busy: int = 0
    agents_idle: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    budget_spent_usd: float = 0.0


class Orchestrator:
    """Multi-agent orchestrator that decomposes goals and coordinates agents.

    The Orchestrator acts as the Director agent. When given a high-level goal:
    1. Decomposes it into sub-tasks
    2. Routes each sub-task to the best specialized agent
    3. Manages inter-agent communication
    4. Aggregates results
    5. Handles failures with reassignment or escalation
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._agents: dict[str, Agent] = {}
        self._role_agents: dict[AgentRole, list[str]] = {}
        self._active_tasks: dict[str, TaskDecomposition] = {}
        self._message_bus: asyncio.Queue[AgentMessage] = asyncio.Queue()
        self._state = OrchestratorState()

    def register_agent(self, agent: Agent) -> None:
        """Register an agent with the orchestrator."""
        self._agents[agent.id] = agent
        if agent.role not in self._role_agents:
            self._role_agents[agent.role] = []
        self._role_agents[agent.role].append(agent.id)

    def unregister_agent(self, agent_id: str) -> None:
        """Remove an agent from the orchestrator."""
        agent = self._agents.pop(agent_id, None)
        if agent and agent.role in self._role_agents:
            self._role_agents[agent.role] = [
                aid for aid in self._role_agents[agent.role] if aid != agent_id
            ]

    async def execute_goal(
        self,
        goal: str,
        constraints: list[str] | None = None,
        budget_usd: float | None = None,
        priority: int = 5,
    ) -> ActionResult:
        """Execute a high-level goal by decomposing and delegating to agents.

        This is the main entry point for the orchestrator.
        """
        constraints = constraints or []

        # Step 1: Decompose the goal into sub-tasks
        decomposition = await self._decompose_goal(goal, constraints)
        task_id = str(uuid.uuid4())
        self._active_tasks[task_id] = decomposition
        self._state.active_tasks += 1

        try:
            # Step 2: Execute based on aggregation strategy
            if decomposition.aggregation_strategy == "parallel":
                results = await self._execute_parallel(decomposition, budget_usd)
            elif decomposition.aggregation_strategy == "map_reduce":
                results = await self._execute_map_reduce(decomposition, budget_usd)
            else:
                results = await self._execute_sequential(decomposition, budget_usd)

            # Step 3: Aggregate results
            final_result = self._aggregate_results(results, goal)

            self._state.total_tasks_completed += 1
            return final_result

        except Exception as e:
            self._state.total_tasks_failed += 1
            return ActionResult(
                success=False,
                output="",
                error=f"Orchestration failed: {str(e)}",
                action_type="orchestration_error",
            )
        finally:
            self._state.active_tasks -= 1
            self._active_tasks.pop(task_id, None)

    async def _decompose_goal(
        self,
        goal: str,
        constraints: list[str],
    ) -> TaskDecomposition:
        """Decompose a high-level goal into sub-tasks for different agents.

        Uses the LLM to analyze the goal and determine:
        1. What sub-tasks are needed
        2. Which agent role should handle each
        3. What dependencies exist between sub-tasks
        4. Whether tasks can run in parallel
        """
        # Analyze the goal to determine required capabilities
        required_roles = self._identify_required_roles(goal)

        # Create sub-tasks based on analysis
        sub_tasks: list[SubTask] = []
        dependencies: dict[str, list[str]] = {}

        # Research phase (if needed)
        if AgentRole.RESEARCHER in required_roles:
            research_task = SubTask(
                description=f"Research and gather information for: {goal}",
                assigned_role=AgentRole.RESEARCHER,
                priority=3,
                estimated_complexity=0.4,
            )
            sub_tasks.append(research_task)

        # Analysis phase (if needed)
        if AgentRole.ANALYST in required_roles:
            analysis_task = SubTask(
                description=f"Analyze data and generate insights for: {goal}",
                assigned_role=AgentRole.ANALYST,
                priority=4,
                estimated_complexity=0.5,
            )
            # Analysis depends on research
            if sub_tasks:
                analysis_task.requires_output_from = [sub_tasks[0].id]
                dependencies[analysis_task.id] = [sub_tasks[0].id]
            sub_tasks.append(analysis_task)

        # Implementation phase (if needed)
        if AgentRole.CODER in required_roles:
            code_task = SubTask(
                description=f"Implement technical solution for: {goal}",
                assigned_role=AgentRole.CODER,
                priority=5,
                estimated_complexity=0.7,
            )
            if sub_tasks:
                code_task.requires_output_from = [sub_tasks[-1].id]
                dependencies[code_task.id] = [sub_tasks[-1].id]
            sub_tasks.append(code_task)

        # Content/marketing phase (if needed)
        if AgentRole.MARKETER in required_roles:
            marketing_task = SubTask(
                description=f"Create content and marketing materials for: {goal}",
                assigned_role=AgentRole.MARKETER,
                priority=5,
                estimated_complexity=0.5,
            )
            sub_tasks.append(marketing_task)

        # Outreach phase (if needed)
        if AgentRole.OUTREACH in required_roles:
            outreach_task = SubTask(
                description=f"Execute outreach and communication for: {goal}",
                assigned_role=AgentRole.OUTREACH,
                priority=6,
                estimated_complexity=0.4,
            )
            if sub_tasks:
                outreach_task.requires_output_from = [sub_tasks[-1].id]
                dependencies[outreach_task.id] = [sub_tasks[-1].id]
            sub_tasks.append(outreach_task)

        # Deployment/ops phase (if needed)
        if AgentRole.OPERATOR in required_roles:
            ops_task = SubTask(
                description=f"Deploy and operationalize: {goal}",
                assigned_role=AgentRole.OPERATOR,
                priority=7,
                estimated_complexity=0.6,
            )
            if sub_tasks:
                ops_task.requires_output_from = [sub_tasks[-1].id]
                dependencies[ops_task.id] = [sub_tasks[-1].id]
            sub_tasks.append(ops_task)

        # If no specific roles identified, create a general task
        if not sub_tasks:
            sub_tasks.append(
                SubTask(
                    description=goal,
                    assigned_role=AgentRole.GENERAL,
                    priority=5,
                    estimated_complexity=0.5,
                )
            )

        # Determine aggregation strategy
        has_dependencies = bool(dependencies)
        strategy = "sequential" if has_dependencies else "parallel"

        return TaskDecomposition(
            original_goal=goal,
            sub_tasks=sub_tasks,
            dependencies=dependencies,
            aggregation_strategy=strategy,
        )

    async def _execute_sequential(
        self,
        decomposition: TaskDecomposition,
        budget_usd: float | None,
    ) -> list[ActionResult]:
        """Execute sub-tasks sequentially, passing outputs between them."""
        results: list[ActionResult] = []
        accumulated_context: dict[str, str] = {}

        for sub_task in decomposition.sub_tasks:
            agent = await self._assign_agent(sub_task)
            if not agent:
                results.append(
                    ActionResult(
                        success=False,
                        error=f"No agent available for role: {sub_task.assigned_role}",
                        action_type="assignment_error",
                    )
                )
                continue

            # Build task context with outputs from dependencies
            task = TaskContext(
                goal=sub_task.description,
                priority=sub_task.priority,
                budget_usd=budget_usd,
                metadata={"accumulated_context": accumulated_context},
            )

            result = await agent.run_task(task)
            sub_task.result = result
            sub_task.status = "completed" if result.success else "failed"
            results.append(result)

            if result.success and result.output:
                accumulated_context[sub_task.id] = result.output

            # If a task fails, try reassignment
            if not result.success:
                reassigned_result = await self._try_reassignment(sub_task, task)
                if reassigned_result:
                    results[-1] = reassigned_result
                    if reassigned_result.success and reassigned_result.output:
                        accumulated_context[sub_task.id] = reassigned_result.output

            agent.reset()

        return results

    async def _execute_parallel(
        self,
        decomposition: TaskDecomposition,
        budget_usd: float | None,
    ) -> list[ActionResult]:
        """Execute independent sub-tasks in parallel."""
        tasks = []
        for sub_task in decomposition.sub_tasks:
            agent = await self._assign_agent(sub_task)
            if agent:
                task = TaskContext(
                    goal=sub_task.description,
                    priority=sub_task.priority,
                    budget_usd=budget_usd,
                )
                tasks.append(agent.run_task(task))
            else:
                tasks.append(self._make_error_result(sub_task))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results: list[ActionResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    ActionResult(
                        success=False,
                        error=str(result),
                        action_type="parallel_error",
                    )
                )
            else:
                processed_results.append(result)
                decomposition.sub_tasks[i].result = result
                decomposition.sub_tasks[i].status = (
                    "completed" if result.success else "failed"
                )

        # Reset agents
        for sub_task in decomposition.sub_tasks:
            if sub_task.assigned_agent_id:
                agent = self._agents.get(sub_task.assigned_agent_id)
                if agent:
                    agent.reset()

        return processed_results

    async def _execute_map_reduce(
        self,
        decomposition: TaskDecomposition,
        budget_usd: float | None,
    ) -> list[ActionResult]:
        """Execute in map-reduce pattern: parallel map, then sequential reduce."""
        # Map phase: execute all tasks in parallel
        map_results = await self._execute_parallel(decomposition, budget_usd)

        # Reduce phase: synthesize results
        successful_outputs = [r.output for r in map_results if r.success and r.output]
        reduce_result = ActionResult(
            success=len(successful_outputs) > 0,
            output="\n\n---\n\n".join(successful_outputs),
            action_type="map_reduce_aggregate",
            metadata={"total_mapped": len(map_results), "successful": len(successful_outputs)},
        )

        return map_results + [reduce_result]

    async def _assign_agent(self, sub_task: SubTask) -> Agent | None:
        """Find and assign the best available agent for a sub-task."""
        role = sub_task.assigned_role
        agent_ids = self._role_agents.get(role, [])

        # Try to find an idle agent with the right role
        for agent_id in agent_ids:
            agent = self._agents.get(agent_id)
            if agent and not agent.is_busy:
                sub_task.assigned_agent_id = agent.id
                return agent

        # Try general agents as fallback
        general_ids = self._role_agents.get(AgentRole.GENERAL, [])
        for agent_id in general_ids:
            agent = self._agents.get(agent_id)
            if agent and not agent.is_busy:
                sub_task.assigned_agent_id = agent.id
                return agent

        return None

    async def _try_reassignment(
        self,
        sub_task: SubTask,
        task: TaskContext,
    ) -> ActionResult | None:
        """Try to reassign a failed task to a different agent."""
        original_agent_id = sub_task.assigned_agent_id
        role = sub_task.assigned_role

        # Find a different agent
        agent_ids = self._role_agents.get(role, [])
        for agent_id in agent_ids:
            if agent_id != original_agent_id:
                agent = self._agents.get(agent_id)
                if agent and not agent.is_busy:
                    sub_task.assigned_agent_id = agent.id
                    result = await agent.run_task(task)
                    agent.reset()
                    return result

        return None

    async def _make_error_result(self, sub_task: SubTask) -> ActionResult:
        """Create an error result for tasks that couldn't be assigned."""
        return ActionResult(
            success=False,
            error=f"No agent available for role: {sub_task.assigned_role}",
            action_type="assignment_error",
        )

    def _aggregate_results(
        self,
        results: list[ActionResult],
        goal: str,
    ) -> ActionResult:
        """Aggregate results from all sub-tasks into a final result."""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        all_outputs = [r.output for r in successful if r.output]
        all_errors = [r.error for r in failed if r.error]

        overall_success = len(successful) > len(failed)

        return ActionResult(
            success=overall_success,
            output="\n\n".join(all_outputs) if all_outputs else "No outputs produced",
            error="; ".join(all_errors) if all_errors else None,
            action_type="orchestration_complete",
            metadata={
                "goal": goal,
                "total_sub_tasks": len(results),
                "successful": len(successful),
                "failed": len(failed),
            },
        )

    def _identify_required_roles(self, goal: str) -> list[AgentRole]:
        """Identify which agent roles are needed based on the goal.

        Uses keyword analysis to determine required specializations.
        In production, this would use LLM-based analysis.
        """
        goal_lower = goal.lower()
        roles: list[AgentRole] = []

        research_keywords = ["research", "find", "search", "discover", "investigate", "analyze market"]
        code_keywords = ["build", "code", "develop", "implement", "fix", "debug", "deploy", "create app", "website"]
        marketing_keywords = ["marketing", "content", "blog", "social media", "seo", "brand", "advertise"]
        analyst_keywords = ["analyze", "data", "report", "metrics", "insights", "dashboard", "financial"]
        outreach_keywords = ["outreach", "email campaign", "leads", "sales", "prospect", "cold email"]
        ops_keywords = ["deploy", "server", "infrastructure", "monitor", "devops", "ci/cd"]

        if any(kw in goal_lower for kw in research_keywords):
            roles.append(AgentRole.RESEARCHER)
        if any(kw in goal_lower for kw in code_keywords):
            roles.append(AgentRole.CODER)
        if any(kw in goal_lower for kw in marketing_keywords):
            roles.append(AgentRole.MARKETER)
        if any(kw in goal_lower for kw in analyst_keywords):
            roles.append(AgentRole.ANALYST)
        if any(kw in goal_lower for kw in outreach_keywords):
            roles.append(AgentRole.OUTREACH)
        if any(kw in goal_lower for kw in ops_keywords):
            roles.append(AgentRole.OPERATOR)

        return roles if roles else [AgentRole.GENERAL]

    def get_state(self) -> OrchestratorState:
        """Get current orchestrator state."""
        self._state.agents_busy = sum(
            1 for a in self._agents.values() if a.is_busy
        )
        self._state.agents_idle = sum(
            1 for a in self._agents.values() if not a.is_busy
        )
        return self._state

    async def broadcast_message(
        self,
        content: str,
        message_type: str = "info",
    ) -> None:
        """Broadcast a message to all registered agents."""
        for agent in self._agents.values():
            message = AgentMessage(
                sender="orchestrator",
                recipient=agent.id,
                content=content,
                message_type=message_type,
            )
            await agent.receive_message(message)
