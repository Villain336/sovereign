"""Base Tool interface - all tools inherit from this.

Tools are the agent's hands - they perform concrete actions in the world.
Each tool has a clear interface: name, description, parameters, and execute().
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Definition of a tool parameter."""

    name: str
    description: str
    param_type: str = "string"  # string, int, float, bool, list, dict
    required: bool = True
    default: Any = None
    enum: list[str] | None = None


class ToolResult(BaseModel):
    """Result returned by a tool execution."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def __str__(self) -> str:
        if self.success:
            return str(self.output) if self.output else "Success"
        return f"Error: {self.error or 'Unknown error'}"


class Tool(ABC):
    """Abstract base class for all tools.

    Every tool must define:
    - name: Unique identifier
    - description: What the tool does (used by the LLM to decide when to use it)
    - parameters: What inputs the tool accepts
    - execute(): The actual execution logic
    """

    name: str = ""
    description: str = ""
    parameters: list[ToolParameter] = []
    category: str = "general"
    risk_level: float = 0.1  # 0-1, used by safety system
    requires_approval: bool = False

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with the given arguments."""
        ...

    def validate_args(self, **kwargs: Any) -> list[str]:
        """Validate that required parameters are provided."""
        errors: list[str] = []
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                if param.default is None:
                    errors.append(f"Missing required parameter: {param.name}")
        return errors

    def to_llm_schema(self) -> dict[str, Any]:
        """Convert tool definition to LLM-compatible function schema."""
        properties: dict[str, Any] = {}
        required: list[str] = []

        for param in self.parameters:
            prop: dict[str, Any] = {
                "type": param.param_type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            if param.default is not None:
                prop["default"] = param.default

            properties[param.name] = prop
            if param.required:
                required.append(param.name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }
