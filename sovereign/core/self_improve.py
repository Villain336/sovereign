"""Self-Improvement Loop - learn from outcomes and adapt over time.

This module enables Sovereign to:
- Record outcomes of every task (success/failure, what worked, what didn't)
- Analyze patterns across past runs
- Extract lessons learned and persist them
- Provide context from past experience to improve future planning
- Track metrics over time (success rate, cost efficiency, speed)

The end goal: an agent that gets better at its job with every run,
eventually requiring no human intervention.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _get_memory_path() -> Path:
    """Get the self-improvement memory storage path."""
    mem_dir = Path.home() / ".sovereign" / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    return mem_dir


def _load_outcomes() -> list[dict[str, Any]]:
    """Load past outcomes from disk."""
    path = _get_memory_path() / "outcomes.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_outcomes(outcomes: list[dict[str, Any]]) -> None:
    """Save outcomes to disk."""
    path = _get_memory_path() / "outcomes.json"
    path.write_text(json.dumps(outcomes, indent=2, default=str), encoding="utf-8")


def _load_lessons() -> list[dict[str, Any]]:
    """Load extracted lessons from disk."""
    path = _get_memory_path() / "lessons.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_lessons(lessons: list[dict[str, Any]]) -> None:
    """Save lessons to disk."""
    path = _get_memory_path() / "lessons.json"
    path.write_text(json.dumps(lessons, indent=2, default=str), encoding="utf-8")


def record_outcome(
    goal: str,
    success: bool,
    output: str = "",
    error: str | None = None,
    steps_executed: int = 0,
    cost_usd: float = 0.0,
    duration_seconds: float = 0.0,
    tools_used: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record the outcome of a task for future learning.

    This should be called after every task completes (success or failure).
    The data is persisted and used to improve future planning.
    """
    outcome = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "goal": goal,
        "success": success,
        "output_preview": output[:500] if output else "",
        "error": error,
        "steps_executed": steps_executed,
        "cost_usd": cost_usd,
        "duration_seconds": duration_seconds,
        "tools_used": tools_used or [],
        "metadata": metadata or {},
    }

    outcomes = _load_outcomes()
    outcomes.append(outcome)

    # Keep only the last 1000 outcomes to prevent unbounded growth
    if len(outcomes) > 1000:
        outcomes = outcomes[-1000:]

    _save_outcomes(outcomes)

    # Auto-extract lessons from failures
    if not success and error:
        _extract_lesson_from_failure(goal, error)

    return outcome


def _extract_lesson_from_failure(goal: str, error: str) -> None:
    """Extract a lesson from a failed task."""
    lessons = _load_lessons()

    # Check if we already have a similar lesson
    error_lower = error.lower()
    for lesson in lessons:
        if lesson.get("error_pattern", "").lower() in error_lower:
            # Increment the occurrence count
            lesson["occurrences"] = lesson.get("occurrences", 1) + 1
            lesson["last_seen"] = datetime.now(timezone.utc).isoformat()
            _save_lessons(lessons)
            return

    # Add new lesson
    lesson = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "type": "failure",
        "goal_pattern": goal[:200],
        "error_pattern": error[:300],
        "lesson": f"Task failed with error: {error[:200]}. Consider alternative approaches.",
        "occurrences": 1,
        "resolved": False,
    }
    lessons.append(lesson)

    # Keep only the last 500 lessons
    if len(lessons) > 500:
        lessons = lessons[-500:]

    _save_lessons(lessons)


def add_lesson(
    lesson_text: str,
    lesson_type: str = "insight",
    goal_pattern: str = "",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Manually add a lesson learned.

    This can be called by the reasoning engine when it discovers
    something useful during reflection.
    """
    lessons = _load_lessons()

    lesson = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "type": lesson_type,
        "goal_pattern": goal_pattern,
        "lesson": lesson_text,
        "tags": tags or [],
        "occurrences": 1,
        "resolved": False,
    }
    lessons.append(lesson)
    _save_lessons(lessons)
    return lesson


def get_relevant_lessons(goal: str, max_lessons: int = 5) -> list[dict[str, Any]]:
    """Get lessons relevant to a given goal.

    Used by the planner to incorporate past learning into new plans.
    Matches by keyword overlap between the goal and lesson patterns.
    """
    lessons = _load_lessons()
    if not lessons:
        return []

    goal_words = set(goal.lower().split())

    scored: list[tuple[float, dict[str, Any]]] = []
    for lesson in lessons:
        pattern = lesson.get("goal_pattern", "") + " " + lesson.get("lesson", "")
        pattern_words = set(pattern.lower().split())

        # Score by word overlap
        overlap = len(goal_words & pattern_words)
        if overlap > 0:
            # Boost by occurrence count (more common = more important)
            score = overlap * (1 + 0.1 * lesson.get("occurrences", 1))
            scored.append((score, lesson))

    # Sort by relevance score
    scored.sort(key=lambda x: x[0], reverse=True)

    return [lesson for _, lesson in scored[:max_lessons]]


def get_performance_stats() -> dict[str, Any]:
    """Get aggregate performance statistics.

    Returns metrics like success rate, average cost, most used tools, etc.
    Used by the dashboard and for self-assessment.
    """
    outcomes = _load_outcomes()
    if not outcomes:
        return {
            "total_tasks": 0,
            "success_rate": 0.0,
            "avg_cost_usd": 0.0,
            "avg_steps": 0.0,
            "total_cost_usd": 0.0,
            "most_common_errors": [],
            "most_used_tools": [],
        }

    total = len(outcomes)
    successes = sum(1 for o in outcomes if o.get("success"))
    total_cost = sum(o.get("cost_usd", 0) for o in outcomes)
    total_steps = sum(o.get("steps_executed", 0) for o in outcomes)

    # Count tool usage
    tool_counts: dict[str, int] = {}
    for outcome in outcomes:
        for tool in outcome.get("tools_used", []):
            tool_counts[tool] = tool_counts.get(tool, 0) + 1

    # Count error patterns
    error_counts: dict[str, int] = {}
    for outcome in outcomes:
        error = outcome.get("error")
        if error:
            # Use first 100 chars as error pattern
            pattern = error[:100]
            error_counts[pattern] = error_counts.get(pattern, 0) + 1

    most_used_tools = sorted(
        tool_counts.items(), key=lambda x: x[1], reverse=True
    )[:10]
    most_common_errors = sorted(
        error_counts.items(), key=lambda x: x[1], reverse=True
    )[:5]

    return {
        "total_tasks": total,
        "success_rate": successes / max(total, 1),
        "avg_cost_usd": total_cost / max(total, 1),
        "avg_steps": total_steps / max(total, 1),
        "total_cost_usd": total_cost,
        "most_used_tools": [{"tool": t, "count": c} for t, c in most_used_tools],
        "most_common_errors": [{"error": e, "count": c} for e, c in most_common_errors],
        "lessons_learned": len(_load_lessons()),
    }
