"""Sovereign CLI - Rich-formatted command-line interface.

Provides a beautiful, interactive CLI for managing the Sovereign
autonomous agent platform. Built with Click + Rich.
"""

from __future__ import annotations

import asyncio

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from sovereign import __version__
from sovereign.config import SovereignConfig, load_config

console = Console()


def get_config(config_path: str | None = None) -> SovereignConfig:
    """Load configuration."""
    # config_path reserved for future YAML config support
    return load_config()


@click.group()
@click.version_option(version=__version__, prog_name="sovereign")
def main() -> None:
    """Sovereign - Autonomous AI Agent Platform for Business Automation.

    The most advanced open-source autonomous agent that can plan, reason,
    execute, learn, and run your business operations.
    """
    pass


@main.command()
@click.option("--config", "-c", default=None, help="Path to config file")
def status(config: str | None) -> None:
    """Show the current status of the Sovereign platform."""
    cfg = get_config(config)

    console.print(
        Panel(
            f"[bold cyan]Sovereign v{__version__}[/bold cyan]\n"
            f"[dim]Autonomous AI Agent Platform[/dim]",
            title="Status",
            border_style="cyan",
        )
    )

    # Config info
    table = Table(title="Configuration", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Data Directory", str(cfg.data_dir))
    table.add_row("Log Level", cfg.log_level.value)
    table.add_row("Default LLM", cfg.llm.default_model)
    table.add_row("Models Configured", str(len(cfg.llm.models)))
    table.add_row("Budget Limit (Daily)", f"${cfg.safety.max_budget_per_day_usd:.2f}")
    table.add_row("Budget Limit (Per Task)", f"${cfg.safety.max_budget_per_task_usd:.2f}")
    table.add_row("Kill Switch", "ACTIVE" if cfg.safety.kill_switch_enabled else "OFF")
    table.add_row("Sandbox Mode", "ON" if cfg.safety.sandbox_enabled else "OFF")

    console.print(table)


@main.command()
@click.argument("goal")
@click.option("--budget", "-b", default=None, type=float, help="Budget limit in USD")
@click.option("--priority", "-p", default=5, type=int, help="Task priority (1-10)")
@click.option("--agent", "-a", default=None, help="Specific agent role to use")
@click.option("--config", "-c", default=None, help="Path to config file")
def run(
    goal: str,
    budget: float | None,
    priority: int,
    agent: str | None,
    config: str | None,
) -> None:
    """Execute a goal using the autonomous agent system.

    GOAL is the task description for the agent to accomplish.

    Examples:
        sovereign run "Research competitors in the CRM space"
        sovereign run "Write a blog post about AI automation" --budget 5.0
        sovereign run "Deploy the landing page" --agent operator
    """
    cfg = get_config(config)

    console.print(
        Panel(
            f"[bold]Goal:[/bold] {goal}\n"
            f"[bold]Budget:[/bold] ${budget:.2f if budget else 'unlimited'}\n"
            f"[bold]Priority:[/bold] {priority}\n"
            f"[bold]Agent:[/bold] {agent or 'auto-routed'}",
            title="[cyan]Starting Task[/cyan]",
            border_style="cyan",
        )
    )

    async def _run() -> None:
        from sovereign.core.agent import Agent, AgentRole, TaskContext

        task_agent = Agent(
            config=cfg,
            role=AgentRole(agent) if agent else AgentRole.GENERAL,
            name=agent or "General",
        )

        # Set up streaming callback for real-time output
        def stream_callback(message: str) -> None:
            # Color-code different message types
            if message.startswith("[PLAN]"):
                console.print(f"[bold cyan]{message}[/bold cyan]")
            elif message.startswith("[STEP"):
                console.print(f"[bold yellow]{message}[/bold yellow]")
            elif message.startswith("  -> OK:"):
                console.print(f"[green]{message}[/green]")
            elif message.startswith("  -> FAILED:"):
                console.print(f"[red]{message}[/red]")
            elif "[REFLECT]" in message:
                console.print(f"[dim]{message}[/dim]")
            elif "[REPLAN]" in message:
                console.print(f"[bold magenta]{message}[/bold magenta]")
            elif "[ABORT]" in message:
                console.print(f"[bold red]{message}[/bold red]")
            else:
                console.print(message)

        task_agent.set_stream_callback(stream_callback)

        task = TaskContext(
            goal=goal,
            priority=priority,
            budget_usd=budget,
        )

        console.print("[yellow]Planning...[/yellow]")
        result = await task_agent.run_task(task)

        # Save lesson to self-improvement memory
        from sovereign.core.self_improve import record_outcome
        record_outcome(
            goal=goal,
            success=result.success,
            output=result.output or "",
            error=result.error,
            steps_executed=result.metadata.get("steps_executed", 0),
        )

        if result.success:
            console.print(
                Panel(
                    f"[green]{result.output or 'Task completed successfully'}[/green]",
                    title="[green]Success[/green]",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[red]{result.error or 'Task failed'}[/red]",
                    title="[red]Failed[/red]",
                    border_style="red",
                )
            )

    asyncio.run(_run())


@main.command()
@click.option("--config", "-c", default=None, help="Path to config file")
def agents(config: str | None) -> None:
    """List all available specialized agents."""
    table = Table(title="Available Agents", show_header=True)
    table.add_column("Role", style="cyan", width=12)
    table.add_column("Description", style="white")
    table.add_column("Capabilities", style="green")

    agent_info = [
        ("researcher", "Information gathering and analysis", "Web research, competitive analysis, data collection"),
        ("coder", "Software development", "Code generation, debugging, testing, deployment"),
        ("marketer", "Content and marketing", "Content creation, SEO, social media, email marketing"),
        ("analyst", "Data analysis and reporting", "Data analysis, financial reporting, forecasting"),
        ("outreach", "Communication and outreach", "Email campaigns, lead nurturing, follow-ups"),
        ("operator", "Operations and deployment", "Deployment, infrastructure, monitoring, automation"),
        ("general", "General-purpose agent", "All capabilities (auto-routed)"),
    ]

    for role, desc, caps in agent_info:
        table.add_row(role, desc, caps)

    console.print(table)


@main.command()
@click.option("--config", "-c", default=None, help="Path to config file")
def tools(config: str | None) -> None:
    """List all available tools."""
    table = Table(title="Available Tools", show_header=True)
    table.add_column("Tool", style="cyan", width=16)
    table.add_column("Category", style="yellow", width=14)
    table.add_column("Description", style="white")
    table.add_column("Risk", style="red", width=6)

    tool_info = [
        # Core tools
        ("web_search", "search", "Search the web (DuckDuckGo, no API key)", "Low"),
        ("browser", "browser", "Browse web pages and extract content", "Low"),
        ("shell", "system", "Execute shell commands", "Med"),
        ("code_executor", "code", "Execute code (Python, JS, shell)", "Med"),
        ("file_read", "filesystem", "Read file contents", "Low"),
        ("file_write", "filesystem", "Write content to files", "Med"),
        ("file_list", "filesystem", "List directory contents", "Low"),
        ("api_request", "api", "Make HTTP API requests", "Med"),
        ("email_send", "communication", "Send emails via SMTP", "Med"),
        # Communication tools
        ("sms_send", "communication", "Send SMS via Twilio", "Med"),
        ("voice_call", "communication", "Make voice calls via Twilio", "High"),
        ("whatsapp_send", "communication", "Send WhatsApp messages", "Med"),
        # Business tools
        ("lead_scrape", "business", "Find & extract business leads", "Low"),
        ("crm_add_lead", "business", "Add lead to CRM pipeline", "Low"),
        ("crm_update_stage", "business", "Move lead through pipeline", "Low"),
        ("crm_list_leads", "business", "List/filter CRM leads", "Low"),
        ("crm_log_interaction", "business", "Log sales interaction", "Low"),
        ("invoice_generate", "business", "Generate HTML invoices", "Low"),
        ("payment_link", "business", "Create Stripe payment links", "Med"),
        ("website_generate", "business", "Generate websites from description", "Low"),
        ("website_deploy", "business", "Deploy websites to the web", "Med"),
        # Design & Deploy tools
        ("ai_design", "design", "Claude-powered Tailwind CSS page generation", "Low"),
        ("site_multipage", "design", "Multi-page static site generator", "Low"),
        ("scaffold_react", "design", "React + Vite project scaffolding", "Low"),
        ("deploy_site", "deploy", "Deploy to Netlify / Vercel", "Med"),
        ("screenshot", "design", "Headless Chrome screenshot capture", "Low"),
        # Browser automation tools
        ("browser_navigate", "browser", "Navigate URLs with headless Chrome", "Low"),
        ("browser_interact", "browser", "Interact with web page elements", "Med"),
        ("browser_scrape", "browser", "Scrape structured data from pages", "Low"),
    ]

    for name, category, desc, risk in tool_info:
        table.add_row(name, category, desc, risk)

    console.print(table)


@main.command()
@click.option("--config", "-c", default=None, help="Path to config file")
def dashboard(config: str | None) -> None:
    """Show the business dashboard with key metrics."""
    get_config(config)  # Validate config loads

    console.print(
        Panel(
            "[bold cyan]Sovereign Business Dashboard[/bold cyan]",
            border_style="cyan",
        )
    )

    # Architecture overview
    tree = Tree("[bold]Sovereign Architecture[/bold]")

    core = tree.add("[cyan]Core[/cyan]")
    core.add("Agent Loop: Plan → Execute → Observe → Reflect → Replan")
    core.add("Tree-of-Thought Planner (3-candidate evaluation)")
    core.add("Self-Critique Reasoning Engine")
    core.add("Multi-Agent Orchestrator")

    memory = tree.add("[green]Memory[/green]")
    memory.add("Working Memory (context window)")
    memory.add("Episodic Memory (past experiences)")
    memory.add("Semantic Memory (vector knowledge)")
    memory.add("Knowledge Graph (entities & relationships)")

    tools_tree = tree.add("[yellow]Tools[/yellow]")
    tools_tree.add("Web Search, Browser, Shell, Code Executor")
    tools_tree.add("File I/O, API Client, Email")
    tools_tree.add("SMS, Voice Calls, WhatsApp (Twilio)")
    tools_tree.add("Lead Scraper, CRM Pipeline, Invoices")
    tools_tree.add("Website Generator & Deployer")
    tools_tree.add("Payment Links (Stripe)")

    business = tree.add("[magenta]Business Modules[/magenta]")
    business.add("Lead Pipeline, Content Pipeline")
    business.add("Revenue Tracker, Finance Tracker")
    business.add("Business Analytics, Strategy Engine")

    safety = tree.add("[red]Safety[/red]")
    safety.add("Multi-layer guardrails")
    safety.add("Approval workflows")
    safety.add("Budget controls")
    safety.add("Audit logging")

    channels = tree.add("[blue]Channels[/blue]")
    channels.add("Slack, Discord, Telegram, Webhooks, Email")

    llm = tree.add("[white]LLM Providers[/white]")
    llm.add("Anthropic (Claude) - Cloud")
    llm.add("OpenAI (GPT-4) - Cloud")
    llm.add("Ollama (Llama3, Mistral) - Local / No API Key")

    console.print(tree)


@main.command()
@click.argument("goal")
@click.option("--budget", "-b", default=None, type=float, help="Budget limit in USD")
@click.option("--priority", "-p", default=5, type=int, help="Task priority (1-10)")
@click.option("--strategy", "-s", default=None, help="Execution strategy: sequential, parallel, map_reduce")
@click.option("--config", "-c", default=None, help="Path to config file")
def orchestrate(
    goal: str,
    budget: float | None,
    priority: int,
    strategy: str | None,
    config: str | None,
) -> None:
    """Execute a goal using multi-agent orchestration.

    Decomposes the goal into sub-tasks and delegates to specialized agents
    (Researcher, Coder, Marketer, Analyst, Outreach, Operator) that
    collaborate via shared memory.

    Examples:
        sovereign orchestrate "Research competitors and create a marketing plan"
        sovereign orchestrate "Build a landing page and find 50 leads" --budget 10.0
        sovereign orchestrate "Analyze our revenue data" --strategy parallel
    """
    cfg = get_config(config)

    console.print(
        Panel(
            f"[bold]Goal:[/bold] {goal}\n"
            f"[bold]Budget:[/bold] ${budget:.2f if budget else 'unlimited'}\n"
            f"[bold]Priority:[/bold] {priority}\n"
            f"[bold]Strategy:[/bold] {strategy or 'auto (LLM decides)'}\n"
            f"[bold]Mode:[/bold] Multi-Agent Orchestration",
            title="[cyan]Orchestrator[/cyan]",
            border_style="cyan",
        )
    )

    async def _orchestrate() -> None:
        from sovereign.agents import (
            AnalystAgent,
            CoderAgent,
            DirectorAgent,
            MarketerAgent,
            OperatorAgent,
            OutreachAgent,
            ResearcherAgent,
        )
        from sovereign.core.orchestrator import Orchestrator
        from sovereign.llm.router import ModelRouter

        # Set up streaming callback for real-time output
        def stream_callback(message: str) -> None:
            if message.startswith("[ORCHESTRATOR]"):
                console.print(f"[bold cyan]{message}[/bold cyan]")
            elif message.startswith("[DELEGATE"):
                console.print(f"[bold magenta]{message}[/bold magenta]")
            elif "[REASSIGN]" in message:
                console.print(f"[bold yellow]{message}[/bold yellow]")
            elif "[OK]" in message:
                console.print(f"[green]{message}[/green]")
            elif "[FAILED]" in message:
                console.print(f"[red]{message}[/red]")
            elif "[WARN]" in message:
                console.print(f"[yellow]{message}[/yellow]")
            elif message.startswith("[PLAN]"):
                console.print(f"[bold cyan]{message}[/bold cyan]")
            elif message.startswith("[STEP"):
                console.print(f"[bold yellow]{message}[/bold yellow]")
            elif message.startswith("  -> OK:"):
                console.print(f"[green]{message}[/green]")
            elif message.startswith("  -> FAILED:"):
                console.print(f"[red]{message}[/red]")
            elif "[REFLECT]" in message:
                console.print(f"[dim]{message}[/dim]")
            elif "[REPLAN]" in message:
                console.print(f"[bold magenta]{message}[/bold magenta]")
            elif "[ABORT]" in message:
                console.print(f"[bold red]{message}[/bold red]")
            else:
                console.print(message)

        # Create orchestrator
        orchestrator = Orchestrator(cfg)
        orchestrator.set_stream_callback(stream_callback)

        # Wire LLM router for intelligent decomposition
        llm_router = ModelRouter(cfg)
        orchestrator.set_llm_router(llm_router)

        # Register all specialized agents
        agents = [
            DirectorAgent(cfg),
            ResearcherAgent(cfg),
            CoderAgent(cfg),
            MarketerAgent(cfg),
            AnalystAgent(cfg),
            OutreachAgent(cfg),
            OperatorAgent(cfg),
        ]
        for agent_instance in agents:
            agent_instance.set_stream_callback(stream_callback)
            orchestrator.register_agent(agent_instance)

        console.print(
            f"[dim]Registered {len(agents)} specialized agents[/dim]"
        )

        # Execute the goal
        result = await orchestrator.execute_goal(
            goal=goal,
            budget_usd=budget,
            priority=priority,
        )

        # Save lesson to self-improvement memory
        from sovereign.core.self_improve import record_outcome
        record_outcome(
            goal=goal,
            success=result.success,
            output=result.output or "",
            error=result.error,
            steps_executed=result.metadata.get("total_sub_tasks", 0),
        )

        if result.success:
            console.print(
                Panel(
                    f"[green]{result.output or 'Goal completed successfully'}[/green]",
                    title="[green]Orchestration Complete[/green]",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[red]{result.error or 'Orchestration failed'}[/red]",
                    title="[red]Orchestration Failed[/red]",
                    border_style="red",
                )
            )

        # Print orchestrator state
        state = orchestrator.get_state()
        console.print(
            f"\n[dim]Tasks completed: {state.total_tasks_completed} | "
            f"Failed: {state.total_tasks_failed} | "
            f"Messages: {state.messages_exchanged} | "
            f"Shared memory entries: {len(orchestrator.shared_memory.entries)}[/dim]"
        )

    asyncio.run(_orchestrate())


@main.command()
@click.option("--config", "-c", default=None, help="Path to config file")
def init(config: str | None) -> None:
    """Initialize a new Sovereign workspace."""
    cfg = get_config(config)
    cfg.ensure_dirs()

    console.print(
        Panel(
            f"[green]Sovereign workspace initialized![/green]\n\n"
            f"Data directory: [cyan]{cfg.data_dir}[/cyan]\n"
            f"Config loaded with defaults.\n\n"
            f"[dim]Set API keys as environment variables:[/dim]\n"
            f"  SOVEREIGN_LLM__MODELS__GPT4__API_KEY=sk-...\n"
            f"  SOVEREIGN_LLM__MODELS__CLAUDE__API_KEY=sk-ant-...\n\n"
            f"[dim]Get started:[/dim]\n"
            f'  sovereign run "Your goal here"',
            title="[cyan]Initialization Complete[/cyan]",
            border_style="green",
        )
    )


@main.command()
def version() -> None:
    """Show the Sovereign version."""
    console.print(f"[bold cyan]Sovereign[/bold cyan] v{__version__}")
    console.print("[dim]Autonomous AI Agent Platform for Business Automation[/dim]")


@main.command()
@click.option("--host", "-h", default="0.0.0.0", help="Bind host")
@click.option("--port", "-p", default=8000, type=int, help="Bind port")
def serve(host: str, port: int) -> None:
    """Start the Sovereign Web UI (FastAPI server).

    Launches a local web server with the dashboard, REST API,
    task queue management, and design engine.

    Examples:
        sovereign serve
        sovereign serve --port 9000
    """
    try:
        import uvicorn  # type: ignore[import-untyped]
    except ImportError:
        console.print(
            "[red]uvicorn is required: pip install uvicorn[/red]"
        )
        return

    from sovereign.web.api import create_app

    console.print(
        Panel(
            f"[bold cyan]Sovereign Web UI[/bold cyan]\n\n"
            f"Dashboard: [green]http://{host}:{port}/dashboard[/green]\n"
            f"API Docs:  [green]http://{host}:{port}/docs[/green]\n"
            f"Health:    [green]http://{host}:{port}/health[/green]",
            title="Starting Server",
            border_style="cyan",
        )
    )

    app = create_app()
    uvicorn.run(app, host=host, port=port)


@main.command(name="queue")
@click.option("--status", "-s", default=None, help="Filter by status")
@click.option("--limit", "-l", default=20, type=int, help="Max items")
def queue_list(status: str | None, limit: int) -> None:
    """Show the persistent task queue."""
    from sovereign.core.task_queue import TaskQueue, TaskStatus

    tq = TaskQueue()
    task_status = TaskStatus(status) if status else None
    tasks = tq.list_tasks(status=task_status, limit=limit)

    if not tasks:
        console.print("[dim]No tasks in queue.[/dim]")
        return

    table = Table(title="Task Queue", show_header=True)
    table.add_column("ID", style="dim", width=8)
    table.add_column("Goal", style="white")
    table.add_column("Status", width=12)
    table.add_column("Priority", width=8, justify="center")
    table.add_column("Created", style="dim", width=20)

    status_style = {
        "pending": "yellow",
        "in_progress": "cyan",
        "completed": "green",
        "failed": "red",
        "cancelled": "dim",
    }

    for t in tasks:
        style = status_style.get(t.status.value, "white")
        table.add_row(
            t.id[:8],
            t.goal[:60],
            f"[{style}]{t.status.value}[/{style}]",
            str(t.priority),
            t.created_at[:19] if t.created_at else "",
        )

    console.print(table)

    stats = tq.get_stats()
    console.print(
        f"\n[dim]Total: {stats.get('total', 0)} | "
        f"Pending: {stats.get('pending', 0)} | "
        f"Running: {stats.get('in_progress', 0)} | "
        f"Done: {stats.get('completed', 0)} | "
        f"Failed: {stats.get('failed', 0)}[/dim]"
    )


@main.command()
@click.argument("action", type=click.Choice(["start", "stop", "status"]))
@click.option("--detach", "-d", is_flag=True, help="Run daemon in background")
@click.option("--interval", "-i", default=None, type=int, help="Heartbeat interval in seconds")
def daemon(action: str, detach: bool, interval: int | None) -> None:
    """Manage the Sovereign heartbeat daemon.

    The daemon runs 24/7, checks for pending tasks in the queue,
    executes them autonomously, and sends notifications when done.

    Examples:
        sovereign daemon start           # Start in foreground
        sovereign daemon start --detach  # Start in background
        sovereign daemon stop            # Stop the daemon
        sovereign daemon status          # Check if running
    """
    from sovereign.core.daemon import HeartbeatDaemon, daemonize

    cfg = get_config()

    if action == "start":
        if HeartbeatDaemon.is_running(cfg.data_dir):
            pid = HeartbeatDaemon.get_pid(cfg.data_dir)
            console.print(f"[yellow]Daemon already running (PID {pid})[/yellow]")
            return

        console.print(
            Panel(
                f"[bold cyan]Starting Sovereign Daemon[/bold cyan]\n\n"
                f"Heartbeat interval: {interval or cfg.scheduler.heartbeat_interval_seconds}s\n"
                f"Mode: {'background' if detach else 'foreground'}\n"
                f"PID file: {cfg.data_dir}/daemon.pid\n"
                f"Log file: {cfg.data_dir}/daemon.log",
                title="Daemon",
                border_style="cyan",
            )
        )

        if detach:
            daemonize()
        else:
            d = HeartbeatDaemon(config=cfg, interval_seconds=interval)
            d.start()

    elif action == "stop":
        d = HeartbeatDaemon(config=cfg)
        if d.stop():
            console.print("[green]Daemon stopped.[/green]")
        else:
            console.print("[yellow]Daemon is not running.[/yellow]")

    elif action == "status":
        if HeartbeatDaemon.is_running(cfg.data_dir):
            state = HeartbeatDaemon.get_state(cfg.data_dir)
            pid = HeartbeatDaemon.get_pid(cfg.data_dir)
            console.print(
                Panel(
                    f"[green]Daemon is RUNNING[/green]\n\n"
                    f"PID: {pid}\n"
                    f"Started: {state.get('started_at', '?')}\n"
                    f"Heartbeats: {state.get('heartbeat_count', 0)}\n"
                    f"Tasks processed: {state.get('tasks_processed', 0)}\n"
                    f"Interval: {state.get('interval_seconds', '?')}s\n"
                    f"Last heartbeat: {state.get('last_heartbeat', '?')}",
                    title="Daemon Status",
                    border_style="green",
                )
            )
        else:
            console.print("[dim]Daemon is not running.[/dim]")


@main.command(name="skills")
@click.option("--tag", "-t", default=None, help="Filter by tag")
@click.option("--search", "-s", default=None, help="Search skills")
def skills_list(tag: str | None, search: str | None) -> None:
    """List available skills (portable YAML workflows).

    Skills are reusable workflows that can be shared and extended.
    Drop .yaml files into ~/.sovereign/skills/ to add your own.

    Examples:
        sovereign skills
        sovereign skills --tag business
        sovereign skills --search "landing page"
    """
    from sovereign.core.skills import SkillRegistry

    registry = SkillRegistry()

    if search:
        skill_list = registry.search(search)
    elif tag:
        skill_list = registry.list_skills(tags=[tag])
    else:
        skill_list = registry.list_skills()

    if not skill_list:
        console.print("[dim]No skills found.[/dim]")
        return

    table = Table(title="Available Skills", show_header=True)
    table.add_column("Name", style="cyan", width=20)
    table.add_column("Description", style="white")
    table.add_column("Tags", style="yellow", width=20)
    table.add_column("Steps", width=6, justify="center")

    for skill in skill_list:
        table.add_row(
            skill.name,
            skill.description[:60],
            ", ".join(skill.tags),
            str(len(skill.steps)),
        )

    console.print(table)
    console.print(
        "\n[dim]Skills directory: ~/.sovereign/skills/[/dim]\n"
        "[dim]Add custom skills by dropping .yaml files there.[/dim]"
    )


@main.command(name="memory")
@click.option("--type", "-t", "mem_type", default="semantic", help="Memory type")
@click.option("--search", "-s", default=None, help="Search memories")
@click.option("--limit", "-l", default=20, type=int, help="Max results")
def memory_cmd(mem_type: str, search: str | None, limit: int) -> None:
    """Browse and search persistent memory.

    Memories are stored as Markdown files in ~/.sovereign/memory/
    and survive restarts. Types: episodic, semantic, procedures.

    Examples:
        sovereign memory
        sovereign memory --type episodic
        sovereign memory --search "competitor analysis"
    """
    from sovereign.memory.persistent import PersistentMemory

    mem = PersistentMemory()

    if search:
        results = mem.search(search, memory_types=[mem_type], max_results=limit)
        if not results:
            console.print(f"[dim]No memories found for '{search}'[/dim]")
            return

        table = Table(title=f"Memory Search: '{search}'", show_header=True)
        table.add_column("Type", style="yellow", width=12)
        table.add_column("Title", style="cyan")
        table.add_column("Score", width=6, justify="right")
        table.add_column("Preview", style="dim")

        for r in results:
            table.add_row(
                r["type"],
                r["header"].get("title", "Untitled")[:40],
                f"{r['score']:.2f}",
                r["content"][:60].replace("\n", " "),
            )

        console.print(table)
    else:
        memories = mem.list_memories(memory_type=mem_type, limit=limit)
        if not memories:
            console.print(f"[dim]No {mem_type} memories found.[/dim]")
            return

        table = Table(title=f"{mem_type.title()} Memories", show_header=True)
        table.add_column("File", style="dim", width=30)
        table.add_column("Title", style="cyan")
        table.add_column("Preview", style="white")

        for m in memories:
            table.add_row(
                m["filename"][:30],
                m["header"].get("title", "Untitled")[:40],
                m["preview"][:50].replace("\n", " "),
            )

        console.print(table)

    console.print(
        f"\n[dim]Memory directory: ~/.sovereign/memory/{mem_type}/[/dim]"
    )


@main.command(name="notifications")
@click.option("--limit", "-l", default=20, type=int, help="Max notifications")
@click.option("--unread", "-u", is_flag=True, help="Show only unread")
def notifications_cmd(limit: int, unread: bool) -> None:
    """Show recent notifications from daemon and task completions.

    Examples:
        sovereign notifications
        sovereign notifications --unread
    """
    from sovereign.core.notifier import Notifier

    cfg = get_config()
    notifier = Notifier(cfg)

    if unread:
        items = notifier.get_unread()
    else:
        items = notifier.get_recent(count=limit)

    if not items:
        console.print("[dim]No notifications.[/dim]")
        return

    for item in reversed(items):
        level = item.get("level", "info")
        color = {"info": "cyan", "error": "red", "warning": "yellow"}.get(level, "white")
        read_marker = "" if item.get("read") else " [bold yellow]*[/bold yellow]"
        console.print(
            f"[{color}]{item.get('title', 'Notification')}[/{color}]{read_marker}\n"
            f"  [dim]{item.get('timestamp', '')[:19]}[/dim]\n"
            f"  {item.get('body', '')[:120]}\n"
        )


if __name__ == "__main__":
    main()
