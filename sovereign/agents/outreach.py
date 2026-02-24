"""Outreach Agent - specialized for communication and relationship building.

Handles email outreach, lead nurturing, customer communication,
and partnership development.
"""

from __future__ import annotations

from sovereign.config import SovereignConfig
from sovereign.core.agent import Agent, AgentCapability, AgentRole


class OutreachAgent(Agent):
    """Agent specialized in outreach and communication.

    Capabilities:
    - Email outreach campaigns
    - Lead nurturing sequences
    - Customer communication
    - Partnership outreach
    - Follow-up management
    """

    def __init__(self, config: SovereignConfig) -> None:
        capabilities = [
            AgentCapability(
                name="email_outreach",
                description="Send personalized outreach emails",
                tool_names=["email_send", "web_search"],
                complexity_range=(0.2, 0.6),
            ),
            AgentCapability(
                name="lead_nurturing",
                description="Nurture leads through automated sequences",
                tool_names=["email_send", "database_query"],
                complexity_range=(0.3, 0.7),
            ),
            AgentCapability(
                name="social_outreach",
                description="Engage with prospects on social platforms",
                tool_names=["api_request", "browser"],
                complexity_range=(0.3, 0.6),
            ),
            AgentCapability(
                name="follow_up",
                description="Manage and execute follow-up communications",
                tool_names=["email_send", "database_query"],
                complexity_range=(0.2, 0.5),
            ),
        ]

        super().__init__(
            config=config,
            role=AgentRole.OUTREACH,
            name="Outreach",
            capabilities=capabilities,
        )
