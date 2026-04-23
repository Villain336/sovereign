"""API Client Tool - make HTTP requests to REST and GraphQL APIs.

Enables the agent to interact with any web API for data retrieval,
service integration, and automation.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class APIClientTool(Tool):
    """Make HTTP requests to REST APIs."""

    name = "api_request"
    description = (
        "Make HTTP requests to REST APIs. Supports GET, POST, PUT, PATCH, DELETE. "
        "Use this to interact with external services, fetch data, or trigger webhooks."
    )
    parameters = [
        ToolParameter(
            name="url",
            description="The URL to send the request to",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="method",
            description="HTTP method: GET, POST, PUT, PATCH, DELETE",
            param_type="string",
            required=False,
            default="GET",
            enum=["GET", "POST", "PUT", "PATCH", "DELETE"],
        ),
        ToolParameter(
            name="headers",
            description="Request headers as JSON object",
            param_type="dict",
            required=False,
        ),
        ToolParameter(
            name="body",
            description="Request body (for POST/PUT/PATCH)",
            param_type="dict",
            required=False,
        ),
        ToolParameter(
            name="params",
            description="Query parameters as JSON object",
            param_type="dict",
            required=False,
        ),
        ToolParameter(
            name="timeout",
            description="Request timeout in seconds (default 30)",
            param_type="integer",
            required=False,
            default=30,
        ),
    ]
    category = "api"
    risk_level = 0.3

    async def execute(self, **kwargs: Any) -> ToolResult:
        url = kwargs.get("url", "")
        method = kwargs.get("method", "GET").upper()
        headers = kwargs.get("headers") or {}
        body = kwargs.get("body")
        params = kwargs.get("params")
        timeout = kwargs.get("timeout", 30)

        if not url:
            return ToolResult(success=False, error="URL is required")

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                request_kwargs: dict[str, Any] = {
                    "method": method,
                    "url": url,
                    "headers": headers,
                }

                if params:
                    request_kwargs["params"] = params

                if body and method in ("POST", "PUT", "PATCH"):
                    request_kwargs["json"] = body

                response = await client.request(**request_kwargs)

                # Try to parse as JSON
                try:
                    response_data = response.json()
                    output = json.dumps(response_data, indent=2)
                except (json.JSONDecodeError, ValueError):
                    output = response.text

                success = 200 <= response.status_code < 400

                return ToolResult(
                    success=success,
                    output=output,
                    error=None if success else f"HTTP {response.status_code}",
                    metadata={
                        "status_code": response.status_code,
                        "url": url,
                        "method": method,
                        "response_headers": dict(response.headers),
                    },
                )

        except httpx.TimeoutException:
            return ToolResult(
                success=False,
                error=f"Request timed out after {timeout}s",
                metadata={"url": url, "method": method},
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Request failed: {str(e)}",
                metadata={"url": url, "method": method},
            )
