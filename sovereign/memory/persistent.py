"""Persistent File-Based Memory - survives restarts.

Like OpenClaw's Markdown-based memory, this stores all memories as
human-readable files on disk. Organized by type:
  ~/.sovereign/memory/episodic/    - Past task experiences
  ~/.sovereign/memory/semantic/    - Learned knowledge
  ~/.sovereign/memory/procedures/  - Learned workflows/skills
  ~/.sovereign/memory/working/     - Current context (cleared on restart)

Each memory is a Markdown file with YAML front matter for metadata.
This makes memories inspectable, editable, and git-trackable.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PersistentMemory:
    """File-based persistent memory that survives restarts.

    Stores memories as Markdown files with JSON metadata headers.
    Supports search, tagging, importance ranking, and automatic
    consolidation of related memories.
    """

    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = base_dir or os.path.join(
            os.path.expanduser("~"), ".sovereign", "memory",
        )
        self._dirs = {
            "episodic": os.path.join(self.base_dir, "episodic"),
            "semantic": os.path.join(self.base_dir, "semantic"),
            "procedures": os.path.join(self.base_dir, "procedures"),
            "working": os.path.join(self.base_dir, "working"),
        }
        for d in self._dirs.values():
            Path(d).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def store(
        self,
        content: str,
        memory_type: str = "semantic",
        tags: list[str] | None = None,
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
        title: str | None = None,
    ) -> str:
        """Store a memory as a Markdown file. Returns the file path."""
        ts = datetime.now(timezone.utc)
        slug = self._make_slug(title or content[:60])
        filename = f"{ts.strftime('%Y%m%d_%H%M%S')}_{slug}.md"
        dir_path = self._dirs.get(memory_type, self._dirs["semantic"])
        filepath = os.path.join(dir_path, filename)

        header = {
            "title": title or content[:80],
            "type": memory_type,
            "tags": tags or [],
            "importance": importance,
            "created": ts.isoformat(),
            "accessed": ts.isoformat(),
            "access_count": 0,
            **(metadata or {}),
        }

        md = self._format_markdown(header, content)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        return filepath

    def store_episode(
        self,
        goal: str,
        outcome: str,
        success: bool,
        steps: list[str] | None = None,
        lessons: list[str] | None = None,
    ) -> str:
        """Store a task episode (what happened, outcome, lessons learned)."""
        content_parts = [
            f"## Goal\n{goal}\n",
            f"## Outcome\n{'SUCCESS' if success else 'FAILURE'}: {outcome}\n",
        ]
        if steps:
            content_parts.append("## Steps\n" + "\n".join(f"- {s}" for s in steps))
        if lessons:
            content_parts.append("## Lessons\n" + "\n".join(f"- {lesson}" for lesson in lessons))

        return self.store(
            content="\n".join(content_parts),
            memory_type="episodic",
            tags=["episode", "success" if success else "failure"],
            importance=0.7 if success else 0.8,  # Failures are more important to remember
            title=f"Episode: {goal[:60]}",
            metadata={"success": success},
        )

    def store_procedure(
        self,
        name: str,
        description: str,
        steps: list[str],
        tags: list[str] | None = None,
    ) -> str:
        """Store a learned procedure/workflow."""
        content = f"## {name}\n\n{description}\n\n### Steps\n"
        content += "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))

        return self.store(
            content=content,
            memory_type="procedures",
            tags=["procedure", *(tags or [])],
            importance=0.8,
            title=name,
        )

    # ------------------------------------------------------------------
    # Read / Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        memory_types: list[str] | None = None,
        tags: list[str] | None = None,
        min_importance: float = 0.0,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Search memories by keyword, tags, and importance."""
        types = memory_types or ["episodic", "semantic", "procedures"]
        results: list[dict[str, Any]] = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for mem_type in types:
            dir_path = self._dirs.get(mem_type)
            if not dir_path or not os.path.exists(dir_path):
                continue

            for fname in os.listdir(dir_path):
                if not fname.endswith(".md"):
                    continue
                filepath = os.path.join(dir_path, fname)
                try:
                    header, content = self._parse_markdown(filepath)
                except Exception:
                    continue

                # Filter by importance
                if header.get("importance", 0) < min_importance:
                    continue

                # Filter by tags
                if tags:
                    file_tags = set(header.get("tags", []))
                    if not file_tags.intersection(tags):
                        continue

                # Score by keyword match
                content_lower = content.lower()
                title_lower = header.get("title", "").lower()
                tag_str = " ".join(header.get("tags", [])).lower()

                score = 0.0
                for word in query_words:
                    if word in title_lower:
                        score += 0.4
                    if word in tag_str:
                        score += 0.3
                    if word in content_lower:
                        score += 0.2
                        # Bonus for frequency
                        count = content_lower.count(word)
                        score += min(count * 0.02, 0.1)

                if score > 0:
                    # Recency bonus
                    try:
                        created = datetime.fromisoformat(header.get("created", ""))
                        age_hours = (
                            datetime.now(timezone.utc) - created
                        ).total_seconds() / 3600
                        recency_bonus = 0.1 / (1.0 + age_hours / 24)
                        score += recency_bonus
                    except (ValueError, TypeError):
                        pass

                    # Importance bonus
                    score += header.get("importance", 0.5) * 0.1

                    results.append({
                        "path": filepath,
                        "header": header,
                        "content": content,
                        "score": score,
                        "type": mem_type,
                    })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:max_results]

    def recall(self, context: str, max_results: int = 5) -> str:
        """Recall relevant memories as formatted text for LLM context."""
        results = self.search(context, max_results=max_results)
        if not results:
            return ""

        parts = ["## Relevant Memories\n"]
        for i, r in enumerate(results, 1):
            header = r["header"]
            snippet = r["content"][:200].replace("\n", " ")
            parts.append(
                f"{i}. [{r['type']}] **{header.get('title', 'Untitled')}** "
                f"(importance: {header.get('importance', 0.5):.1f})\n"
                f"   {snippet}..."
            )
        return "\n".join(parts)

    def list_memories(
        self, memory_type: str = "semantic", limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List memories of a given type, most recent first."""
        dir_path = self._dirs.get(memory_type)
        if not dir_path or not os.path.exists(dir_path):
            return []

        memories: list[dict[str, Any]] = []
        for fname in sorted(os.listdir(dir_path), reverse=True):
            if not fname.endswith(".md"):
                continue
            filepath = os.path.join(dir_path, fname)
            try:
                header, content = self._parse_markdown(filepath)
                memories.append({
                    "path": filepath,
                    "filename": fname,
                    "header": header,
                    "preview": content[:150],
                })
            except Exception:
                continue
            if len(memories) >= limit:
                break
        return memories

    def get_memory(self, filepath: str) -> dict[str, Any]:
        """Read a specific memory file."""
        header, content = self._parse_markdown(filepath)

        # Update access tracking
        header["access_count"] = header.get("access_count", 0) + 1
        header["accessed"] = datetime.now(timezone.utc).isoformat()
        md = self._format_markdown(header, content)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        return {"header": header, "content": content, "path": filepath}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_slug(text: str) -> str:
        """Create a filename-safe slug from text."""
        slug = re.sub(r"[^a-z0-9]+", "_", text.lower().strip())
        slug = slug.strip("_")[:40]
        return slug or f"memory_{int(time.time())}"

    @staticmethod
    def _format_markdown(header: dict[str, Any], content: str) -> str:
        """Format a memory as Markdown with JSON front matter."""
        header_json = json.dumps(header, indent=2, default=str)
        return f"<!--\n{header_json}\n-->\n\n{content}\n"

    @staticmethod
    def _parse_markdown(filepath: str) -> tuple[dict[str, Any], str]:
        """Parse a memory Markdown file into header and content."""
        with open(filepath, encoding="utf-8") as f:
            text = f.read()

        # Extract JSON header from HTML comment
        match = re.match(r"<!--\s*(.*?)\s*-->", text, re.DOTALL)
        if match:
            try:
                header = json.loads(match.group(1))
            except json.JSONDecodeError:
                header = {}
            content = text[match.end():].strip()
        else:
            header = {}
            content = text.strip()

        return header, content
