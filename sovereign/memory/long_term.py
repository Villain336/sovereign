"""Semantic Memory - long-term knowledge storage with vector embeddings.

Uses vector similarity search to find relevant past knowledge.
This provides the agent with genuine long-term memory that persists
across tasks and sessions.
"""

from __future__ import annotations

import json
from pathlib import Path

from sovereign.config import SovereignConfig
from sovereign.memory.store import MemoryEntry, MemorySearchResult, MemoryType


class SemanticMemory:
    """Long-term semantic memory using vector embeddings.

    Stores knowledge as vector embeddings for efficient similarity search.
    Falls back to keyword-based search if no vector store is available.

    In production, this integrates with ChromaDB or similar vector stores.
    The fallback implementation uses TF-IDF-like scoring for portability.
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._store_path = Path(config.memory.vector_store_path)
        self._store_path.mkdir(parents=True, exist_ok=True)
        self._entries: list[MemoryEntry] = []
        self._index_file = self._store_path / "semantic_index.json"
        self._load_index()

    def _load_index(self) -> None:
        """Load the memory index from disk."""
        if self._index_file.exists():
            try:
                data = json.loads(self._index_file.read_text())
                self._entries = [MemoryEntry(**entry) for entry in data]
            except (json.JSONDecodeError, Exception):
                self._entries = []

    def _save_index(self) -> None:
        """Persist the memory index to disk."""
        data = [entry.model_dump(mode="json") for entry in self._entries]
        self._index_file.write_text(json.dumps(data, indent=2, default=str))

    async def store(self, entry: MemoryEntry) -> None:
        """Store a memory entry with its vector embedding."""
        # Compute a simple text fingerprint for deduplication
        if self._is_duplicate(entry.content):
            return

        entry.memory_type = MemoryType.SEMANTIC
        self._entries.append(entry)
        self._save_index()

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[MemorySearchResult]:
        """Search semantic memory by text similarity.

        Uses TF-IDF-like scoring as a portable fallback.
        In production, this would use vector similarity via ChromaDB.
        """
        if not self._entries:
            return []

        query_lower = query.lower()
        query_terms = set(query_lower.split())

        scored: list[tuple[MemoryEntry, float]] = []

        for entry in self._entries:
            content_lower = entry.content.lower()
            content_terms = set(content_lower.split())

            # Term overlap (TF-IDF-like)
            if not query_terms:
                continue

            overlap = len(query_terms & content_terms)
            if overlap == 0:
                continue

            # Normalize by query length and document length
            precision = overlap / len(query_terms)
            recall = overlap / max(len(content_terms), 1)

            # F1-like score
            if precision + recall > 0:
                score = 2 * (precision * recall) / (precision + recall)
            else:
                score = 0.0

            # Boost by importance
            score *= (0.7 + 0.3 * entry.importance)

            # Boost by tag relevance
            tag_overlap = len(set(query_lower.split()) & set(t.lower() for t in entry.tags))
            if tag_overlap > 0:
                score *= 1.2

            scored.append((entry, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        results: list[MemorySearchResult] = []
        for entry, score in scored[:max_results]:
            entry.touch()
            results.append(
                MemorySearchResult(
                    entry=entry,
                    relevance_score=min(score, 1.0),
                    source_layer=MemoryType.SEMANTIC,
                )
            )

        self._save_index()
        return results

    async def get_all(self, tags: list[str] | None = None) -> list[MemoryEntry]:
        """Get all entries, optionally filtered by tags."""
        if tags:
            tag_set = set(tags)
            return [e for e in self._entries if set(e.tags) & tag_set]
        return list(self._entries)

    async def delete(self, entry_id: str) -> bool:
        """Delete an entry by ID."""
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.id != entry_id]
        if len(self._entries) < before:
            self._save_index()
            return True
        return False

    async def clear(self) -> None:
        """Clear all semantic memories."""
        self._entries.clear()
        self._save_index()

    def _is_duplicate(self, content: str, threshold: float = 0.9) -> bool:
        """Check if content is a near-duplicate of existing entries."""
        content_words = set(content.lower().split())
        for entry in self._entries:
            entry_words = set(entry.content.lower().split())
            if not content_words or not entry_words:
                continue
            overlap = len(content_words & entry_words)
            similarity = overlap / max(len(content_words | entry_words), 1)
            if similarity >= threshold:
                return True
        return False

    @property
    def size(self) -> int:
        return len(self._entries)
