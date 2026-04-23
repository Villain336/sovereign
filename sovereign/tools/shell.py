"""Shell Tool - execute shell commands with sandboxing and safety checks.

Provides controlled access to the system shell for running commands,
scripts, and system operations.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class ShellTool(Tool):
    """Execute shell commands with safety controls."""

    name = "shell"
    description = (
        "Execute a shell command and return its output. Use this for running scripts, "
        "managing files, installing packages, and system operations. Commands are "
        "validated against a blocklist before execution."
    )
    parameters = [
        ToolParameter(
            name="command",
            description="The shell command to execute",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="working_dir",
            description="Working directory for the command",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="timeout",
            description="Timeout in seconds (default 60)",
            param_type="integer",
            required=False,
            default=60,
        ),
    ]
    category = "system"
    risk_level = 0.6
    requires_approval = False

    def __init__(
        self,
        blocked_commands: list[str] | None = None,
        allowed_dirs: list[str] | None = None,
    ) -> None:
        self._blocked_commands = blocked_commands or [
            "rm -rf /",
            "mkfs",
            "dd if=",
            ":(){ :|:& };:",
            "chmod -R 777 /",
            "> /dev/sda",
        ]
        self._allowed_dirs = allowed_dirs

    async def execute(self, **kwargs: Any) -> ToolResult:
        command = kwargs.get("command", "")
        working_dir = kwargs.get("working_dir")
        timeout = kwargs.get("timeout", 60)

        if not command:
            return ToolResult(success=False, error="Command is required")

        # Safety check
        safety_error = self._check_safety(command)
        if safety_error:
            return ToolResult(success=False, error=safety_error)

        # Validate working directory
        if working_dir and not os.path.isdir(working_dir):
            return ToolResult(
                success=False,
                error=f"Working directory does not exist: {working_dir}",
            )

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return ToolResult(
                    success=False,
                    error=f"Command timed out after {timeout}s",
                    metadata={"command": command},
                )

            stdout_text = stdout.decode("utf-8", errors="replace")
            stderr_text = stderr.decode("utf-8", errors="replace")

            success = process.returncode == 0
            output = stdout_text
            if stderr_text and not success:
                output += f"\nSTDERR:\n{stderr_text}"

            return ToolResult(
                success=success,
                output=output,
                error=stderr_text if not success else None,
                metadata={
                    "command": command,
                    "return_code": process.returncode,
                    "working_dir": working_dir or os.getcwd(),
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Command execution failed: {str(e)}",
                metadata={"command": command},
            )

    def _check_safety(self, command: str) -> str | None:
        """Check if the command is safe to execute."""
        command_lower = command.lower().strip()

        for blocked in self._blocked_commands:
            if blocked.lower() in command_lower:
                return f"Command blocked: contains '{blocked}'"

        return None
