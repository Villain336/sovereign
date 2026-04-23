"""Researcher Agent - specialized for information gathering and analysis.

Capable of web research, data collection, competitive analysis,
and synthesizing findings into actionable intelligence.
"""

from __future__ import annotations

from sovereign.config import SovereignConfig
from sovereign.core.agent import Agent, AgentCapability, AgentRole


class ResearcherAgent(Agent):
    """Agent specialized in research and information gathering.

    Capabilities:
    - Web search and content extraction
    - Competitive analysis
    - Market research
    - Data collection and synthesis
    - Fact-checking and verification
    """

    def __init__(self, config: SovereignConfig) -> None:
        capabilities = [
            AgentCapability(
                name="web_research",
                description="Search the web and extract information from websites",
                tool_names=["web_search", "browser"],
                complexity_range=(0.1, 0.7),
            ),
            AgentCapability(
                name="data_collection",
                description="Collect and organize data from multiple sources",
                tool_names=["web_search", "browser", "api_request", "database_query"],
                complexity_range=(0.3, 0.8),
            ),
            AgentCapability(
                name="competitive_analysis",
                description="Analyze competitors, markets, and industry trends",
                tool_names=["web_search", "browser"],
                complexity_range=(0.4, 0.9),
            ),
            AgentCapability(
                name="fact_verification",
                description="Verify claims and cross-reference information",
                tool_names=["web_search", "browser"],
                complexity_range=(0.2, 0.6),
            ),
        ]

        super().__init__(
            config=config,
            role=AgentRole.RESEARCHER,
            name="Researcher",
            capabilities=capabilities,
        )
