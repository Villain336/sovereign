"""Persistent Task Queue - SQLite-backed task persistence.

Tasks survive restarts. The queue supports priority ordering,
status tracking, retry logic, and result storage.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class PersistentTask(BaseModel):
    """A task that persists across restarts."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5
    agent_role: str = "general"
    budget_usd: float | None = None
    result_output: str = ""
    result_error: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )
    started_at: str = ""
    completed_at: str = ""


class TaskQueue:
    """SQLite-backed persistent task queue.

    Tasks are stored in a SQLite database so they survive process restarts.
    Supports priority ordering, status tracking, and retry logic.
    """

    def __init__(self, db_path: str | None = None) -> None:
        if db_path is None:
            data_dir = os.path.join(os.path.expanduser("~"), ".sovereign")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "task_queue.db")
        self._db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database schema."""
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    priority INTEGER NOT NULL DEFAULT 5,
                    agent_role TEXT NOT NULL DEFAULT 'general',
                    budget_usd REAL,
                    result_output TEXT DEFAULT '',
                    result_error TEXT DEFAULT '',
                    metadata TEXT DEFAULT '{}',
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    created_at TEXT NOT NULL,
                    started_at TEXT DEFAULT '',
                    completed_at TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_status
                ON tasks(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_priority
                ON tasks(priority DESC)
            """)
            conn.commit()
        finally:
            conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_task(self, task: PersistentTask) -> str:
        """Add a task to the queue. Returns the task ID."""
        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT INTO tasks
                   (id, goal, status, priority, agent_role, budget_usd,
                    result_output, result_error, metadata, retry_count,
                    max_retries, created_at, started_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    task.id,
                    task.goal,
                    task.status.value,
                    task.priority,
                    task.agent_role,
                    task.budget_usd,
                    task.result_output,
                    task.result_error,
                    json.dumps(task.metadata),
                    task.retry_count,
                    task.max_retries,
                    task.created_at,
                    task.started_at,
                    task.completed_at,
                ),
            )
            conn.commit()
            return task.id
        finally:
            conn.close()

    def get_task(self, task_id: str) -> PersistentTask | None:
        """Get a task by ID."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,),
            ).fetchone()
            if row is None:
                return None
            return self._row_to_task(row)
        finally:
            conn.close()

    def get_next_task(self) -> PersistentTask | None:
        """Get the highest-priority pending task."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                """SELECT * FROM tasks
                   WHERE status = 'pending'
                   ORDER BY priority DESC, created_at ASC
                   LIMIT 1""",
            ).fetchone()
            if row is None:
                return None
            return self._row_to_task(row)
        finally:
            conn.close()

    def list_tasks(
        self,
        status: TaskStatus | None = None,
        limit: int = 50,
    ) -> list[PersistentTask]:
        """List tasks, optionally filtered by status."""
        conn = self._get_conn()
        try:
            if status:
                rows = conn.execute(
                    """SELECT * FROM tasks WHERE status = ?
                       ORDER BY priority DESC, created_at DESC LIMIT ?""",
                    (status.value, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM tasks
                       ORDER BY priority DESC, created_at DESC LIMIT ?""",
                    (limit,),
                ).fetchall()
            return [self._row_to_task(r) for r in rows]
        finally:
            conn.close()

    def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        output: str = "",
        error: str = "",
    ) -> None:
        """Update task status and optionally set result."""
        conn = self._get_conn()
        try:
            now = datetime.now(timezone.utc).isoformat()
            updates = {"status": status.value}

            if status == TaskStatus.IN_PROGRESS:
                updates["started_at"] = now
            elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                updates["completed_at"] = now

            if output:
                updates["result_output"] = output
            if error:
                updates["result_error"] = error

            set_clause = ", ".join(f"{k} = ?" for k in updates)
            values = list(updates.values()) + [task_id]

            conn.execute(
                f"UPDATE tasks SET {set_clause} WHERE id = ?",  # noqa: S608
                values,
            )
            conn.commit()
        finally:
            conn.close()

    def retry_task(self, task_id: str) -> bool:
        """Retry a failed task if retries remain. Returns True if retried."""
        task = self.get_task(task_id)
        if task is None:
            return False
        if task.retry_count >= task.max_retries:
            return False

        conn = self._get_conn()
        try:
            conn.execute(
                """UPDATE tasks
                   SET status = 'pending',
                       retry_count = retry_count + 1,
                       result_error = '',
                       started_at = '',
                       completed_at = ''
                   WHERE id = ?""",
                (task_id,),
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def cancel_task(self, task_id: str) -> None:
        """Cancel a pending or in-progress task."""
        self.update_status(task_id, TaskStatus.CANCELLED)

    def get_stats(self) -> dict[str, int]:
        """Get task count by status."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status",
            ).fetchall()
            stats: dict[str, int] = {}
            for row in rows:
                stats[row["status"]] = row["cnt"]
            stats["total"] = sum(stats.values())
            return stats
        finally:
            conn.close()

    def clear_completed(self) -> int:
        """Remove all completed tasks. Returns count removed."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "DELETE FROM tasks WHERE status IN ('completed', 'cancelled')",
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> PersistentTask:
        """Convert a database row to a PersistentTask."""
        metadata = {}
        raw_meta = row["metadata"]
        if raw_meta:
            try:
                metadata = json.loads(raw_meta)
            except json.JSONDecodeError:
                pass

        return PersistentTask(
            id=row["id"],
            goal=row["goal"],
            status=TaskStatus(row["status"]),
            priority=row["priority"],
            agent_role=row["agent_role"],
            budget_usd=row["budget_usd"],
            result_output=row["result_output"] or "",
            result_error=row["result_error"] or "",
            metadata=metadata,
            retry_count=row["retry_count"],
            max_retries=row["max_retries"],
            created_at=row["created_at"],
            started_at=row["started_at"] or "",
            completed_at=row["completed_at"] or "",
        )
