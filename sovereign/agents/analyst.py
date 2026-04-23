"""Analyst Agent - specialized for data analysis and reporting.

Handles data analysis, metric tracking, report generation,
and insight extraction from business data.
"""

from __future__ import annotations

from sovereign.config import SovereignConfig
from sovereign.core.agent import Agent, AgentCapability, AgentRole


class AnalystAgent(Agent):
    """Agent specialized in data analysis and reporting.

    Capabilities:
    - Data analysis and visualization
    - Financial reporting
    - KPI tracking and dashboards
    - Trend analysis
    - Forecasting
    """

    def __init__(self, config: SovereignConfig) -> None:
        capabilities = [
            AgentCapability(
                name="data_analysis",
                description="Analyze data sets and extract insights",
                tool_names=["code_executor", "database_query", "file_read"],
                complexity_range=(0.3, 0.8),
            ),
            AgentCapability(
                name="reporting",
                description="Generate business reports and summaries",
                tool_names=["database_query", "file_write", "code_executor"],
                complexity_range=(0.3, 0.7),
            ),
            AgentCapability(
                name="financial_analysis",
                description="Analyze financial data, P&L, and budgets",
                tool_names=["database_query", "code_executor"],
                complexity_range=(0.4, 0.9),
            ),
            AgentCapability(
                name="forecasting",
                description="Generate forecasts and predictions from historical data",
                tool_names=["code_executor", "database_query"],
                complexity_range=(0.5, 0.9),
            ),
        ]

        super().__init__(
            config=config,
            role=AgentRole.ANALYST,
            name="Analyst",
            capabilities=capabilities,
        )
