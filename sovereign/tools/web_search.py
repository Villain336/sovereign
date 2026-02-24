"""Web Search Tool - search the web using multiple search engines.

Supports multiple search backends and aggregates results.
"""

from __future__ import annotations

from typing import Any

import httpx

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class WebSearchTool(Tool):
    """Search the web and return relevant results."""

    name = "web_search"
    description = (
        "Search the web for information. Returns relevant web pages with titles, "
        "URLs, and snippets. Use this to research topics, find documentation, "
        "or gather market intelligence."
    )
    parameters = [
        ToolParameter(
            name="query",
            description="The search query string",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="num_results",
            description="Number of results to return (default 5)",
            param_type="integer",
            required=False,
            default=5,
        ),
        ToolParameter(
            name="search_type",
            description="Type of search: general, news, academic",
            param_type="string",
            required=False,
            default="general",
            enum=["general", "news", "academic"],
        ),
    ]
    category = "search"
    risk_level = 0.1

    def __init__(self, api_key: str = "", search_engine: str = "serper") -> None:
        self._api_key = api_key
        self._search_engine = search_engine

    async def execute(self, **kwargs: Any) -> ToolResult:
        query = kwargs.get("query", "")
        num_results = kwargs.get("num_results", 5)
        search_type = kwargs.get("search_type", "general")

        if not query:
            return ToolResult(success=False, error="Query is required")

        try:
            if self._search_engine == "serper" and self._api_key:
                results = await self._search_serper(query, num_results, search_type)
            else:
                results = await self._search_duckduckgo(query, num_results)

            if not results:
                return ToolResult(
                    success=True,
                    output="No results found.",
                    metadata={"query": query, "result_count": 0},
                )

            formatted = self._format_results(results)
            return ToolResult(
                success=True,
                output=formatted,
                metadata={"query": query, "result_count": len(results)},
            )

        except Exception as e:
            return ToolResult(success=False, error=f"Search failed: {str(e)}")

    async def _search_serper(
        self, query: str, num_results: int, search_type: str
    ) -> list[dict[str, str]]:
        """Search using Serper API (Google Search)."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self._api_key, "Content-Type": "application/json"},
                json={"q": query, "num": num_results},
            )
            response.raise_for_status()
            data = response.json()

        results: list[dict[str, str]] = []
        for item in data.get("organic", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            })
        return results

    async def _search_duckduckgo(
        self, query: str, num_results: int
    ) -> list[dict[str, str]]:
        """Fallback search using DuckDuckGo HTML (no API key needed)."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "Sovereign/0.1"},
            )

        # Parse simple results from HTML (basic extraction)
        results: list[dict[str, str]] = []
        text = response.text

        # Simple extraction of result links and snippets
        import re

        links = re.findall(r'class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', text)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', text, re.DOTALL)

        for i, (url, title) in enumerate(links[:num_results]):
            snippet = snippets[i] if i < len(snippets) else ""
            # Clean HTML from snippet
            snippet = re.sub(r"<[^>]+>", "", snippet).strip()
            results.append({
                "title": title.strip(),
                "url": url,
                "snippet": snippet,
            })

        return results

    def _format_results(self, results: list[dict[str, str]]) -> str:
        """Format search results as readable text."""
        parts: list[str] = []
        for i, result in enumerate(results, 1):
            parts.append(
                f"{i}. **{result['title']}**\n"
                f"   URL: {result['url']}\n"
                f"   {result['snippet']}"
            )
        return "\n\n".join(parts)
