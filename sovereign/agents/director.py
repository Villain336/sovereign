"""Director Agent - the top-level agent that manages the whole operation.

The Director coordinates all specialized agents through the Orchestrator,
making high-level strategic decisions about goal decomposition, agent
assignment, and result synthesis.
"""

from __future__ import annotations

from sovereign.config import SovereignConfig
from sovereign.core.agent import Agent, AgentCapability, AgentRole


class DirectorAgent(Agent):
    """Agent specialized in directing and coordinating other agents.

    Capabilities:
    - Goal decomposition and strategic planning
    - Agent coordination and task delegation
    - Result synthesis and quality control
    - Resource allocation and budget management
    """

    def __init__(self, config: SovereignConfig) -> None:
        capabilities = [
            AgentCapability(
                name="strategic_planning",
                description="Break complex goals into actionable sub-tasks",
                tool_names=[],
                complexity_range=(0.5, 1.0),
            ),
            AgentCapability(
                name="agent_coordination",
                description="Coordinate specialized agents for multi-step tasks",
                tool_names=[],
                complexity_range=(0.4, 0.9),
            ),
            AgentCapability(
                name="result_synthesis",
                description="Synthesize outputs from multiple agents into cohesive deliverables",
                tool_names=[],
                complexity_range=(0.3, 0.8),
            ),
            AgentCapability(
                name="quality_control",
                description="Review and validate agent outputs for quality and completeness",
                tool_names=[],
                complexity_range=(0.2, 0.7),
            ),
        ]

        super().__init__(
            config=config,
            role=AgentRole.DIRECTOR,
            name="Director",
            capabilities=capabilities,
        )
