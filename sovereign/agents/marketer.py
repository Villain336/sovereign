"""Marketer Agent - specialized for content creation and marketing.

Handles content strategy, copywriting, SEO, social media,
and brand management tasks.
"""

from __future__ import annotations

from sovereign.config import SovereignConfig
from sovereign.core.agent import Agent, AgentCapability, AgentRole


class MarketerAgent(Agent):
    """Agent specialized in marketing and content creation.

    Capabilities:
    - Content creation (blog posts, social media, emails)
    - SEO optimization
    - Social media management
    - Brand voice and messaging
    - Campaign planning
    """

    def __init__(self, config: SovereignConfig) -> None:
        capabilities = [
            AgentCapability(
                name="content_creation",
                description="Create blog posts, articles, and marketing copy",
                tool_names=["web_search", "file_write"],
                complexity_range=(0.2, 0.7),
            ),
            AgentCapability(
                name="seo_optimization",
                description="Optimize content for search engines",
                tool_names=["web_search", "browser"],
                complexity_range=(0.3, 0.7),
            ),
            AgentCapability(
                name="social_media",
                description="Create and manage social media content",
                tool_names=["api_request", "web_search"],
                complexity_range=(0.2, 0.5),
            ),
            AgentCapability(
                name="email_marketing",
                description="Create email campaigns and newsletters",
                tool_names=["email_send", "file_write"],
                complexity_range=(0.3, 0.6),
            ),
            AgentCapability(
                name="market_research",
                description="Research market trends and competitor strategies",
                tool_names=["web_search", "browser"],
                complexity_range=(0.4, 0.8),
            ),
        ]

        super().__init__(
            config=config,
            role=AgentRole.MARKETER,
            name="Marketer",
            capabilities=capabilities,
        )
