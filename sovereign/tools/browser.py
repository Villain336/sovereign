"""Browser Tool - web browsing and scraping with headless browser.

Provides web browsing capabilities using HTTP-based scraping.
For full browser automation, integrates with Playwright when available.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin, urlparse

import httpx

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class BrowserTool(Tool):
    """Browse web pages and extract content."""

    name = "browser"
    description = (
        "Browse a web page and extract its text content. Use this for reading "
        "documentation, scraping data, checking websites, and gathering information "
        "from specific URLs."
    )
    parameters = [
        ToolParameter(
            name="url",
            description="URL of the page to browse",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="extract",
            description="What to extract: text, links, or all",
            param_type="string",
            required=False,
            default="text",
            enum=["text", "links", "all"],
        ),
        ToolParameter(
            name="selector",
            description="CSS selector to extract specific elements (optional)",
            param_type="string",
            required=False,
        ),
    ]
    category = "browser"
    risk_level = 0.2

    async def execute(self, **kwargs: Any) -> ToolResult:
        url = kwargs.get("url", "")
        extract = kwargs.get("extract", "text")

        if not url:
            return ToolResult(success=False, error="URL is required")

        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"https://{url}"

        try:
            async with httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers={"User-Agent": "Sovereign/0.1 (Autonomous Agent)"},
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "application/json" not in content_type:
                return ToolResult(
                    success=True,
                    output=f"Non-text content ({content_type}), size: {len(response.content)} bytes",
                    metadata={"url": url, "content_type": content_type},
                )

            html = response.text

            if extract == "text":
                text = self._extract_text(html)
                output = text[:10000]  # Limit output size
            elif extract == "links":
                links = self._extract_links(html, url)
                output = "\n".join(links[:100])
            else:
                text = self._extract_text(html)
                links = self._extract_links(html, url)
                output = f"=== TEXT ===\n{text[:8000]}\n\n=== LINKS ===\n" + "\n".join(
                    links[:50]
                )

            return ToolResult(
                success=True,
                output=output,
                metadata={
                    "url": url,
                    "status_code": response.status_code,
                    "content_type": content_type,
                },
            )

        except httpx.HTTPStatusError as e:
            return ToolResult(
                success=False,
                error=f"HTTP {e.response.status_code}: {url}",
                metadata={"url": url},
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Browse failed: {str(e)}",
                metadata={"url": url},
            )

    def _extract_text(self, html: str) -> str:
        """Extract readable text from HTML."""
        import re

        # Remove script and style elements
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", text)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        text = "\n".join(line.strip() for line in text.split("\n") if line.strip())

        # Decode HTML entities
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")
        text = text.replace("&nbsp;", " ")

        return text.strip()

    def _extract_links(self, html: str, base_url: str) -> list[str]:
        """Extract all links from HTML."""
        import re

        links: list[str] = []
        for match in re.finditer(r'href=["\']([^"\']+)["\']', html):
            href = match.group(1)
            if href.startswith("javascript:") or href.startswith("#"):
                continue
            absolute_url = urljoin(base_url, href)
            if absolute_url not in links:
                links.append(absolute_url)
        return links
