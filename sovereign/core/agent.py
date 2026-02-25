"""Base Agent class - the fundamental building block of Sovereign.

Each agent has a role, can plan, reason, execute actions, and learn from outcomes.
Agents communicate through a message-passing protocol and can be orchestrated
by the Orchestrator for multi-agent collaboration.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig
from sovereign.core.executor import ActionResult, Executor
from sovereign.core.planner import Plan, Planner, StepStatus
from sovereign.core.reasoning import ReasoningEngine, Reflection
from sovereign.llm.router import ModelRouter
from sovereign.tools.registry import ToolRegistry


class AgentRole(str, Enum):
    """Predefined agent specializations."""

    DIRECTOR = "director"
    RESEARCHER = "researcher"
    CODER = "coder"
    MARKETER = "marketer"
    ANALYST = "analyst"
    OUTREACH = "outreach"
    OPERATOR = "operator"
    GENERAL = "general"


class AgentState(str, Enum):
    """Current state of an agent."""

    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    WAITING_APPROVAL = "waiting_approval"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentMessage(BaseModel):
    """Message passed between agents."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    recipient: str
    content: str
    message_type: str = "task"  # task, result, query, info, error
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskContext(BaseModel):
    """Context for a task being executed by an agent."""

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    parent_task_id: str | None = None
    constraints: list[str] = Field(default_factory=list)
    priority: int = 5  # 1 = highest, 10 = lowest
    deadline: datetime | None = None
    budget_usd: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    history: list[AgentMessage] = Field(default_factory=list)


class AgentCapability(BaseModel):
    """Describes a capability that an agent possesses."""

    name: str
    description: str
    tool_names: list[str] = Field(default_factory=list)
    complexity_range: tuple[float, float] = (0.0, 1.0)


class Agent:
    """Base agent with planning, reasoning, and execution capabilities.

    The agent loop follows: Plan -> Execute -> Observe -> Reflect -> Replan.
    This is a tree-of-thought approach where the agent can explore multiple
    paths and self-correct based on outcomes.
    """

    def __init__(
        self,
        config: SovereignConfig,
        role: AgentRole = AgentRole.GENERAL,
        name: str | None = None,
        capabilities: list[AgentCapability] | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name or f"{role.value}-{self.id[:8]}"
        self.role = role
        self.config = config
        self.state = AgentState.IDLE
        self.capabilities = capabilities or []

        # Initialize LLM router for real AI-powered planning/reasoning
        self.llm_router = ModelRouter(config)

        # Initialize and register all real tools
        self.tool_registry = ToolRegistry()
        self._register_all_tools()

        self.planner = Planner(config, llm_router=self.llm_router)
        self.reasoning = ReasoningEngine(config, llm_router=self.llm_router)
        self.executor = Executor(config, llm_router=self.llm_router)
        self.executor.register_tools(
            {name: tool for name, tool in self.tool_registry._tools.items()}
        )

        self._message_queue: asyncio.Queue[AgentMessage] = asyncio.Queue()
        self._current_task: TaskContext | None = None
        self._current_plan: Plan | None = None
        self._execution_history: list[ActionResult] = []
        self._reflections: list[Reflection] = []
        self._stream_callback: Any = None  # For streaming output

    def _register_all_tools(self) -> None:
        """Register all real tools so the agent can actually use them."""
        # Core tools (always available)
        from sovereign.tools.api_client import APIClientTool
        from sovereign.tools.browser import BrowserTool
        from sovereign.tools.code_executor import CodeExecutorTool
        from sovereign.tools.email_client import EmailSendTool
        from sovereign.tools.file_manager import FileListTool, FileReadTool, FileWriteTool
        from sovereign.tools.shell import ShellTool
        from sovereign.tools.web_search import WebSearchTool

        self.tool_registry.register(ShellTool())
        self.tool_registry.register(FileReadTool())
        self.tool_registry.register(FileWriteTool())
        self.tool_registry.register(FileListTool())
        self.tool_registry.register(WebSearchTool())
        self.tool_registry.register(BrowserTool())
        self.tool_registry.register(APIClientTool())
        self.tool_registry.register(CodeExecutorTool())
        self.tool_registry.register(EmailSendTool(
            smtp_host=self.config.channels.email_smtp_host,
            smtp_port=self.config.channels.email_smtp_port,
            username=self.config.channels.email_username,
            password=self.config.channels.email_password,
        ))

        # Communication tools (Twilio)
        from sovereign.tools.twilio_tool import SMSSendTool, VoiceCallTool, WhatsAppTool

        self.tool_registry.register(SMSSendTool())
        self.tool_registry.register(VoiceCallTool())
        self.tool_registry.register(WhatsAppTool())

        # Business tools
        from sovereign.tools.crm import (
            CRMAddLeadTool,
            CRMListLeadsTool,
            CRMLogInteractionTool,
            CRMUpdateStageTool,
        )
        from sovereign.tools.invoice import InvoiceGenerateTool, PaymentLinkTool
        from sovereign.tools.lead_scraper import LeadScraperTool
        from sovereign.tools.website_builder import (
            WebsiteDeployTool,
            WebsiteGeneratorTool,
        )

        self.tool_registry.register(LeadScraperTool())
        self.tool_registry.register(CRMAddLeadTool())
        self.tool_registry.register(CRMUpdateStageTool())
        self.tool_registry.register(CRMListLeadsTool())
        self.tool_registry.register(CRMLogInteractionTool())
        self.tool_registry.register(InvoiceGenerateTool())
        self.tool_registry.register(PaymentLinkTool())
        self.tool_registry.register(WebsiteGeneratorTool())
        self.tool_registry.register(WebsiteDeployTool())

        # Design & Deploy tools (Phase 5)
        from sovereign.tools.browser_auto import (
            BrowserInteractTool,
            BrowserNavigateTool,
            BrowserScrapeTool,
        )
        from sovereign.tools.deploy_tool import DeployTool, ScreenshotTool
        from sovereign.tools.design_engine import AIDesignTool
        from sovereign.tools.site_generator import MultiPageSiteTool, ReactScaffoldTool

        design_tool = AIDesignTool()
        design_tool.set_llm_router(self.llm_router)
        self.tool_registry.register(design_tool)
        self.tool_registry.register(MultiPageSiteTool())
        self.tool_registry.register(ReactScaffoldTool())
        self.tool_registry.register(DeployTool())
        self.tool_registry.register(ScreenshotTool())
        self.tool_registry.register(BrowserNavigateTool())
        self.tool_registry.register(BrowserInteractTool())
        self.tool_registry.register(BrowserScrapeTool())

    def set_stream_callback(self, callback: Any) -> None:
        """Set a callback for streaming agent output in real-time."""
        self._stream_callback = callback

    @property
    def is_busy(self) -> bool:
        return self.state not in (AgentState.IDLE, AgentState.COMPLETED, AgentState.FAILED)

    async def run_task(self, task: TaskContext) -> ActionResult:
        """Execute a complete task through the plan-execute-reflect loop.

        This is the main agent loop:
        1. Create initial plan from goal
        2. Execute each step, observing outcomes
        3. After each step, reflect on progress
        4. If reflection suggests replanning, create new plan
        5. Continue until goal is achieved or failure
        """
        self._current_task = task
        self.state = AgentState.PLANNING

        try:
            # Phase 1: Create initial plan
            plan = await self.planner.create_plan(
                goal=task.goal,
                constraints=task.constraints,
                context=self._build_context(task),
                agent_role=self.role,
            )
            self._current_plan = plan

            # Phase 2: Execute plan with reflection loop
            max_replans = 3
            replan_count = 0

            await self._emit(f"[PLAN] {len(plan.steps)} steps generated")
            for i, s in enumerate(plan.steps, 1):
                await self._emit(f"  {i}. [{s.step_type.value}] {s.description}")

            while not plan.is_complete and replan_count <= max_replans:
                current_step = plan.get_next_step()
                if current_step is None:
                    break

                # Execute step
                self.state = AgentState.EXECUTING
                step_idx = plan.steps.index(current_step) + 1
                await self._emit(
                    f"\n[STEP {step_idx}/{len(plan.steps)}] "
                    f"{current_step.step_type.value}: {current_step.description}"
                )

                result = await self.executor.execute_step(
                    step=current_step,
                    context=self._build_context(task),
                )
                self._execution_history.append(result)

                # Update step status based on result
                if result.success:
                    current_step.status = StepStatus.COMPLETED
                    current_step.output = result.output
                    await self._emit(f"  -> OK: {(result.output or '')[:200]}")
                else:
                    current_step.status = StepStatus.FAILED
                    current_step.error = result.error
                    await self._emit(f"  -> FAILED: {result.error}")

                # Phase 3: Reflect on progress
                self.state = AgentState.REFLECTING
                reflection = await self.reasoning.reflect(
                    goal=task.goal,
                    plan=plan,
                    last_result=result,
                    history=self._execution_history,
                )
                self._reflections.append(reflection)
                await self._emit(
                    f"  [REFLECT] Progress: {reflection.goal_progress:.0%} | "
                    f"Confidence: {reflection.confidence:.0%}"
                )

                # Phase 4: Decide whether to replan
                if reflection.should_replan and replan_count < max_replans:
                    self.state = AgentState.PLANNING
                    await self._emit("  [REPLAN] Adjusting strategy...")
                    plan = await self.planner.replan(
                        original_plan=plan,
                        reflection=reflection,
                        goal=task.goal,
                        context=self._build_context(task),
                    )
                    self._current_plan = plan
                    replan_count += 1
                elif reflection.should_abort:
                    self.state = AgentState.FAILED
                    await self._emit("[ABORT] Agent is aborting task.")
                    return ActionResult(
                        success=False,
                        output="",
                        error=f"Agent aborted: {reflection.reasoning}",
                        action_type="abort",
                    )

            # Compile final result
            self.state = AgentState.COMPLETED
            final_output = self._compile_results()
            return ActionResult(
                success=True,
                output=final_output,
                action_type="task_complete",
                metadata={
                    "steps_executed": len(self._execution_history),
                    "replans": replan_count,
                    "reflections": len(self._reflections),
                },
            )

        except Exception as e:
            self.state = AgentState.FAILED
            return ActionResult(
                success=False,
                output="",
                error=str(e),
                action_type="task_error",
            )

    async def receive_message(self, message: AgentMessage) -> None:
        """Receive a message from another agent or the orchestrator."""
        await self._message_queue.put(message)
        if self._current_task:
            self._current_task.history.append(message)

    async def send_message(
        self,
        recipient: str,
        content: str,
        message_type: str = "info",
        metadata: dict[str, Any] | None = None,
    ) -> AgentMessage:
        """Create a message to send to another agent."""
        return AgentMessage(
            sender=self.id,
            recipient=recipient,
            content=content,
            message_type=message_type,
            metadata=metadata or {},
        )

    def _build_context(self, task: TaskContext) -> dict[str, Any]:
        """Build execution context from task and agent state."""
        return {
            "agent_id": self.id,
            "agent_role": self.role.value,
            "agent_name": self.name,
            "task_id": task.task_id,
            "goal": task.goal,
            "constraints": task.constraints,
            "priority": task.priority,
            "execution_history": [r.model_dump() for r in self._execution_history[-10:]],
            "reflections": [r.model_dump() for r in self._reflections[-5:]],
            "capabilities": [c.model_dump() for c in self.capabilities],
        }

    async def _emit(self, message: str) -> None:
        """Emit a streaming message to the callback if set."""
        if self._stream_callback:
            self._stream_callback(message)

    def _compile_results(self) -> str:
        """Compile all execution results into a final summary."""
        successful_outputs = [
            r.output for r in self._execution_history if r.success and r.output
        ]
        if not successful_outputs:
            return "No outputs produced."
        return "\n\n---\n\n".join(successful_outputs)

    def reset(self) -> None:
        """Reset agent to idle state for new tasks."""
        self.state = AgentState.IDLE
        self._current_task = None
        self._current_plan = None
        self._execution_history.clear()
        self._reflections.clear()
