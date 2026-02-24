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


if __name__ == "__main__":
    main()
