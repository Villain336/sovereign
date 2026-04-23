"""Heartbeat Daemon - runs Sovereign 24/7 as a background process.

Like OpenClaw's heartbeat, the daemon wakes up at configurable intervals,
checks for pending tasks in the queue, executes them, and sends notifications
when complete. It can also respond to inbound messages.

Usage:
    sovereign daemon start          # Start the daemon
    sovereign daemon start --detach # Start in background
    sovereign daemon stop           # Stop the daemon
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sovereign.config import SovereignConfig, load_config
from sovereign.core.task_queue import PersistentTask, TaskQueue, TaskStatus


class HeartbeatDaemon:
    """Background daemon that continuously processes tasks.

    Features:
    - Wakes up at configurable intervals (heartbeat)
    - Processes pending tasks from the persistent queue
    - Sends notifications when tasks complete
    - Writes a PID file for process management
    - Logs activity to ~/.sovereign/daemon.log
    - Graceful shutdown on SIGTERM/SIGINT
    """

    def __init__(
        self,
        config: SovereignConfig | None = None,
        interval_seconds: int | None = None,
    ) -> None:
        self.config = config or load_config()
        self.interval = interval_seconds or self.config.scheduler.heartbeat_interval_seconds
        self.queue = TaskQueue()
        self._running = False
        self._pid_file = os.path.join(self.config.data_dir, "daemon.pid")
        self._log_file = os.path.join(self.config.data_dir, "daemon.log")
        self._state_file = os.path.join(self.config.data_dir, "daemon_state.json")
        self._heartbeat_count = 0
        self._tasks_processed = 0
        self._started_at: str = ""

    def _write_log(self, message: str) -> None:
        """Append a log line to the daemon log file."""
        timestamp = datetime.now(timezone.utc).isoformat()
        line = f"[{timestamp}] {message}\n"
        Path(self._log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(line)

    def _write_pid(self) -> None:
        """Write current PID to file."""
        Path(self._pid_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self._pid_file, "w") as f:
            f.write(str(os.getpid()))

    def _remove_pid(self) -> None:
        """Remove PID file."""
        if os.path.exists(self._pid_file):
            os.remove(self._pid_file)

    def _save_state(self) -> None:
        """Save daemon state to disk."""
        state = {
            "running": self._running,
            "pid": os.getpid(),
            "started_at": self._started_at,
            "heartbeat_count": self._heartbeat_count,
            "tasks_processed": self._tasks_processed,
            "interval_seconds": self.interval,
            "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        }
        with open(self._state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    @staticmethod
    def get_state(data_dir: str | None = None) -> dict[str, Any]:
        """Read daemon state from disk."""
        if data_dir is None:
            data_dir = os.path.join(os.path.expanduser("~"), ".sovereign")
        state_file = os.path.join(data_dir, "daemon_state.json")
        if not os.path.exists(state_file):
            return {"running": False}
        try:
            with open(state_file, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"running": False}

    @staticmethod
    def get_pid(data_dir: str | None = None) -> int | None:
        """Read the daemon PID from file."""
        if data_dir is None:
            data_dir = os.path.join(os.path.expanduser("~"), ".sovereign")
        pid_file = os.path.join(data_dir, "daemon.pid")
        if not os.path.exists(pid_file):
            return None
        try:
            with open(pid_file) as f:
                return int(f.read().strip())
        except (ValueError, OSError):
            return None

    @staticmethod
    def is_running(data_dir: str | None = None) -> bool:
        """Check if the daemon is currently running."""
        pid = HeartbeatDaemon.get_pid(data_dir)
        if pid is None:
            return False
        try:
            os.kill(pid, 0)  # Signal 0 = check if process exists
            return True
        except OSError:
            return False

    def start(self) -> None:
        """Start the daemon (blocking)."""
        if self.is_running(self.config.data_dir):
            existing_pid = self.get_pid(self.config.data_dir)
            print(f"Daemon already running (PID {existing_pid})")
            return

        self._running = True
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._write_pid()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

        self._write_log(f"Daemon started (PID {os.getpid()}, interval {self.interval}s)")
        self._save_state()

        try:
            asyncio.run(self._run_loop())
        except KeyboardInterrupt:
            pass
        finally:
            self._shutdown()

    def stop(self) -> bool:
        """Stop a running daemon. Returns True if stopped."""
        pid = self.get_pid(self.config.data_dir)
        if pid is None:
            return False
        try:
            os.kill(pid, signal.SIGTERM)
            # Wait for it to stop
            for _ in range(10):
                time.sleep(0.5)
                try:
                    os.kill(pid, 0)
                except OSError:
                    break
            self._remove_pid()
            return True
        except OSError:
            self._remove_pid()
            return False

    def _handle_signal(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals gracefully."""
        self._write_log(f"Received signal {signum}, shutting down...")
        self._running = False

    def _shutdown(self) -> None:
        """Clean shutdown."""
        self._running = False
        self._write_log(
            f"Daemon stopped. Heartbeats: {self._heartbeat_count}, "
            f"Tasks processed: {self._tasks_processed}"
        )
        self._save_state()
        self._remove_pid()

    async def _run_loop(self) -> None:
        """Main heartbeat loop."""
        while self._running:
            self._heartbeat_count += 1
            self._write_log(f"Heartbeat #{self._heartbeat_count}")

            try:
                await self._process_pending_tasks()
            except Exception as e:
                self._write_log(f"ERROR in heartbeat: {e!s}")

            self._save_state()

            # Sleep in small increments so we can respond to signals
            for _ in range(self.interval):
                if not self._running:
                    break
                await asyncio.sleep(1)

    async def _process_pending_tasks(self) -> None:
        """Process all pending tasks in the queue."""
        while self._running:
            task = self.queue.get_next_task()
            if task is None:
                break

            self._write_log(f"Processing task {task.id[:8]}: {task.goal[:80]}")
            self.queue.update_status(task.id, TaskStatus.IN_PROGRESS)

            try:
                result = await self._execute_task(task)

                if result.get("success"):
                    self.queue.update_status(
                        task.id,
                        TaskStatus.COMPLETED,
                        output=result.get("output", "Done"),
                    )
                    self._write_log(f"Task {task.id[:8]} completed")
                else:
                    error = result.get("error", "Unknown error")
                    self.queue.update_status(
                        task.id, TaskStatus.FAILED, error=error,
                    )
                    self._write_log(f"Task {task.id[:8]} failed: {error}")

                    # Auto-retry if retries remain
                    if task.retry_count < task.max_retries:
                        self.queue.retry_task(task.id)
                        self._write_log(f"Task {task.id[:8]} queued for retry")

                self._tasks_processed += 1

                # Send notification
                await self._notify_completion(task, result)

            except Exception as e:
                self.queue.update_status(
                    task.id, TaskStatus.FAILED, error=str(e),
                )
                self._write_log(f"Task {task.id[:8]} error: {e!s}")

    async def _execute_task(self, task: PersistentTask) -> dict[str, Any]:
        """Execute a single task using the agent system."""
        try:
            from sovereign.core.agent import Agent, AgentRole, TaskContext

            role = AgentRole.GENERAL
            if task.agent_role != "general":
                try:
                    role = AgentRole(task.agent_role)
                except ValueError:
                    role = AgentRole.GENERAL

            agent = Agent(config=self.config, role=role)

            task_ctx = TaskContext(
                goal=task.goal,
                priority=task.priority,
                budget_usd=task.budget_usd,
            )

            result = await agent.run_task(task_ctx)

            return {
                "success": result.success,
                "output": result.output or "",
                "error": result.error,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _notify_completion(
        self, task: PersistentTask, result: dict[str, Any],
    ) -> None:
        """Send a notification when a task completes."""
        from sovereign.core.notifier import Notifier

        notifier = Notifier(self.config)
        status = "completed" if result.get("success") else "failed"
        summary = result.get("output", result.get("error", ""))[:500]

        await notifier.notify(
            title=f"Sovereign Task {status.title()}",
            body=f"Goal: {task.goal}\nStatus: {status}\n\n{summary}",
            level="info" if result.get("success") else "error",
        )


def daemonize() -> None:
    """Fork the process to run as a true background daemon (Unix only)."""
    if sys.platform == "win32":
        print("Daemonize not supported on Windows. Run without --detach.")
        return

    pid = os.fork()
    if pid > 0:
        # Parent exits
        print(f"Daemon started in background (PID {pid})")
        sys.exit(0)

    # Child continues as daemon
    os.setsid()

    # Redirect stdout/stderr to log
    data_dir = os.path.join(os.path.expanduser("~"), ".sovereign")
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    log_path = os.path.join(data_dir, "daemon_stdout.log")

    with open(log_path, "a") as log_f:
        os.dup2(log_f.fileno(), sys.stdout.fileno())
        os.dup2(log_f.fileno(), sys.stderr.fileno())

    daemon = HeartbeatDaemon()
    daemon.start()
