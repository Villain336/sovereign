"""Operator Agent - specialized for deployment and operations.

Handles infrastructure, deployment, monitoring, and
operational tasks for running services.
"""

from __future__ import annotations

from sovereign.config import SovereignConfig
from sovereign.core.agent import Agent, AgentCapability, AgentRole


class OperatorAgent(Agent):
    """Agent specialized in operations and deployment.

    Capabilities:
    - Service deployment
    - Infrastructure management
    - Monitoring and alerting
    - CI/CD pipeline management
    - System administration
    """

    def __init__(self, config: SovereignConfig) -> None:
        capabilities = [
            AgentCapability(
                name="deployment",
                description="Deploy and manage applications and services",
                tool_names=["shell", "file_write", "api_request"],
                complexity_range=(0.4, 0.9),
            ),
            AgentCapability(
                name="infrastructure",
                description="Manage servers, databases, and cloud resources",
                tool_names=["shell", "api_request"],
                complexity_range=(0.5, 0.9),
            ),
            AgentCapability(
                name="monitoring",
                description="Monitor service health and performance",
                tool_names=["shell", "api_request", "browser"],
                complexity_range=(0.3, 0.7),
            ),
            AgentCapability(
                name="automation",
                description="Create and manage automation scripts and pipelines",
                tool_names=["shell", "file_write", "code_executor"],
                complexity_range=(0.3, 0.8),
            ),
        ]

        super().__init__(
            config=config,
            role=AgentRole.OPERATOR,
            name="Operator",
            capabilities=capabilities,
        )
