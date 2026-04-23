"""Code Executor Tool - execute code in a sandboxed environment.

Supports Python, JavaScript, and shell scripts with output capture.
Uses subprocess isolation for safety.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from typing import Any

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class CodeExecutorTool(Tool):
    """Execute code snippets in a sandboxed environment."""

    name = "code_executor"
    description = (
        "Execute code in Python, JavaScript, or shell. The code runs in an isolated "
        "environment and stdout/stderr are captured. Use this for data processing, "
        "calculations, testing code snippets, and automation scripts."
    )
    parameters = [
        ToolParameter(
            name="code",
            description="The code to execute",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="language",
            description="Programming language: python, javascript, shell",
            param_type="string",
            required=False,
            default="python",
            enum=["python", "javascript", "shell"],
        ),
        ToolParameter(
            name="timeout",
            description="Execution timeout in seconds (default 30)",
            param_type="integer",
            required=False,
            default=30,
        ),
    ]
    category = "code"
    risk_level = 0.5

    LANGUAGE_COMMANDS = {
        "python": "python3",
        "javascript": "node",
        "shell": "bash",
    }

    LANGUAGE_EXTENSIONS = {
        "python": ".py",
        "javascript": ".js",
        "shell": ".sh",
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        timeout = kwargs.get("timeout", 30)

        if not code:
            return ToolResult(success=False, error="Code is required")

        if language not in self.LANGUAGE_COMMANDS:
            return ToolResult(
                success=False,
                error=f"Unsupported language: {language}. Use: {list(self.LANGUAGE_COMMANDS.keys())}",
            )

        interpreter = self.LANGUAGE_COMMANDS[language]
        extension = self.LANGUAGE_EXTENSIONS[language]

        try:
            # Write code to a temporary file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=extension, delete=False
            ) as f:
                f.write(code)
                temp_path = f.name

            try:
                process = await asyncio.create_subprocess_exec(
                    interpreter,
                    temp_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), timeout=timeout
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    return ToolResult(
                        success=False,
                        error=f"Code execution timed out after {timeout}s",
                        metadata={"language": language},
                    )

                stdout_text = stdout.decode("utf-8", errors="replace")
                stderr_text = stderr.decode("utf-8", errors="replace")

                success = process.returncode == 0
                output = stdout_text
                if stderr_text and not success:
                    output += f"\nErrors:\n{stderr_text}"

                return ToolResult(
                    success=success,
                    output=output,
                    error=stderr_text if not success else None,
                    metadata={
                        "language": language,
                        "return_code": process.returncode,
                    },
                )

            finally:
                os.unlink(temp_path)

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Code execution failed: {str(e)}",
                metadata={"language": language},
            )
