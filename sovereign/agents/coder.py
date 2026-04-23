"""Coder Agent - specialized for software development tasks.

Handles code writing, debugging, testing, deployment, and
technical architecture decisions.
"""

from __future__ import annotations

from sovereign.config import SovereignConfig
from sovereign.core.agent import Agent, AgentCapability, AgentRole


class CoderAgent(Agent):
    """Agent specialized in software development.

    Capabilities:
    - Code generation and editing
    - Bug fixing and debugging
    - Testing and quality assurance
    - Deployment and DevOps
    - Architecture design
    """

    def __init__(self, config: SovereignConfig) -> None:
        capabilities = [
            AgentCapability(
                name="code_generation",
                description="Write code in any language based on requirements",
                tool_names=["code_executor", "file_write", "file_read", "shell"],
                complexity_range=(0.2, 0.9),
            ),
            AgentCapability(
                name="debugging",
                description="Find and fix bugs in code",
                tool_names=["code_executor", "file_read", "shell"],
                complexity_range=(0.3, 0.9),
            ),
            AgentCapability(
                name="testing",
                description="Write and run tests for code quality",
                tool_names=["code_executor", "shell", "file_write"],
                complexity_range=(0.2, 0.7),
            ),
            AgentCapability(
                name="deployment",
                description="Deploy applications and manage infrastructure",
                tool_names=["shell", "api_request", "file_write"],
                complexity_range=(0.4, 0.9),
            ),
            AgentCapability(
                name="code_review",
                description="Review code for quality, security, and best practices",
                tool_names=["file_read"],
                complexity_range=(0.3, 0.8),
            ),
        ]

        super().__init__(
            config=config,
            role=AgentRole.CODER,
            name="Coder",
            capabilities=capabilities,
        )
