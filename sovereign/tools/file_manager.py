"""File Manager Tool - file system operations with safety controls.

Read, write, list, and manage files and directories.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class FileReadTool(Tool):
    """Read file contents."""

    name = "file_read"
    description = "Read the contents of a file. Returns the file text content."
    parameters = [
        ToolParameter(
            name="path",
            description="Absolute path to the file to read",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="max_lines",
            description="Maximum number of lines to read (default: all)",
            param_type="integer",
            required=False,
        ),
    ]
    category = "filesystem"
    risk_level = 0.1

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", "")
        max_lines = kwargs.get("max_lines")

        if not path:
            return ToolResult(success=False, error="Path is required")

        file_path = Path(path)
        if not file_path.exists():
            return ToolResult(success=False, error=f"File not found: {path}")
        if not file_path.is_file():
            return ToolResult(success=False, error=f"Not a file: {path}")

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            if max_lines:
                lines = content.split("\n")
                content = "\n".join(lines[:max_lines])
                if len(lines) > max_lines:
                    content += f"\n... ({len(lines) - max_lines} more lines)"

            return ToolResult(
                success=True,
                output=content,
                metadata={
                    "path": path,
                    "size_bytes": file_path.stat().st_size,
                    "lines": content.count("\n") + 1,
                },
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Read failed: {str(e)}")


class FileWriteTool(Tool):
    """Write content to a file."""

    name = "file_write"
    description = (
        "Write content to a file. Creates the file if it doesn't exist, "
        "or overwrites existing content."
    )
    parameters = [
        ToolParameter(
            name="path",
            description="Absolute path to the file to write",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="content",
            description="Content to write to the file",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="append",
            description="Append to existing file instead of overwriting (default: false)",
            param_type="boolean",
            required=False,
            default=False,
        ),
    ]
    category = "filesystem"
    risk_level = 0.3

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", "")
        content = kwargs.get("content", "")
        append = kwargs.get("append", False)

        if not path:
            return ToolResult(success=False, error="Path is required")

        file_path = Path(path)

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            mode = "a" if append else "w"
            file_path.write_text(content, encoding="utf-8") if not append else \
                open(file_path, mode, encoding="utf-8").write(content)

            return ToolResult(
                success=True,
                output=f"Written {len(content)} characters to {path}",
                metadata={
                    "path": path,
                    "size_bytes": file_path.stat().st_size,
                    "mode": "append" if append else "write",
                },
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Write failed: {str(e)}")


class FileListTool(Tool):
    """List files and directories."""

    name = "file_list"
    description = "List files and directories at a given path."
    parameters = [
        ToolParameter(
            name="path",
            description="Directory path to list",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="recursive",
            description="List recursively (default: false)",
            param_type="boolean",
            required=False,
            default=False,
        ),
        ToolParameter(
            name="pattern",
            description="Glob pattern to filter files (e.g., '*.py')",
            param_type="string",
            required=False,
        ),
    ]
    category = "filesystem"
    risk_level = 0.1

    async def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", "")
        recursive = kwargs.get("recursive", False)
        pattern = kwargs.get("pattern")

        if not path:
            return ToolResult(success=False, error="Path is required")

        dir_path = Path(path)
        if not dir_path.exists():
            return ToolResult(success=False, error=f"Path not found: {path}")
        if not dir_path.is_dir():
            return ToolResult(success=False, error=f"Not a directory: {path}")

        try:
            entries: list[str] = []

            if pattern:
                glob_method = dir_path.rglob if recursive else dir_path.glob
                for item in sorted(glob_method(pattern)):
                    rel_path = item.relative_to(dir_path)
                    marker = "/" if item.is_dir() else ""
                    entries.append(f"{rel_path}{marker}")
            else:
                if recursive:
                    for item in sorted(dir_path.rglob("*")):
                        rel_path = item.relative_to(dir_path)
                        marker = "/" if item.is_dir() else ""
                        entries.append(f"{rel_path}{marker}")
                else:
                    for item in sorted(dir_path.iterdir()):
                        marker = "/" if item.is_dir() else ""
                        entries.append(f"{item.name}{marker}")

            output = "\n".join(entries) if entries else "(empty directory)"
            return ToolResult(
                success=True,
                output=output,
                metadata={"path": path, "entry_count": len(entries)},
            )
        except Exception as e:
            return ToolResult(success=False, error=f"List failed: {str(e)}")
