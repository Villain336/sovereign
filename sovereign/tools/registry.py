"""Tool Registry - discovers, registers, and manages all available tools.

Provides capability-based tool discovery so agents can find the right
tool for any task, and the LLM can be given only relevant tool definitions.
"""

from __future__ import annotations

from typing import Any

from sovereign.tools.base import Tool, ToolResult


class ToolRegistry:
    """Central registry for all available tools.

    Features:
    - Register/unregister tools dynamically
    - Capability-based discovery (find tools by category or keyword)
    - Tool execution with validation
    - Usage tracking for analytics
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._usage_counts: dict[str, int] = {}
        self._category_index: dict[str, list[str]] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        self._usage_counts[tool.name] = 0

        category = tool.category
        if category not in self._category_index:
            self._category_index[category] = []
        if tool.name not in self._category_index[category]:
            self._category_index[category].append(tool.name)

    def unregister(self, tool_name: str) -> bool:
        """Unregister a tool."""
        tool = self._tools.pop(tool_name, None)
        if tool:
            self._usage_counts.pop(tool_name, None)
            cat_tools = self._category_index.get(tool.category, [])
            if tool_name in cat_tools:
                cat_tools.remove(tool_name)
            return True
        return False

    def get(self, tool_name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(tool_name)

    async def execute(self, tool_name: str, **kwargs: Any) -> ToolResult:
        """Execute a tool by name with arguments."""
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool not found: {tool_name}",
            )

        # Validate arguments
        errors = tool.validate_args(**kwargs)
        if errors:
            return ToolResult(
                success=False,
                error=f"Validation errors: {'; '.join(errors)}",
            )

        try:
            result = await tool.execute(**kwargs)
            self._usage_counts[tool_name] = self._usage_counts.get(tool_name, 0) + 1
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Tool execution error: {str(e)}",
            )

    def find_by_category(self, category: str) -> list[Tool]:
        """Find tools by category."""
        tool_names = self._category_index.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]

    def find_by_capability(self, query: str) -> list[Tool]:
        """Find tools matching a capability query (keyword search)."""
        query_lower = query.lower()
        results: list[Tool] = []

        for tool in self._tools.values():
            # Search in name, description, and category
            searchable = f"{tool.name} {tool.description} {tool.category}".lower()
            if query_lower in searchable:
                results.append(tool)

        return results

    def get_all_schemas(self) -> list[dict[str, Any]]:
        """Get LLM-compatible schemas for all tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.to_llm_schema(),
            }
            for tool in self._tools.values()
        ]

    def get_schemas_for_categories(self, categories: list[str]) -> list[dict[str, Any]]:
        """Get schemas for tools in specific categories only."""
        schemas: list[dict[str, Any]] = []
        for category in categories:
            tools = self.find_by_category(category)
            for tool in tools:
                schemas.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.to_llm_schema(),
                })
        return schemas

    def get_usage_stats(self) -> dict[str, int]:
        """Get usage statistics for all tools."""
        return dict(self._usage_counts)

    @property
    def tool_count(self) -> int:
        return len(self._tools)

    @property
    def categories(self) -> list[str]:
        return list(self._category_index.keys())

    def list_tools(self) -> list[dict[str, str]]:
        """List all registered tools with basic info."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "risk_level": str(tool.risk_level),
            }
            for tool in self._tools.values()
        ]
