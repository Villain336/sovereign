"""Sovereign platform configuration."""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Sovereign"
    app_version: str = "0.1.0"
    debug: bool = False

    # LLM Configuration
    anthropic_api_key: Optional[str] = None
    llm_model: str = "claude-sonnet-4-20250514"
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.1

    # Agent Configuration
    agent_max_iterations: int = 10
    agent_confidence_threshold: float = 0.85
    hitl_risk_threshold: float = 0.7  # Above this, require human approval

    # Audit Configuration
    audit_hash_algorithm: str = "sha256"

    # Database (in-memory for MVP)
    database_url: str = "sqlite:///sovereign.db"

    class Config:
        env_file = ".env"
        env_prefix = "SOVEREIGN_"


settings = Settings()
