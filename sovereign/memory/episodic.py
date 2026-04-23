"""Episodic Memory - stores past task experiences with outcomes.

This enables the agent to learn from its own history:
- What approaches worked for similar tasks
- What failures to avoid
- How long similar tasks took
- What tools were most effective
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig
from sovereign.memory.store import MemoryEntry, MemorySearchResult, MemoryType


class Episode(BaseModel):
    """A complete record of a task execution."""

    id: str
    goal: str
    approach: str = ""
    outcome: str = ""
    success: bool = False
    steps_taken: int = 0
    duration_seconds: float = 0.0
    cost_usd: float = 0.0
    tools_used: list[str] = Field(default_factory=list)
    agent_role: str = "general"
    lessons: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class EpisodicMemory:
    """Stores and retrieves past task episodes for experiential learning.

    Each episode records:
    - The goal/task description
    - The approach taken (plan summary)
    - The outcome (success/failure + output)
    - Lessons learned
    - Performance metrics (time, cost, steps)

    This allows the agent to:
    - Learn from past successes and failures
    - Estimate task difficulty and duration
    - Choose better approaches for similar tasks
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._max_episodes = config.memory.episodic_memory_max_episodes
        self._episodes: list[Episode] = []
        self._store_path = Path(config.memory.vector_store_path) / "episodes.json"
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        """Load episodes from disk."""
        if self._store_path.exists():
            try:
                data = json.loads(self._store_path.read_text())
                self._episodes = [Episode(**ep) for ep in data]
            except (json.JSONDecodeError, Exception):
                self._episodes = []

    def _save(self) -> None:
        """Save episodes to disk."""
        data = [ep.model_dump(mode="json") for ep in self._episodes]
        self._store_path.write_text(json.dumps(data, indent=2, default=str))

    async def record_episode(self, episode: Episode) -> None:
        """Record a completed task episode."""
        self._episodes.append(episode)

        # Evict old episodes if over capacity
        if len(self._episodes) > self._max_episodes:
            # Keep most important episodes (successful ones, recent ones)
            self._episodes.sort(
                key=lambda e: (e.success, e.created_at.timestamp()),
                reverse=True,
            )
            self._episodes = self._episodes[: self._max_episodes]

        self._save()

    async def store(self, entry: MemoryEntry) -> None:
        """Store a memory entry as an episode."""
        episode = Episode(
            id=entry.id,
            goal=entry.content,
            tags=entry.tags,
            metadata=entry.metadata,
            success=entry.metadata.get("success", False),
        )
        await self.record_episode(episode)

    async def search(
        self,
        query: str,
        max_results: int = 5,
        tags: list[str] | None = None,
    ) -> list[MemorySearchResult]:
        """Search episodes by similarity to query."""
        if not self._episodes:
            return []

        query_lower = query.lower()
        query_terms = set(query_lower.split())

        scored: list[tuple[Episode, float]] = []

        for episode in self._episodes:
            goal_terms = set(episode.goal.lower().split())

            overlap = len(query_terms & goal_terms)
            if overlap == 0:
                continue

            score = overlap / max(len(query_terms), 1)

            # Boost successful episodes
            if episode.success:
                score *= 1.3

            # Boost episodes with matching tags
            if tags:
                tag_overlap = len(set(tags) & set(episode.tags))
                if tag_overlap > 0:
                    score *= 1.2

            scored.append((episode, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        results: list[MemorySearchResult] = []
        for episode, score in scored[:max_results]:
            entry = MemoryEntry(
                id=episode.id,
                memory_type=MemoryType.EPISODIC,
                content=self._format_episode(episode),
                metadata=episode.metadata,
                tags=episode.tags,
                importance=0.8 if episode.success else 0.4,
                created_at=episode.created_at,
            )
            results.append(
                MemorySearchResult(
                    entry=entry,
                    relevance_score=min(score, 1.0),
                    source_layer=MemoryType.EPISODIC,
                )
            )

        return results

    async def get_similar_episodes(
        self,
        goal: str,
        max_results: int = 3,
    ) -> list[Episode]:
        """Find episodes with similar goals for learning."""
        goal_lower = goal.lower()
        goal_terms = set(goal_lower.split())

        scored = []
        for episode in self._episodes:
            ep_terms = set(episode.goal.lower().split())
            overlap = len(goal_terms & ep_terms)
            if overlap >= 2:
                scored.append((episode, overlap))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [ep for ep, _ in scored[:max_results]]

    async def get_success_rate(self, tags: list[str] | None = None) -> float:
        """Get the success rate for episodes, optionally filtered by tags."""
        episodes = self._episodes
        if tags:
            tag_set = set(tags)
            episodes = [e for e in episodes if set(e.tags) & tag_set]

        if not episodes:
            return 0.0

        successful = sum(1 for e in episodes if e.success)
        return successful / len(episodes)

    async def extract_patterns(self) -> list[str]:
        """Extract common patterns from episodes for semantic memory consolidation.

        Looks for recurring themes in successful vs. failed episodes.
        """
        if len(self._episodes) < 5:
            return []

        patterns: list[str] = []

        # Find common tools in successful episodes
        successful = [e for e in self._episodes if e.success]
        if successful:
            tool_counts: dict[str, int] = {}
            for ep in successful:
                for tool in ep.tools_used:
                    tool_counts[tool] = tool_counts.get(tool, 0) + 1

            frequent_tools = [
                tool for tool, count in tool_counts.items()
                if count >= len(successful) * 0.3  # Used in 30%+ of successes
            ]
            if frequent_tools:
                patterns.append(
                    f"Frequently successful tools: {', '.join(frequent_tools)}"
                )

        # Find common failure patterns
        failed = [e for e in self._episodes if not e.success]
        if failed:
            all_lessons = []
            for ep in failed:
                all_lessons.extend(ep.lessons)
            if all_lessons:
                # Simple frequency analysis of lesson keywords
                word_counts: dict[str, int] = {}
                for lesson in all_lessons:
                    for word in lesson.lower().split():
                        if len(word) > 4:
                            word_counts[word] = word_counts.get(word, 0) + 1

                common_issues = sorted(
                    word_counts.items(), key=lambda x: x[1], reverse=True
                )[:5]
                if common_issues:
                    patterns.append(
                        f"Common failure themes: {', '.join(w for w, _ in common_issues)}"
                    )

        return patterns

    def _format_episode(self, episode: Episode) -> str:
        """Format an episode as a human-readable string."""
        status = "SUCCESS" if episode.success else "FAILED"
        parts = [
            f"[{status}] Goal: {episode.goal}",
            f"Approach: {episode.approach}" if episode.approach else "",
            f"Outcome: {episode.outcome}" if episode.outcome else "",
            f"Steps: {episode.steps_taken}, Duration: {episode.duration_seconds:.1f}s",
        ]
        if episode.lessons:
            parts.append(f"Lessons: {'; '.join(episode.lessons)}")
        return " | ".join(p for p in parts if p)

    @property
    def size(self) -> int:
        return len(self._episodes)
