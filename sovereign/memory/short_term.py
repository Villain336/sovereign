"""Working Memory - fast, bounded context for the current task.

Manages the conversation context and recent information the agent
needs for its current task. Automatically evicts old entries when
the token budget is exceeded.
"""

from __future__ import annotations

from typing import Any

from sovereign.config import SovereignConfig
from sovereign.memory.store import MemoryEntry, MemoryType


class WorkingMemory:
    """Short-term working memory with bounded capacity.

    Maintains the current context window for an agent, including:
    - Recent conversation messages
    - Task-relevant information
    - Intermediate results

    Automatically manages capacity using importance-based eviction.
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self.max_tokens = config.memory.working_memory_max_tokens
        self._entries: list[MemoryEntry] = []
        self._current_tokens = 0

    def add(self, entry: MemoryEntry) -> None:
        """Add an entry to working memory, evicting if necessary."""
        entry_tokens = self._estimate_tokens(entry.content)

        # Evict less important entries if over capacity
        while self._current_tokens + entry_tokens > self.max_tokens and self._entries:
            evicted = self._evict_least_important()
            if evicted is None:
                break

        self._entries.append(entry)
        self._current_tokens += entry_tokens

    def add_message(
        self,
        role: str,
        content: str,
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        """Convenience method to add a conversation message."""
        entry = MemoryEntry(
            memory_type=MemoryType.WORKING,
            content=f"[{role}] {content}",
            metadata={"role": role, **(metadata or {})},
            importance=importance,
        )
        self.add(entry)
        return entry

    def get_context(self, max_tokens: int | None = None) -> list[MemoryEntry]:
        """Get the current working memory context.

        Returns entries ordered chronologically, within the token budget.
        """
        budget = max_tokens or self.max_tokens
        result: list[MemoryEntry] = []
        tokens_used = 0

        # Return most recent entries first (reversed), then re-reverse for chronological order
        for entry in reversed(self._entries):
            entry_tokens = self._estimate_tokens(entry.content)
            if tokens_used + entry_tokens <= budget:
                result.append(entry)
                tokens_used += entry_tokens
            else:
                break

        return list(reversed(result))

    def get_context_string(self, max_tokens: int | None = None) -> str:
        """Get working memory as a formatted string for LLM context."""
        entries = self.get_context(max_tokens)
        return "\n".join(e.content for e in entries)

    def search(self, query: str, max_results: int = 5) -> list[MemoryEntry]:
        """Search working memory by keyword matching.

        Working memory is small enough for simple keyword search.
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored: list[tuple[MemoryEntry, float]] = []
        for entry in self._entries:
            content_lower = entry.content.lower()
            content_words = set(content_lower.split())

            # Simple word overlap score
            overlap = len(query_words & content_words)
            if overlap > 0:
                score = overlap / len(query_words)
                scored.append((entry, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        results = [entry for entry, _ in scored[:max_results]]

        for entry in results:
            entry.touch()

        return results

    def get_important(self, threshold: float = 0.7) -> list[MemoryEntry]:
        """Get entries above the importance threshold."""
        return [e for e in self._entries if e.importance >= threshold]

    def prune(self, keep_recent: int = 10) -> int:
        """Prune old, low-importance entries. Returns number pruned."""
        if len(self._entries) <= keep_recent:
            return 0

        # Sort by importance (keep high importance) and recency
        entries_scored = []
        for i, entry in enumerate(self._entries):
            recency = i / len(self._entries)  # Newer = higher score
            combined = entry.importance * 0.6 + recency * 0.4
            entries_scored.append((entry, combined))

        entries_scored.sort(key=lambda x: x[1], reverse=True)
        kept = [e for e, _ in entries_scored[:keep_recent]]

        pruned_count = len(self._entries) - len(kept)
        self._entries = kept
        self._current_tokens = sum(self._estimate_tokens(e.content) for e in kept)

        return pruned_count

    def clear(self) -> None:
        """Clear all working memory."""
        self._entries.clear()
        self._current_tokens = 0

    def _evict_least_important(self) -> MemoryEntry | None:
        """Evict the least important entry from working memory."""
        if not self._entries:
            return None

        # Find least important entry (prefer evicting older entries for ties)
        min_entry = min(self._entries, key=lambda e: e.importance)
        self._entries.remove(min_entry)
        self._current_tokens -= self._estimate_tokens(min_entry.content)
        return min_entry

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for a text. ~4 chars per token is a rough heuristic."""
        return len(text) // 4 + 1

    @property
    def size(self) -> int:
        return len(self._entries)

    @property
    def tokens_used(self) -> int:
        return self._current_tokens

    @property
    def tokens_available(self) -> int:
        return max(0, self.max_tokens - self._current_tokens)
