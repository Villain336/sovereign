"""Unified Memory Store - manages all memory layers.

Sovereign's memory architecture has four layers:
1. Working Memory (short-term): Current conversation and task context
2. Episodic Memory: Past task experiences with outcomes (for learning)
3. Semantic Memory (long-term): Knowledge stored as vector embeddings
4. Procedural Memory: Learned skills and workflows

This is a major differentiator over OpenClaw (markdown files) and Manus (file-based).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig


class MemoryType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemoryEntry(BaseModel):
    """A single entry in any memory layer."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    memory_type: MemoryType
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    importance: float = 0.5  # 0-1, used for retention/eviction
    access_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    embedding: list[float] | None = None

    def touch(self) -> None:
        """Update access tracking."""
        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc)


class MemoryQuery(BaseModel):
    """Query to search across memory layers."""

    text: str
    memory_types: list[MemoryType] = Field(
        default_factory=lambda: [MemoryType.SEMANTIC, MemoryType.EPISODIC]
    )
    tags: list[str] = Field(default_factory=list)
    min_importance: float = 0.0
    max_results: int = 10
    recency_weight: float = 0.3  # How much to weight recent memories


class MemorySearchResult(BaseModel):
    """Result from a memory search."""

    entry: MemoryEntry
    relevance_score: float = 0.0
    source_layer: MemoryType = MemoryType.SEMANTIC


class MemoryStore:
    """Unified memory store that coordinates all memory layers.

    Provides a single interface for storing and retrieving memories
    across all layers, with intelligent search that combines
    semantic similarity, recency, and importance.
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config

        # Import here to avoid circular imports
        from sovereign.memory.episodic import EpisodicMemory
        from sovereign.memory.knowledge_graph import KnowledgeGraph
        from sovereign.memory.long_term import SemanticMemory
        from sovereign.memory.short_term import WorkingMemory

        self.working = WorkingMemory(config)
        self.semantic = SemanticMemory(config)
        self.episodic = EpisodicMemory(config)
        self.knowledge_graph = KnowledgeGraph(config)

    async def store(
        self,
        content: str,
        memory_type: MemoryType,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        importance: float = 0.5,
    ) -> MemoryEntry:
        """Store a memory in the appropriate layer."""
        entry = MemoryEntry(
            memory_type=memory_type,
            content=content,
            metadata=metadata or {},
            tags=tags or [],
            importance=importance,
        )

        if memory_type == MemoryType.WORKING:
            self.working.add(entry)
        elif memory_type == MemoryType.EPISODIC:
            await self.episodic.store(entry)
        elif memory_type == MemoryType.SEMANTIC:
            await self.semantic.store(entry)
        elif memory_type == MemoryType.PROCEDURAL:
            await self.semantic.store(entry)  # Stored in semantic with procedural tag

        return entry

    async def search(self, query: MemoryQuery) -> list[MemorySearchResult]:
        """Search across all specified memory layers.

        Combines results from multiple layers and ranks them by
        a weighted combination of semantic similarity, recency, and importance.
        """
        all_results: list[MemorySearchResult] = []

        if MemoryType.WORKING in query.memory_types:
            working_results = self.working.search(query.text, query.max_results)
            for entry in working_results:
                all_results.append(
                    MemorySearchResult(
                        entry=entry,
                        relevance_score=0.8,  # Working memory is always relevant
                        source_layer=MemoryType.WORKING,
                    )
                )

        if MemoryType.EPISODIC in query.memory_types:
            episodic_results = await self.episodic.search(
                query.text, query.max_results, query.tags
            )
            all_results.extend(episodic_results)

        if MemoryType.SEMANTIC in query.memory_types:
            semantic_results = await self.semantic.search(query.text, query.max_results)
            all_results.extend(semantic_results)

        # Re-rank by combined score
        for result in all_results:
            result.relevance_score = self._compute_combined_score(
                result, query.recency_weight
            )

        # Sort by combined score and limit
        all_results.sort(key=lambda r: r.relevance_score, reverse=True)
        return all_results[: query.max_results]

    async def recall(self, context: str, max_results: int = 5) -> str:
        """Recall relevant memories as a formatted context string.

        This is the main interface used by agents to augment their prompts
        with relevant past knowledge.
        """
        query = MemoryQuery(text=context, max_results=max_results)
        results = await self.search(query)

        if not results:
            return ""

        parts = ["## Relevant Memories\n"]
        for i, result in enumerate(results, 1):
            entry = result.entry
            parts.append(
                f"{i}. [{entry.memory_type.value}] {entry.content} "
                f"(relevance: {result.relevance_score:.2f})"
            )

        return "\n".join(parts)

    def _compute_combined_score(
        self,
        result: MemorySearchResult,
        recency_weight: float,
    ) -> float:
        """Compute a combined relevance score using multiple signals."""
        entry = result.entry

        # Base semantic relevance
        semantic_score = result.relevance_score

        # Recency bonus
        now = datetime.now(timezone.utc)
        age_hours = (now - entry.last_accessed).total_seconds() / 3600
        recency_score = 1.0 / (1.0 + age_hours / 24)  # Decay over days

        # Importance bonus
        importance_score = entry.importance

        # Access frequency bonus (diminishing returns)
        access_score = min(entry.access_count / 10, 1.0)

        # Weighted combination
        combined = (
            semantic_score * (1.0 - recency_weight) * 0.5
            + recency_score * recency_weight
            + importance_score * 0.3
            + access_score * 0.1
        )

        return min(combined, 1.0)

    async def consolidate(self) -> None:
        """Consolidate memories - promote important working memories to long-term.

        This mimics how human memory consolidation works during sleep:
        - Important working memories get stored in episodic/semantic memory
        - Duplicate or low-importance memories are pruned
        - Patterns across episodic memories are extracted as semantic knowledge
        """
        # Promote important working memories
        important_working = self.working.get_important(threshold=0.7)
        for entry in important_working:
            await self.semantic.store(entry)

        # Prune working memory
        self.working.prune()

        # Extract patterns from episodic memories
        patterns = await self.episodic.extract_patterns()
        for pattern in patterns:
            await self.store(
                content=pattern,
                memory_type=MemoryType.SEMANTIC,
                tags=["extracted_pattern"],
                importance=0.8,
            )
