"""Configuration management for Sovereign.

Supports environment variables, .env files, and YAML config files.
All settings use pydantic-settings for validation and type safety.
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LLMProviderType(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LLMModelConfig(BaseModel):
    """Configuration for a single LLM model."""

    provider: LLMProviderType
    model_name: str
    api_key: str = ""
    base_url: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    capabilities: list[str] = Field(default_factory=lambda: ["general"])
    max_context_window: int = 128000


class ModelRouterConfig(BaseModel):
    """Configuration for the smart model router."""

    default_model: str = "gpt-4o"
    models: dict[str, LLMModelConfig] = Field(default_factory=dict)
    complexity_threshold_high: float = 0.7
    complexity_threshold_low: float = 0.3
    cost_optimization: bool = True


class MemoryConfig(BaseModel):
    """Configuration for the memory system."""

    working_memory_max_tokens: int = 16000
    episodic_memory_max_episodes: int = 1000
    vector_store_collection: str = "sovereign_memory"
    vector_store_path: str = str(Path.home() / ".sovereign" / "vector_store")
    knowledge_graph_path: str = str(Path.home() / ".sovereign" / "knowledge_graph.json")
    procedural_memory_path: str = str(Path.home() / ".sovereign" / "procedures")


class SafetyConfig(BaseModel):
    """Configuration for safety guardrails."""

    require_approval_above_risk: int = 7
    max_budget_per_task_usd: float = 50.0
    max_budget_per_day_usd: float = 500.0
    max_concurrent_actions: int = 5
    sandbox_enabled: bool = True
    kill_switch_enabled: bool = True
    blocked_domains: list[str] = Field(default_factory=list)
    blocked_commands: list[str] = Field(
        default_factory=lambda: ["rm -rf /", "mkfs", "dd if=", ":(){ :|:& };:"]
    )
    audit_log_path: str = str(Path.home() / ".sovereign" / "audit.log")


class SchedulerConfig(BaseModel):
    """Configuration for the task scheduler."""

    heartbeat_interval_seconds: int = 300
    max_concurrent_tasks: int = 10
    task_timeout_seconds: int = 3600
    queue_persistence_path: str = str(Path.home() / ".sovereign" / "task_queue.json")


class ChannelConfig(BaseModel):
    """Configuration for communication channels."""

    slack_bot_token: str = ""
    slack_app_token: str = ""
    discord_bot_token: str = ""
    telegram_bot_token: str = ""
    email_smtp_host: str = ""
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    webhook_secret: str = ""


class SovereignConfig(BaseSettings):
    """Main configuration for the Sovereign platform."""

    model_config = {"env_prefix": "SOVEREIGN_", "env_nested_delimiter": "__"}

    app_name: str = "Sovereign"
    log_level: LogLevel = LogLevel.INFO
    data_dir: str = str(Path.home() / ".sovereign")

    llm: ModelRouterConfig = Field(default_factory=ModelRouterConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)
    channels: ChannelConfig = Field(default_factory=ChannelConfig)

    def ensure_dirs(self) -> None:
        """Create necessary directories."""
        dirs = [
            self.data_dir,
            self.memory.vector_store_path,
            self.memory.procedural_memory_path,
            os.path.dirname(self.memory.knowledge_graph_path),
            os.path.dirname(self.safety.audit_log_path),
            os.path.dirname(self.scheduler.queue_persistence_path),
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)


def load_config(**overrides: Any) -> SovereignConfig:
    """Load configuration from environment and optional overrides.

    Automatically detects API keys from environment variables and
    configures default models.
    """
    config = SovereignConfig(**overrides)

    # Auto-configure Anthropic if API key is in environment
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if anthropic_key and "claude" not in config.llm.models:
        config.llm.models["claude"] = LLMModelConfig(
            provider=LLMProviderType.ANTHROPIC,
            model_name="claude-sonnet-4-20250514",
            api_key=anthropic_key,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_input=0.003,
            cost_per_1k_output=0.015,
            capabilities=["general", "coding", "analysis", "creative", "planning"],
            max_context_window=200000,
        )
        config.llm.default_model = "claude"

    # Auto-configure OpenAI if API key is in environment
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if openai_key and "gpt4" not in config.llm.models:
        config.llm.models["gpt4"] = LLMModelConfig(
            provider=LLMProviderType.OPENAI,
            model_name="gpt-4o",
            api_key=openai_key,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_input=0.005,
            cost_per_1k_output=0.015,
            capabilities=["general", "coding", "analysis", "creative", "planning"],
            max_context_window=128000,
        )
        if not anthropic_key:
            config.llm.default_model = "gpt4"

    config.ensure_dirs()
    return config
