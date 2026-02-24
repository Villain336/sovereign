"""Sovereign Web API - FastAPI REST endpoints.

Provides a REST API for managing agents, tasks, the design engine,
and viewing system status. This is the backend for the Sovereign Web UI.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from sovereign.config import SovereignConfig, load_config
from sovereign.core.task_queue import PersistentTask, TaskQueue, TaskStatus


def create_app() -> Any:
    """Create and configure the FastAPI application."""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import HTMLResponse
        from pydantic import BaseModel
    except ImportError as exc:
        raise ImportError(
            "FastAPI is required for the web UI. Install with: pip install fastapi uvicorn"
        ) from exc

    app = FastAPI(
        title="Sovereign API",
        description="REST API for the Sovereign Autonomous Agent Platform",
        version="0.2.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize shared state
    config = load_config()
    task_queue = TaskQueue()

    # ---------------------------------------------------------------
    # Request/Response models
    # ---------------------------------------------------------------

    class TaskCreate(BaseModel):
        goal: str
        priority: int = 5
        agent_role: str = "general"
        budget_usd: float | None = None

    class TaskResponse(BaseModel):
        id: str
        goal: str
        status: str
        priority: int
        agent_role: str
        budget_usd: float | None
        result_output: str
        result_error: str
        retry_count: int
        created_at: str
        started_at: str
        completed_at: str

    class DesignRequest(BaseModel):
        page_type: str = "saas_landing"
        brand_name: str
        description: str
        palette: str = "midnight"
        sections: str = "hero,features,pricing,testimonials,cta,footer"
        use_llm: str = "true"

    class RunGoalRequest(BaseModel):
        goal: str
        budget_usd: float | None = None
        priority: int = 5

    # ---------------------------------------------------------------
    # System endpoints
    # ---------------------------------------------------------------

    @app.get("/")
    async def root() -> dict[str, str]:
        return {
            "name": "Sovereign API",
            "version": "0.2.0",
            "status": "running",
        }

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    @app.get("/status")
    async def status() -> dict[str, Any]:
        from sovereign import __version__
        stats = task_queue.get_stats()
        return {
            "version": __version__,
            "config": {
                "data_dir": config.data_dir,
                "default_model": config.llm.default_model,
                "models_configured": len(config.llm.models),
                "budget_per_task": config.safety.max_budget_per_task_usd,
                "budget_per_day": config.safety.max_budget_per_day_usd,
            },
            "task_queue": stats,
        }

    # ---------------------------------------------------------------
    # Agent endpoints
    # ---------------------------------------------------------------

    @app.get("/agents")
    async def list_agents() -> list[dict[str, str]]:
        return [
            {"role": "director", "name": "Director", "description": "Coordinates all agents"},
            {"role": "researcher", "name": "Researcher", "description": "Information gathering"},
            {"role": "coder", "name": "Coder", "description": "Software development"},
            {"role": "marketer", "name": "Marketer", "description": "Content & marketing"},
            {"role": "analyst", "name": "Analyst", "description": "Data analysis"},
            {"role": "outreach", "name": "Outreach", "description": "Communication"},
            {"role": "operator", "name": "Operator", "description": "Operations & deployment"},
        ]

    # ---------------------------------------------------------------
    # Task Queue endpoints
    # ---------------------------------------------------------------

    @app.post("/tasks")
    async def create_task(req: TaskCreate) -> TaskResponse:
        task = PersistentTask(
            goal=req.goal,
            priority=req.priority,
            agent_role=req.agent_role,
            budget_usd=req.budget_usd,
        )
        task_queue.add_task(task)
        return _task_to_response(task)

    @app.get("/tasks")
    async def list_tasks(
        status_filter: str | None = None,
        limit: int = 50,
    ) -> list[TaskResponse]:
        task_status = TaskStatus(status_filter) if status_filter else None
        tasks = task_queue.list_tasks(status=task_status, limit=limit)
        return [_task_to_response(t) for t in tasks]

    @app.get("/tasks/{task_id}")
    async def get_task(task_id: str) -> TaskResponse:
        task = task_queue.get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return _task_to_response(task)

    @app.post("/tasks/{task_id}/cancel")
    async def cancel_task(task_id: str) -> dict[str, str]:
        task = task_queue.get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        task_queue.cancel_task(task_id)
        return {"status": "cancelled", "task_id": task_id}

    @app.post("/tasks/{task_id}/retry")
    async def retry_task(task_id: str) -> dict[str, Any]:
        success = task_queue.retry_task(task_id)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot retry (max retries reached or task not found)")
        return {"status": "retrying", "task_id": task_id}

    @app.get("/tasks/stats/summary")
    async def task_stats() -> dict[str, int]:
        return task_queue.get_stats()

    # ---------------------------------------------------------------
    # Run agent goal (async)
    # ---------------------------------------------------------------

    @app.post("/run")
    async def run_goal(req: RunGoalRequest) -> dict[str, str]:
        """Queue a goal for agent execution."""
        task = PersistentTask(
            goal=req.goal,
            priority=req.priority,
            budget_usd=req.budget_usd,
        )
        task_queue.add_task(task)

        # Run in background
        asyncio.create_task(_execute_task(task.id, config, task_queue))

        return {"task_id": task.id, "status": "queued"}

    # ---------------------------------------------------------------
    # Design Engine endpoints
    # ---------------------------------------------------------------

    @app.post("/design")
    async def generate_design(req: DesignRequest) -> dict[str, Any]:
        from sovereign.tools.design_engine import AIDesignTool

        tool = AIDesignTool()

        # Wire up LLM if available
        if config.llm.models:
            try:
                from sovereign.llm.router import ModelRouter
                router = ModelRouter(config)
                tool.set_llm_router(router)
            except Exception:
                pass

        result = await tool.execute(
            page_type=req.page_type,
            brand_name=req.brand_name,
            description=req.description,
            palette=req.palette,
            sections=req.sections,
            use_llm=req.use_llm,
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Read the generated HTML
        output_dir = result.metadata.get("output_dir", "")
        html_content = ""
        if output_dir:
            html_path = os.path.join(output_dir, "index.html")
            if os.path.exists(html_path):
                with open(html_path, encoding="utf-8") as f:
                    html_content = f.read()

        return {
            "success": True,
            "output_dir": output_dir,
            "html_preview": html_content[:50000],
            "metadata": result.metadata,
        }

    @app.get("/design/palettes")
    async def list_palettes() -> dict[str, Any]:
        from sovereign.tools.design_engine import DESIGN_SYSTEM
        return DESIGN_SYSTEM["color_palettes"]

    # ---------------------------------------------------------------
    # Tools endpoints
    # ---------------------------------------------------------------

    @app.get("/tools")
    async def list_tools() -> list[dict[str, str]]:
        return [
            {"name": "web_search", "category": "search", "description": "Search the web"},
            {"name": "browser", "category": "browser", "description": "Browse web pages"},
            {"name": "browser_navigate", "category": "browser", "description": "Navigate with headless Chrome"},
            {"name": "browser_interact", "category": "browser", "description": "Interact with web elements"},
            {"name": "browser_scrape", "category": "browser", "description": "Scrape structured data"},
            {"name": "shell", "category": "system", "description": "Execute shell commands"},
            {"name": "file_read", "category": "filesystem", "description": "Read files"},
            {"name": "file_write", "category": "filesystem", "description": "Write files"},
            {"name": "ai_design", "category": "design", "description": "AI-powered UI generation"},
            {"name": "site_multipage", "category": "design", "description": "Multi-page site generator"},
            {"name": "scaffold_react", "category": "design", "description": "React project scaffolding"},
            {"name": "deploy_site", "category": "deploy", "description": "Deploy to Netlify/Vercel"},
            {"name": "screenshot", "category": "design", "description": "Take screenshots"},
            {"name": "lead_scrape", "category": "business", "description": "Find business leads"},
            {"name": "crm_add_lead", "category": "business", "description": "CRM pipeline management"},
            {"name": "invoice_generate", "category": "business", "description": "Generate invoices"},
            {"name": "sms_send", "category": "communication", "description": "Send SMS via Twilio"},
            {"name": "email_send", "category": "communication", "description": "Send emails"},
        ]

    # ---------------------------------------------------------------
    # Dashboard (serves a built-in HTML dashboard)
    # ---------------------------------------------------------------

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard() -> str:
        from sovereign.web.dashboard import DASHBOARD_HTML
        return DASHBOARD_HTML

    # ---------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------

    def _task_to_response(task: PersistentTask) -> TaskResponse:
        return TaskResponse(
            id=task.id,
            goal=task.goal,
            status=task.status.value,
            priority=task.priority,
            agent_role=task.agent_role,
            budget_usd=task.budget_usd,
            result_output=task.result_output,
            result_error=task.result_error,
            retry_count=task.retry_count,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
        )

    return app


async def _execute_task(
    task_id: str,
    config: SovereignConfig,
    queue: TaskQueue,
) -> None:
    """Execute a task from the queue using the agent system."""
    queue.update_status(task_id, TaskStatus.IN_PROGRESS)

    task = queue.get_task(task_id)
    if task is None:
        return

    try:
        from sovereign.core.agent import Agent, AgentRole, TaskContext

        agent = Agent(
            config=config,
            role=AgentRole(task.agent_role) if task.agent_role != "general" else AgentRole.GENERAL,
        )

        task_ctx = TaskContext(
            goal=task.goal,
            priority=task.priority,
            budget_usd=task.budget_usd,
        )

        result = await agent.run_task(task_ctx)

        if result.success:
            queue.update_status(
                task_id,
                TaskStatus.COMPLETED,
                output=result.output or "Completed",
            )
        else:
            queue.update_status(
                task_id,
                TaskStatus.FAILED,
                error=result.error or "Unknown error",
            )
    except Exception as e:
        queue.update_status(task_id, TaskStatus.FAILED, error=str(e))
