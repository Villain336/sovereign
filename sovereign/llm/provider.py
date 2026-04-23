"""LLM Provider abstraction - unified interface for all model providers.

Supports OpenAI, Anthropic, and Ollama with a consistent API.
Tracks token usage and costs for budget management.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AsyncIterator

import httpx
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """A message in a conversation."""

    role: MessageRole
    content: str
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


class ToolDefinition(BaseModel):
    """Definition of a tool the LLM can call."""

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    """Response from an LLM provider."""

    content: str
    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_seconds: float = 0.0
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    finish_reason: str = ""
    raw_response: dict[str, Any] = Field(default_factory=dict)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        base_url: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        cost_per_1k_input: float = 0.0,
        cost_per_1k_output: float = 0.0,
    ) -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.cost_per_1k_input = cost_per_1k_input
        self.cost_per_1k_output = cost_per_1k_output
        self._client: httpx.AsyncClient | None = None
        self._total_tokens_used = 0
        self._total_cost_usd = 0.0

    @abstractmethod
    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate a response from the model."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Stream a response from the model."""
        ...

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate the cost of a request."""
        input_cost = (input_tokens / 1000) * self.cost_per_1k_input
        output_cost = (output_tokens / 1000) * self.cost_per_1k_output
        return input_cost + output_cost

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def total_tokens_used(self) -> int:
        return self._total_tokens_used

    @property
    def total_cost_usd(self) -> float:
        return self._total_cost_usd


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (GPT-4, GPT-4o, etc.)."""

    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        client = await self._get_client()
        start_time = time.time()

        url = self.base_url or "https://api.openai.com/v1"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": [self._format_message(m) for m in messages],
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
        }

        if tools:
            payload["tools"] = [self._format_tool(t) for t in tools]

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        response = await client.post(
            f"{url}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        cost = self.calculate_cost(input_tokens, output_tokens)
        self._total_tokens_used += input_tokens + output_tokens
        self._total_cost_usd += cost

        tool_calls = []
        if choice["message"].get("tool_calls"):
            for tc in choice["message"]["tool_calls"]:
                tool_calls.append({
                    "id": tc["id"],
                    "name": tc["function"]["name"],
                    "arguments": json.loads(tc["function"]["arguments"]),
                })

        return LLMResponse(
            content=choice["message"].get("content", ""),
            model=self.model_name,
            provider="openai",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=cost,
            latency_seconds=time.time() - start_time,
            tool_calls=tool_calls,
            finish_reason=choice.get("finish_reason", ""),
            raw_response=data,
        )

    async def stream(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        client = await self._get_client()

        url = self.base_url or "https://api.openai.com/v1"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": [self._format_message(m) for m in messages],
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
            "stream": True,
        }

        async with client.stream(
            "POST", f"{url}/chat/completions", headers=headers, json=payload
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    chunk = json.loads(line[6:])
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content

    def _format_message(self, message: Message) -> dict[str, Any]:
        msg: dict[str, Any] = {"role": message.role.value, "content": message.content}
        if message.name:
            msg["name"] = message.name
        if message.tool_calls:
            msg["tool_calls"] = message.tool_calls
        if message.tool_call_id:
            msg["tool_call_id"] = message.tool_call_id
        return msg

    def _format_tool(self, tool: ToolDefinition) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }


class AnthropicProvider(LLMProvider):
    """Anthropic API provider (Claude 3.5, Claude 4, etc.)."""

    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        client = await self._get_client()
        start_time = time.time()

        url = self.base_url or "https://api.anthropic.com/v1"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        # Anthropic uses a different message format
        system_msg = ""
        conversation: list[dict[str, str]] = []
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_msg = msg.content
            else:
                conversation.append({"role": msg.role.value, "content": msg.content})

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": conversation,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
        }

        if system_msg:
            payload["system"] = system_msg

        if tools:
            payload["tools"] = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.parameters,
                }
                for t in tools
            ]

        response = await client.post(
            f"{url}/messages",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        content_blocks = data.get("content", [])
        text_content = " ".join(
            block["text"] for block in content_blocks if block["type"] == "text"
        )

        tool_calls = []
        for block in content_blocks:
            if block["type"] == "tool_use":
                tool_calls.append({
                    "id": block["id"],
                    "name": block["name"],
                    "arguments": block["input"],
                })

        usage = data.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        cost = self.calculate_cost(input_tokens, output_tokens)
        self._total_tokens_used += input_tokens + output_tokens
        self._total_cost_usd += cost

        return LLMResponse(
            content=text_content,
            model=self.model_name,
            provider="anthropic",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=cost,
            latency_seconds=time.time() - start_time,
            tool_calls=tool_calls,
            finish_reason=data.get("stop_reason", ""),
            raw_response=data,
        )

    async def stream(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        client = await self._get_client()

        url = self.base_url or "https://api.anthropic.com/v1"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        system_msg = ""
        conversation: list[dict[str, str]] = []
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_msg = msg.content
            else:
                conversation.append({"role": msg.role.value, "content": msg.content})

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": conversation,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
            "stream": True,
        }
        if system_msg:
            payload["system"] = system_msg

        async with client.stream(
            "POST", f"{url}/messages", headers=headers, json=payload
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        event = json.loads(line[6:])
                        if event.get("type") == "content_block_delta":
                            delta = event.get("delta", {})
                            text = delta.get("text", "")
                            if text:
                                yield text
                    except json.JSONDecodeError:
                        continue


class OllamaProvider(LLMProvider):
    """Ollama local model provider."""

    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        client = await self._get_client()
        start_time = time.time()

        url = self.base_url or "http://localhost:11434"

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": [
                {"role": m.role.value, "content": m.content} for m in messages
            ],
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else self.temperature,
                "num_predict": max_tokens or self.max_tokens,
            },
        }

        if json_mode:
            payload["format"] = "json"

        response = await client.post(f"{url}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()

        content = data.get("message", {}).get("content", "")
        eval_count = data.get("eval_count", 0)
        prompt_eval_count = data.get("prompt_eval_count", 0)

        return LLMResponse(
            content=content,
            model=self.model_name,
            provider="ollama",
            input_tokens=prompt_eval_count,
            output_tokens=eval_count,
            total_tokens=prompt_eval_count + eval_count,
            cost_usd=0.0,  # Local models are free
            latency_seconds=time.time() - start_time,
            finish_reason="stop",
            raw_response=data,
        )

    async def stream(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        client = await self._get_client()

        url = self.base_url or "http://localhost:11434"

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": [
                {"role": m.role.value, "content": m.content} for m in messages
            ],
            "stream": True,
            "options": {
                "temperature": temperature if temperature is not None else self.temperature,
                "num_predict": max_tokens or self.max_tokens,
            },
        }

        async with client.stream("POST", f"{url}/api/chat", json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
