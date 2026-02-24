"""Smart Model Router - routes tasks to the optimal LLM based on requirements.

This is a key differentiator: instead of using one model for everything,
Sovereign intelligently routes based on:
- Task complexity (simple tasks → cheap models, complex → capable models)
- Required capabilities (coding, analysis, creative writing, etc.)
- Cost optimization (stay within budget)
- Latency requirements (real-time vs. batch)
- Model availability and rate limits
"""

from __future__ import annotations

from sovereign.config import LLMModelConfig, LLMProviderType, SovereignConfig
from sovereign.llm.provider import (
    AnthropicProvider,
    LLMProvider,
    LLMResponse,
    Message,
    OllamaProvider,
    OpenAIProvider,
    ToolDefinition,
)


class TaskProfile(object):
    """Profile of a task for model routing decisions."""

    def __init__(
        self,
        complexity: float = 0.5,
        required_capabilities: list[str] | None = None,
        max_cost_usd: float | None = None,
        max_latency_seconds: float | None = None,
        prefer_streaming: bool = False,
        requires_tool_use: bool = False,
    ) -> None:
        self.complexity = complexity  # 0-1
        self.required_capabilities = required_capabilities or ["general"]
        self.max_cost_usd = max_cost_usd
        self.max_latency_seconds = max_latency_seconds
        self.prefer_streaming = prefer_streaming
        self.requires_tool_use = requires_tool_use


class ModelRouter:
    """Routes LLM requests to the optimal model based on task requirements.

    Maintains a pool of configured models and selects the best one for each
    request based on the task profile, cost constraints, and model capabilities.
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._providers: dict[str, LLMProvider] = {}
        self._model_configs: dict[str, LLMModelConfig] = {}
        self._usage_tracking: dict[str, dict[str, float]] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize LLM providers from configuration."""
        for model_key, model_config in self.config.llm.models.items():
            provider = self._create_provider(model_config)
            if provider:
                self._providers[model_key] = provider
                self._model_configs[model_key] = model_config
                self._usage_tracking[model_key] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost_usd": 0.0,
                    "errors": 0,
                }

    def _create_provider(self, config: LLMModelConfig) -> LLMProvider | None:
        """Create a provider instance from config."""
        provider_map = {
            LLMProviderType.OPENAI: OpenAIProvider,
            LLMProviderType.ANTHROPIC: AnthropicProvider,
            LLMProviderType.OLLAMA: OllamaProvider,
        }

        provider_class = provider_map.get(config.provider)
        if not provider_class:
            return None

        return provider_class(
            api_key=config.api_key,
            model_name=config.model_name,
            base_url=config.base_url,
            max_tokens=config.max_tokens,
            temperature=0.7,
            cost_per_1k_input=config.cost_per_1k_input,
            cost_per_1k_output=config.cost_per_1k_output,
        )

    def add_provider(
        self, key: str, config: LLMModelConfig
    ) -> None:
        """Dynamically add a new provider."""
        provider = self._create_provider(config)
        if provider:
            self._providers[key] = provider
            self._model_configs[key] = config
            self._usage_tracking[key] = {
                "requests": 0,
                "tokens": 0,
                "cost_usd": 0.0,
                "errors": 0,
            }

    async def generate(
        self,
        messages: list[Message],
        task_profile: TaskProfile | None = None,
        tools: list[ToolDefinition] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = False,
        model_key: str | None = None,
    ) -> LLMResponse:
        """Generate a response, routing to the best model for the task.

        If model_key is specified, uses that model directly.
        Otherwise, selects the best model based on the task profile.
        """
        if model_key and model_key in self._providers:
            selected_key = model_key
        else:
            profile = task_profile or TaskProfile()
            selected_key = self._select_model(profile)

        provider = self._providers[selected_key]

        try:
            response = await provider.generate(
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
            )

            # Track usage
            self._usage_tracking[selected_key]["requests"] += 1
            self._usage_tracking[selected_key]["tokens"] += response.total_tokens
            self._usage_tracking[selected_key]["cost_usd"] += response.cost_usd

            return response

        except Exception:
            self._usage_tracking[selected_key]["errors"] += 1

            # Try fallback model
            fallback_key = self._get_fallback(selected_key)
            if fallback_key:
                fallback_provider = self._providers[fallback_key]
                return await fallback_provider.generate(
                    messages=messages,
                    tools=tools,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode,
                )
            raise

    def _select_model(self, profile: TaskProfile) -> str:
        """Select the best model based on the task profile.

        Scoring algorithm considers:
        1. Capability match (does the model support required capabilities?)
        2. Complexity match (is the model powerful enough?)
        3. Cost efficiency (cheaper is better within capability requirements)
        4. Error rate (prefer reliable models)
        """
        if not self._providers:
            raise ValueError("No LLM providers configured")

        scores: dict[str, float] = {}

        for model_key, model_config in self._model_configs.items():
            score = 0.0

            # Capability match (0-0.4)
            required_caps = set(profile.required_capabilities)
            model_caps = set(model_config.capabilities)
            if required_caps:
                overlap = len(required_caps & model_caps)
                cap_score = overlap / len(required_caps)
                score += 0.4 * cap_score

            # Complexity match (0-0.3)
            # Higher complexity tasks need more capable (usually more expensive) models
            if profile.complexity > self.config.llm.complexity_threshold_high:
                # High complexity: prefer powerful models (higher cost = usually more capable)
                score += 0.3 * min(model_config.cost_per_1k_output / 0.06, 1.0)
            elif profile.complexity < self.config.llm.complexity_threshold_low:
                # Low complexity: prefer cheap models
                if model_config.cost_per_1k_output > 0:
                    score += 0.3 * (1.0 - min(model_config.cost_per_1k_output / 0.06, 1.0))
                else:
                    score += 0.3  # Free models get full score for simple tasks
            else:
                # Medium complexity: balanced
                score += 0.15

            # Cost efficiency (0-0.2)
            if profile.max_cost_usd is not None:
                # Estimate cost for this request
                estimated_cost = (model_config.cost_per_1k_input * 2 +
                                  model_config.cost_per_1k_output * 1)
                if estimated_cost <= profile.max_cost_usd:
                    score += 0.2
                else:
                    score -= 0.1
            elif self.config.llm.cost_optimization:
                # Prefer cheaper models when cost optimization is enabled
                if model_config.cost_per_1k_output > 0:
                    score += 0.2 * (1.0 - min(model_config.cost_per_1k_output / 0.06, 0.9))
                else:
                    score += 0.2

            # Reliability (0-0.1)
            usage = self._usage_tracking.get(model_key, {})
            total_requests = usage.get("requests", 0)
            errors = usage.get("errors", 0)
            if total_requests > 0:
                error_rate = errors / total_requests
                score += 0.1 * (1.0 - error_rate)
            else:
                score += 0.05  # Neutral for untested models

            scores[model_key] = score

        # Select highest scoring model
        best_key = max(scores, key=lambda k: scores[k])
        return best_key

    def _get_fallback(self, failed_key: str) -> str | None:
        """Get a fallback model when the primary fails."""
        for key in self._providers:
            if key != failed_key:
                return key
        return None

    def get_usage_stats(self) -> dict[str, dict[str, float]]:
        """Get usage statistics for all models."""
        return dict(self._usage_tracking)

    def get_total_cost(self) -> float:
        """Get total cost across all models."""
        return sum(stats["cost_usd"] for stats in self._usage_tracking.values())

    async def close(self) -> None:
        """Close all provider connections."""
        for provider in self._providers.values():
            await provider.close()
