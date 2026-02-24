"""Multi-Agent Orchestrator - the Director that coordinates specialized agents.

This is Sovereign's key differentiator over OpenClaw and Manus:
- LLM-powered goal decomposition into sub-tasks
- Specialized agent routing based on capabilities
- Parallel agent execution with result aggregation
- Inter-agent communication via shared memory and message bus
- Dynamic agent spawning based on workload
- Real delegation: sub-agents actually plan, reason, and execute
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig
from sovereign.core.agent import (
    Agent,
    AgentMessage,
    AgentRole,
    TaskContext,
)
from sovereign.core.executor import ActionResult


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


class TaskDecomposition(BaseModel):
    """A goal decomposed into sub-tasks for different agents."""

    original_goal: str
    sub_tasks: list[SubTask] = Field(default_factory=list)
    dependencies: dict[str, list[str]] = Field(default_factory=dict)
    aggregation_strategy: str = "sequential"  # sequential, parallel, map_reduce
    rationale: str = ""


class SharedMemoryEntry(BaseModel):
    """A single entry in shared memory."""

    value: str
    author: str
    tags: list[str] = Field(default_factory=list)
    timestamp: str = ""


class SharedMemory(BaseModel):
    """Shared memory space for inter-agent collaboration.

    Agents can read/write to this shared context so that outputs
    from one agent are available to others without explicit passing.
    """

    entries: dict[str, SharedMemoryEntry] = Field(default_factory=dict)

    def write(
        self,
        key: str,
        value: str,
        author: str,
        tags: list[str] | None = None,
    ) -> None:
        """Write a value to shared memory."""
        self.entries[key] = SharedMemoryEntry(
            value=value,
            author=author,
            tags=tags or [],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def read(self, key: str) -> str | None:
        """Read a value from shared memory."""
        entry = self.entries.get(key)
        return entry.value if entry else None

    def search(self, tag: str) -> list[tuple[str, str]]:
        """Search entries by tag. Returns list of (key, value) tuples."""
        results = []
        for key, entry in self.entries.items():
            if tag in entry.tags:
                results.append((key, entry.value))
        return results

    def get_context_summary(self, max_entries: int = 10) -> str:
        """Get a summary of recent shared memory for agent context."""
        sorted_entries = sorted(
            self.entries.items(),
            key=lambda x: x[1].timestamp,
            reverse=True,
        )[:max_entries]
        if not sorted_entries:
            return "No shared context available."
        lines = []
        for key, entry in sorted_entries:
            preview = entry.value[:200]
            lines.append(f"[{entry.author}] {key}: {preview}")
        return "\n".join(lines)


class OrchestratorState(BaseModel):
    """Current state of the orchestrator."""

    active_tasks: int = 0
    agents_busy: int = 0
    agents_idle: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    budget_spent_usd: float = 0.0
    messages_exchanged: int = 0


class Orchestrator:
    """Multi-agent orchestrator that decomposes goals and coordinates agents.

    The Orchestrator acts as the Director agent. When given a high-level goal:
    1. Uses LLM to decompose it into sub-tasks with rationale
    2. Routes each sub-task to the best specialized agent
    3. Manages inter-agent communication via shared memory
    4. Aggregates results with LLM-powered synthesis
    5. Handles failures with reassignment or escalation
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._agents: dict[str, Agent] = {}
        self._role_agents: dict[AgentRole, list[str]] = {}
        self._active_tasks: dict[str, TaskDecomposition] = {}
        self._message_bus: asyncio.Queue[AgentMessage] = asyncio.Queue()
        self._message_log: list[AgentMessage] = []
        self._state = OrchestratorState()
        self._shared_memory = SharedMemory()
        self._stream_callback: Any = None
        self._llm_router: Any = None

    def set_llm_router(self, router: Any) -> None:
        """Set the LLM router for intelligent decomposition."""
        self._llm_router = router

    def set_stream_callback(self, callback: Any) -> None:
        """Set callback for streaming orchestrator output."""
        self._stream_callback = callback

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

    @property
    def shared_memory(self) -> SharedMemory:
        """Access shared memory for inter-agent communication."""
        return self._shared_memory

    async def execute_goal(
        self,
        goal: str,
        constraints: list[str] | None = None,
        budget_usd: float | None = None,
        priority: int = 5,
    ) -> ActionResult:
        """Execute a high-level goal by decomposing and delegating to agents."""
        constraints = constraints or []

        await self._emit(f"\n[ORCHESTRATOR] Received goal: {goal}")
        await self._emit(f"[ORCHESTRATOR] {len(self._agents)} agents registered")

        # Step 1: Decompose the goal into sub-tasks using LLM
        await self._emit("[ORCHESTRATOR] Decomposing goal into sub-tasks...")
        decomposition = await self._decompose_goal(goal, constraints)
        task_id = str(uuid.uuid4())
        self._active_tasks[task_id] = decomposition
        self._state.active_tasks += 1

        await self._emit(
            f"[ORCHESTRATOR] Strategy: {decomposition.aggregation_strategy}"
        )
        if decomposition.rationale:
            await self._emit(
                f"[ORCHESTRATOR] Rationale: {decomposition.rationale[:200]}"
            )
        for i, st in enumerate(decomposition.sub_tasks, 1):
            await self._emit(
                f"  {i}. [{st.assigned_role.value}] {st.description}"
            )

        try:
            # Step 2: Execute based on aggregation strategy
            if decomposition.aggregation_strategy == "parallel":
                results = await self._execute_parallel(decomposition, budget_usd)
            elif decomposition.aggregation_strategy == "map_reduce":
                results = await self._execute_map_reduce(decomposition, budget_usd)
            else:
                results = await self._execute_sequential(decomposition, budget_usd)

            # Step 3: Aggregate results using LLM synthesis
            await self._emit("\n[ORCHESTRATOR] Synthesizing results...")
            final_result = await self._aggregate_results(results, goal)

            self._state.total_tasks_completed += 1
            await self._emit("[ORCHESTRATOR] Goal complete.")
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
        """Decompose a goal. Uses LLM if available, else keywords."""
        if self._llm_router:
            try:
                return await self._decompose_with_llm(goal, constraints)
            except Exception:
                pass
        return self._decompose_with_keywords(goal, constraints)

    async def _decompose_with_llm(
        self,
        goal: str,
        constraints: list[str],
    ) -> TaskDecomposition:
        """Use LLM to intelligently decompose a goal into sub-tasks."""
        from sovereign.llm.provider import Message, MessageRole

        available_roles = list(
            set(r.value for r in self._role_agents.keys()) | {"general"}
        )

        memory_context = self._shared_memory.get_context_summary(5)

        system_prompt = (
            "You are the Director of an autonomous AI agent team called Sovereign. "
            "Given a high-level goal, decompose it into sub-tasks for specialized agents.\n\n"
            f"Available agent roles: {', '.join(available_roles)}\n\n"
            "Respond with a JSON object:\n"
            '{\n'
            '  "rationale": "Why you chose this decomposition",\n'
            '  "strategy": "sequential" or "parallel" or "map_reduce",\n'
            '  "sub_tasks": [\n'
            '    {\n'
            '      "description": "What this agent should do",\n'
            '      "role": "one of the available roles",\n'
            '      "priority": 1-10,\n'
            '      "complexity": 0.0-1.0,\n'
            '      "depends_on": []\n'
            '    }\n'
            '  ]\n'
            '}\n\n'
            "Rules:\n"
            "- Break complex goals into 2-6 sub-tasks\n"
            "- Use the most specific role for each task\n"
            "- Use 'sequential' if tasks depend on each other\n"
            "- Use 'parallel' if all tasks are independent\n"
            "- Use 'map_reduce' if tasks produce data that needs synthesis\n"
            "Respond ONLY with valid JSON. No markdown, no explanation."
        )

        user_content = f"GOAL: {goal}"
        if constraints:
            user_content += f"\nCONSTRAINTS: {', '.join(constraints)}"
        if memory_context != "No shared context available.":
            user_content += f"\nSHARED CONTEXT:\n{memory_context}"

        messages = [
            Message(role=MessageRole.SYSTEM, content=system_prompt),
            Message(role=MessageRole.USER, content=user_content),
        ]

        response = await self._llm_router.generate(
            messages=messages,
            temperature=0.5,
            max_tokens=1024,
        )

        return self._parse_decomposition(response.content, goal)

    def _parse_decomposition(self, content: str, goal: str) -> TaskDecomposition:
        """Parse LLM response into a TaskDecomposition."""
        try:
            text = content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
            if text.startswith("json"):
                text = text[4:].strip()

            data = json.loads(text)

            strategy = data.get("strategy", "sequential")
            rationale = data.get("rationale", "")
            raw_tasks = data.get("sub_tasks", [])

            sub_tasks: list[SubTask] = []
            dependencies: dict[str, list[str]] = {}

            for raw in raw_tasks:
                role_str = raw.get("role", "general")
                try:
                    role = AgentRole(role_str)
                except ValueError:
                    role = AgentRole.GENERAL

                task = SubTask(
                    description=raw.get("description", "Execute task"),
                    assigned_role=role,
                    priority=raw.get("priority", 5),
                    estimated_complexity=raw.get("complexity", 0.5),
                )

                dep_indices = raw.get("depends_on", [])
                if dep_indices and sub_tasks:
                    dep_ids = []
                    for idx in dep_indices:
                        if isinstance(idx, int) and 0 <= idx < len(sub_tasks):
                            dep_ids.append(sub_tasks[idx].id)
                    if dep_ids:
                        task.requires_output_from = dep_ids
                        dependencies[task.id] = dep_ids

                sub_tasks.append(task)

            if not sub_tasks:
                return self._decompose_with_keywords(goal, [])

            return TaskDecomposition(
                original_goal=goal,
                sub_tasks=sub_tasks,
                dependencies=dependencies,
                aggregation_strategy=strategy,
                rationale=rationale,
            )

        except (json.JSONDecodeError, KeyError, TypeError):
            return self._decompose_with_keywords(goal, [])

    def _decompose_with_keywords(
        self,
        goal: str,
        constraints: list[str],
    ) -> TaskDecomposition:
        """Fallback: decompose using keyword analysis."""
        required_roles = self._identify_required_roles(goal)

        sub_tasks: list[SubTask] = []
        dependencies: dict[str, list[str]] = {}

        if AgentRole.RESEARCHER in required_roles:
            task = SubTask(
                description=f"Research and gather information for: {goal}",
                assigned_role=AgentRole.RESEARCHER,
                priority=3,
                estimated_complexity=0.4,
            )
            sub_tasks.append(task)

        if AgentRole.ANALYST in required_roles:
            task = SubTask(
                description=f"Analyze data and generate insights for: {goal}",
                assigned_role=AgentRole.ANALYST,
                priority=4,
                estimated_complexity=0.5,
            )
            if sub_tasks:
                task.requires_output_from = [sub_tasks[0].id]
                dependencies[task.id] = [sub_tasks[0].id]
            sub_tasks.append(task)

        if AgentRole.CODER in required_roles:
            task = SubTask(
                description=f"Implement technical solution for: {goal}",
                assigned_role=AgentRole.CODER,
                priority=5,
                estimated_complexity=0.7,
            )
            if sub_tasks:
                task.requires_output_from = [sub_tasks[-1].id]
                dependencies[task.id] = [sub_tasks[-1].id]
            sub_tasks.append(task)

        if AgentRole.MARKETER in required_roles:
            task = SubTask(
                description=f"Create content and marketing materials for: {goal}",
                assigned_role=AgentRole.MARKETER,
                priority=5,
                estimated_complexity=0.5,
            )
            sub_tasks.append(task)

        if AgentRole.OUTREACH in required_roles:
            task = SubTask(
                description=f"Execute outreach and communication for: {goal}",
                assigned_role=AgentRole.OUTREACH,
                priority=6,
                estimated_complexity=0.4,
            )
            if sub_tasks:
                task.requires_output_from = [sub_tasks[-1].id]
                dependencies[task.id] = [sub_tasks[-1].id]
            sub_tasks.append(task)

        if AgentRole.OPERATOR in required_roles:
            task = SubTask(
                description=f"Deploy and operationalize: {goal}",
                assigned_role=AgentRole.OPERATOR,
                priority=7,
                estimated_complexity=0.6,
            )
            if sub_tasks:
                task.requires_output_from = [sub_tasks[-1].id]
                dependencies[task.id] = [sub_tasks[-1].id]
            sub_tasks.append(task)

        if not sub_tasks:
            sub_tasks.append(
                SubTask(
                    description=goal,
                    assigned_role=AgentRole.GENERAL,
                    priority=5,
                    estimated_complexity=0.5,
                )
            )

        has_deps = bool(dependencies)
        strategy = "sequential" if has_deps else "parallel"

        return TaskDecomposition(
            original_goal=goal,
            sub_tasks=sub_tasks,
            dependencies=dependencies,
            aggregation_strategy=strategy,
            rationale="Keyword-based decomposition",
        )

    async def _execute_sequential(
        self,
        decomposition: TaskDecomposition,
        budget_usd: float | None,
    ) -> list[ActionResult]:
        """Execute sub-tasks sequentially, passing outputs via shared memory."""
        results: list[ActionResult] = []

        for i, sub_task in enumerate(decomposition.sub_tasks, 1):
            await self._emit(
                f"\n[DELEGATE {i}/{len(decomposition.sub_tasks)}] "
                f"Assigning to {sub_task.assigned_role.value}: "
                f"{sub_task.description[:100]}"
            )

            agent = await self._assign_agent(sub_task)
            if not agent:
                await self._emit(
                    f"  [WARN] No agent for role {sub_task.assigned_role.value}, "
                    "creating general agent"
                )
                agent = Agent(config=self.config, role=AgentRole.GENERAL)
                if self._stream_callback:
                    agent.set_stream_callback(self._stream_callback)
                self.register_agent(agent)
                sub_task.assigned_agent_id = agent.id

            # Inject shared memory context into the task
            shared_context = self._shared_memory.get_context_summary(5)
            task_goal = sub_task.description
            if shared_context != "No shared context available.":
                task_goal += f"\n\nContext from other agents:\n{shared_context}"

            task = TaskContext(
                goal=task_goal,
                priority=sub_task.priority,
                budget_usd=budget_usd,
                metadata={
                    "orchestrator_task": True,
                    "sub_task_id": sub_task.id,
                },
            )

            if self._stream_callback:
                agent.set_stream_callback(self._stream_callback)

            result = await agent.run_task(task)
            sub_task.result = result
            sub_task.status = "completed" if result.success else "failed"
            results.append(result)

            # Store result in shared memory for other agents
            self._shared_memory.write(
                key=f"task_{i}_{sub_task.assigned_role.value}",
                value=result.output or result.error or "No output",
                author=agent.name,
                tags=[sub_task.assigned_role.value, "result"],
            )

            await self._emit(
                f"  [{'OK' if result.success else 'FAILED'}] "
                f"{sub_task.assigned_role.value}: "
                f"{(result.output or result.error or '')[:150]}"
            )

            # If a task fails, try reassignment
            if not result.success:
                reassigned = await self._try_reassignment(sub_task, task)
                if reassigned and reassigned.success:
                    results[-1] = reassigned
                    self._shared_memory.write(
                        key=f"task_{i}_{sub_task.assigned_role.value}",
                        value=reassigned.output or "",
                        author="reassigned_agent",
                        tags=[sub_task.assigned_role.value, "result", "retry"],
                    )

            agent.reset()

        return results

    async def _execute_parallel(
        self,
        decomposition: TaskDecomposition,
        budget_usd: float | None,
    ) -> list[ActionResult]:
        """Execute independent sub-tasks in parallel."""
        await self._emit(
            f"[ORCHESTRATOR] Running {len(decomposition.sub_tasks)} tasks in parallel"
        )

        async def _run_sub_task(sub_task: SubTask, idx: int) -> ActionResult:
            agent = await self._assign_agent(sub_task)
            if not agent:
                agent = Agent(config=self.config, role=AgentRole.GENERAL)
                if self._stream_callback:
                    agent.set_stream_callback(self._stream_callback)
                self.register_agent(agent)
                sub_task.assigned_agent_id = agent.id

            task = TaskContext(
                goal=sub_task.description,
                priority=sub_task.priority,
                budget_usd=budget_usd,
                metadata={
                    "orchestrator_task": True,
                    "sub_task_id": sub_task.id,
                },
            )

            if self._stream_callback:
                agent.set_stream_callback(self._stream_callback)

            result = await agent.run_task(task)
            sub_task.result = result
            sub_task.status = "completed" if result.success else "failed"

            self._shared_memory.write(
                key=f"parallel_{idx}_{sub_task.assigned_role.value}",
                value=result.output or result.error or "No output",
                author=agent.name,
                tags=[sub_task.assigned_role.value, "result", "parallel"],
            )

            agent.reset()
            return result

        tasks = [
            _run_sub_task(st, i)
            for i, st in enumerate(decomposition.sub_tasks)
        ]
        results_raw = await asyncio.gather(*tasks, return_exceptions=True)

        processed: list[ActionResult] = []
        for result in results_raw:
            if isinstance(result, Exception):
                processed.append(
                    ActionResult(
                        success=False,
                        error=str(result),
                        action_type="parallel_error",
                    )
                )
            else:
                processed.append(result)

        return processed

    async def _execute_map_reduce(
        self,
        decomposition: TaskDecomposition,
        budget_usd: float | None,
    ) -> list[ActionResult]:
        """Map-reduce: parallel map, then LLM-powered reduce."""
        map_results = await self._execute_parallel(decomposition, budget_usd)

        successful_outputs = [
            r.output for r in map_results if r.success and r.output
        ]

        if self._llm_router and successful_outputs:
            try:
                from sovereign.llm.provider import Message, MessageRole

                messages = [
                    Message(
                        role=MessageRole.SYSTEM,
                        content=(
                            "You are synthesizing results from multiple AI agents. "
                            "Combine their outputs into a coherent, comprehensive "
                            "final result. Preserve key details from each."
                        ),
                    ),
                    Message(
                        role=MessageRole.USER,
                        content=(
                            f"Goal: {decomposition.original_goal}\n\n"
                            "Agent outputs to synthesize:\n"
                            + "\n---\n".join(
                                f"Agent {i+1}:\n{out}"
                                for i, out in enumerate(successful_outputs)
                            )
                        ),
                    ),
                ]

                response = await self._llm_router.generate(
                    messages=messages,
                    temperature=0.5,
                    max_tokens=2048,
                )

                reduce_result = ActionResult(
                    success=True,
                    output=response.content,
                    action_type="map_reduce_synthesis",
                    metadata={
                        "total_mapped": len(map_results),
                        "successful": len(successful_outputs),
                    },
                )
                return map_results + [reduce_result]

            except Exception:
                pass

        reduce_result = ActionResult(
            success=len(successful_outputs) > 0,
            output="\n\n---\n\n".join(successful_outputs),
            action_type="map_reduce_aggregate",
            metadata={
                "total_mapped": len(map_results),
                "successful": len(successful_outputs),
            },
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

        agent_ids = self._role_agents.get(role, [])
        for agent_id in agent_ids:
            if agent_id != original_agent_id:
                agent = self._agents.get(agent_id)
                if agent and not agent.is_busy:
                    await self._emit(
                        f"  [REASSIGN] Trying another {role.value} agent..."
                    )
                    sub_task.assigned_agent_id = agent.id
                    if self._stream_callback:
                        agent.set_stream_callback(self._stream_callback)
                    result = await agent.run_task(task)
                    agent.reset()
                    return result

        return None

    async def _aggregate_results(
        self,
        results: list[ActionResult],
        goal: str,
    ) -> ActionResult:
        """Aggregate results, using LLM for intelligent synthesis."""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        all_outputs = [r.output for r in successful if r.output]
        all_errors = [r.error for r in failed if r.error]

        overall_success = len(successful) > len(failed)

        if self._llm_router and all_outputs and len(all_outputs) > 1:
            try:
                from sovereign.llm.provider import Message, MessageRole

                messages = [
                    Message(
                        role=MessageRole.SYSTEM,
                        content=(
                            "You are the Director of an AI agent team. "
                            "Synthesize the results from your team's work "
                            "into a clear, actionable final report. "
                            "Highlight key findings and deliverables."
                        ),
                    ),
                    Message(
                        role=MessageRole.USER,
                        content=(
                            f"Original goal: {goal}\n\n"
                            f"Results from {len(successful)} agents:\n\n"
                            + "\n\n---\n\n".join(all_outputs)
                            + (
                                f"\n\n{len(failed)} tasks failed: "
                                + "; ".join(all_errors)
                                if all_errors
                                else ""
                            )
                        ),
                    ),
                ]

                response = await self._llm_router.generate(
                    messages=messages,
                    temperature=0.5,
                    max_tokens=2048,
                )

                return ActionResult(
                    success=overall_success,
                    output=response.content,
                    error="; ".join(all_errors) if all_errors else None,
                    action_type="orchestration_complete",
                    metadata={
                        "goal": goal,
                        "total_sub_tasks": len(results),
                        "successful": len(successful),
                        "failed": len(failed),
                        "shared_memory_entries": len(
                            self._shared_memory.entries
                        ),
                    },
                )
            except Exception:
                pass

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

    async def send_agent_message(
        self,
        from_agent_id: str,
        to_agent_id: str,
        content: str,
        message_type: str = "info",
    ) -> None:
        """Send a message between agents via the message bus."""
        message = AgentMessage(
            sender=from_agent_id,
            recipient=to_agent_id,
            content=content,
            message_type=message_type,
        )
        self._message_log.append(message)
        self._state.messages_exchanged += 1

        recipient = self._agents.get(to_agent_id)
        if recipient:
            await recipient.receive_message(message)

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
            self._message_log.append(message)
            await agent.receive_message(message)

    async def _emit(self, message: str) -> None:
        """Emit a streaming message."""
        if self._stream_callback:
            self._stream_callback(message)
