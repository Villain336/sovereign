"""Task Scheduler - cron-like scheduling, heartbeat, and task queue.

Enables the agent to schedule recurring tasks, monitor health,
and manage a persistent task queue for deferred execution.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Coroutine

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduledTask(BaseModel):
    """A task in the scheduler."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    goal: str = ""  # The goal to pass to an agent
    cron_expression: str = ""  # e.g., "0 9 * * *" for 9am daily
    interval_seconds: int = 0  # For simple interval scheduling
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5
    max_retries: int = 3
    retry_count: int = 0
    last_run: datetime | None = None
    next_run: datetime | None = None
    last_result: str = ""
    last_error: str = ""
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_recurring(self) -> bool:
        return bool(self.cron_expression or self.interval_seconds > 0)


class HeartbeatStatus(BaseModel):
    """Status of the scheduler heartbeat."""

    is_alive: bool = True
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uptime_seconds: float = 0.0
    tasks_running: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0


class TaskScheduler:
    """Scheduler for autonomous task execution.

    Features:
    - Cron-like recurring task scheduling
    - Interval-based scheduling
    - Priority-based task queue
    - Heartbeat monitoring
    - Persistent task storage
    - Automatic retry on failure
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._tasks: dict[str, ScheduledTask] = {}
        self._task_handlers: dict[str, Callable[..., Coroutine[Any, Any, str]]] = {}
        self._running = False
        self._heartbeat = HeartbeatStatus()
        self._start_time = datetime.now(timezone.utc)
        self._store_path = Path(config.data_dir) / "scheduler.json"
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if self._store_path.exists():
            try:
                data = json.loads(self._store_path.read_text())
                self._tasks = {
                    tid: ScheduledTask(**tdata)
                    for tid, tdata in data.get("tasks", {}).items()
                }
            except (json.JSONDecodeError, Exception):
                self._tasks = {}

    def _save(self) -> None:
        data = {
            "tasks": {
                tid: task.model_dump(mode="json") for tid, task in self._tasks.items()
            }
        }
        self._store_path.write_text(json.dumps(data, indent=2, default=str))

    def schedule_task(
        self,
        name: str,
        goal: str = "",
        description: str = "",
        interval_seconds: int = 0,
        cron_expression: str = "",
        priority: int = 5,
        tags: list[str] | None = None,
    ) -> ScheduledTask:
        """Schedule a new task."""
        task = ScheduledTask(
            name=name,
            description=description,
            goal=goal,
            interval_seconds=interval_seconds,
            cron_expression=cron_expression,
            priority=priority,
            tags=tags or [],
        )

        # Set next run time
        if interval_seconds > 0:
            task.next_run = datetime.now(timezone.utc) + timedelta(seconds=interval_seconds)
        else:
            task.next_run = datetime.now(timezone.utc)

        self._tasks[task.id] = task
        self._save()
        return task

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.status = TaskStatus.CANCELLED
        self._save()
        return True

    def register_handler(
        self,
        task_name: str,
        handler: Callable[..., Coroutine[Any, Any, str]],
    ) -> None:
        """Register a handler function for a task name."""
        self._task_handlers[task_name] = handler

    async def run(self) -> None:
        """Start the scheduler loop."""
        self._running = True
        self._start_time = datetime.now(timezone.utc)

        while self._running:
            try:
                await self._tick()
                await asyncio.sleep(self.config.scheduler.heartbeat_interval_seconds)
                self._update_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(5)

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False

    async def _tick(self) -> None:
        """Execute one scheduler tick - check and run due tasks."""
        now = datetime.now(timezone.utc)
        due_tasks = self._get_due_tasks(now)

        # Sort by priority (lower = higher priority)
        due_tasks.sort(key=lambda t: t.priority)

        # Limit concurrent tasks
        running_count = sum(
            1 for t in self._tasks.values() if t.status == TaskStatus.RUNNING
        )
        available_slots = self.config.scheduler.max_concurrent_tasks - running_count

        for task in due_tasks[:available_slots]:
            asyncio.create_task(self._execute_task(task))

    async def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a single task."""
        task.status = TaskStatus.RUNNING
        task.last_run = datetime.now(timezone.utc)
        self._heartbeat.tasks_running += 1

        try:
            handler = self._task_handlers.get(task.name)
            if handler:
                result = await handler(task.goal, task.metadata)
                task.last_result = str(result)
                task.status = TaskStatus.COMPLETED
                self._heartbeat.tasks_completed += 1
            else:
                task.last_result = f"No handler registered for: {task.name}"
                task.status = TaskStatus.COMPLETED
                self._heartbeat.tasks_completed += 1

        except Exception as e:
            task.last_error = str(e)
            task.retry_count += 1

            if task.retry_count < task.max_retries:
                task.status = TaskStatus.PENDING
                # Exponential backoff for retry
                delay = min(2 ** task.retry_count * 60, 3600)
                task.next_run = datetime.now(timezone.utc) + timedelta(seconds=delay)
            else:
                task.status = TaskStatus.FAILED
                self._heartbeat.tasks_failed += 1

        finally:
            self._heartbeat.tasks_running = max(0, self._heartbeat.tasks_running - 1)

            # Schedule next run for recurring tasks
            if task.is_recurring and task.status == TaskStatus.COMPLETED:
                task.status = TaskStatus.PENDING
                if task.interval_seconds > 0:
                    task.next_run = datetime.now(timezone.utc) + timedelta(
                        seconds=task.interval_seconds
                    )

            self._save()

    def _get_due_tasks(self, now: datetime) -> list[ScheduledTask]:
        """Get tasks that are due for execution."""
        due: list[ScheduledTask] = []
        for task in self._tasks.values():
            if task.status == TaskStatus.PENDING and task.next_run and task.next_run <= now:
                due.append(task)
        return due

    def _update_heartbeat(self) -> None:
        """Update heartbeat status."""
        self._heartbeat.is_alive = True
        self._heartbeat.last_heartbeat = datetime.now(timezone.utc)
        self._heartbeat.uptime_seconds = (
            datetime.now(timezone.utc) - self._start_time
        ).total_seconds()

    def get_heartbeat(self) -> HeartbeatStatus:
        """Get current heartbeat status."""
        self._update_heartbeat()
        return self._heartbeat

    def get_tasks(
        self,
        status: TaskStatus | None = None,
        tags: list[str] | None = None,
    ) -> list[ScheduledTask]:
        """Get tasks, optionally filtered."""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        if tags:
            tag_set = set(tags)
            tasks = [t for t in tasks if set(t.tags) & tag_set]
        return tasks

    def get_stats(self) -> dict[str, Any]:
        """Get scheduler statistics."""
        by_status: dict[str, int] = {}
        for task in self._tasks.values():
            by_status[task.status.value] = by_status.get(task.status.value, 0) + 1

        return {
            "total_tasks": len(self._tasks),
            "by_status": by_status,
            "heartbeat": self._heartbeat.model_dump(mode="json"),
            "running": self._running,
        }
