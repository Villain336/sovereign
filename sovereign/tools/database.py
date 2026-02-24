"""Database Tool - interact with databases for data operations.

Supports SQLite (built-in) and can connect to PostgreSQL/MySQL via URLs.
Used by analyst agents for data querying and storage.
"""

from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path
from typing import Any

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class DatabaseTool(Tool):
    """Execute SQL queries against databases."""

    name = "database_query"
    description = (
        "Execute SQL queries against a SQLite database. Use this for storing data, "
        "querying information, creating tables, and data analysis. The database is "
        "automatically created if it doesn't exist."
    )
    parameters = [
        ToolParameter(
            name="query",
            description="SQL query to execute",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="database",
            description="Path to SQLite database file (default: sovereign.db)",
            param_type="string",
            required=False,
            default="sovereign.db",
        ),
        ToolParameter(
            name="params",
            description="Query parameters as a list (for parameterized queries)",
            param_type="list",
            required=False,
        ),
    ]
    category = "data"
    risk_level = 0.3

    # Dangerous SQL patterns to block
    BLOCKED_PATTERNS = ["drop database", "drop schema"]

    def __init__(self, default_db_path: str = "") -> None:
        self._default_db = default_db_path

    async def execute(self, **kwargs: Any) -> ToolResult:
        query = kwargs.get("query", "")
        database = kwargs.get("database", self._default_db or "sovereign.db")
        params = kwargs.get("params") or []

        if not query:
            return ToolResult(success=False, error="Query is required")

        # Safety check
        query_lower = query.lower().strip()
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in query_lower:
                return ToolResult(
                    success=False,
                    error=f"Query blocked: contains '{pattern}'",
                )

        try:
            # Ensure directory exists
            db_path = Path(database)
            db_path.parent.mkdir(parents=True, exist_ok=True)

            def _execute_query() -> dict[str, Any]:
                conn = sqlite3.connect(str(db_path))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                try:
                    cursor.execute(query, params)

                    # Check if it's a SELECT or similar query that returns rows
                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        rows = [dict(row) for row in cursor.fetchall()]
                        return {
                            "type": "query",
                            "columns": columns,
                            "rows": rows,
                            "row_count": len(rows),
                        }
                    else:
                        conn.commit()
                        return {
                            "type": "execute",
                            "rows_affected": cursor.rowcount,
                        }
                finally:
                    cursor.close()
                    conn.close()

            result = await asyncio.get_event_loop().run_in_executor(
                None, _execute_query
            )

            if result["type"] == "query":
                if result["rows"]:
                    # Format as table
                    output = self._format_table(result["columns"], result["rows"])
                else:
                    output = "Query returned 0 rows."
            else:
                output = f"Query executed. Rows affected: {result['rows_affected']}"

            return ToolResult(
                success=True,
                output=output,
                metadata={
                    "database": str(database),
                    **result,
                },
            )

        except sqlite3.Error as e:
            return ToolResult(
                success=False,
                error=f"SQL error: {str(e)}",
                metadata={"query": query},
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Database error: {str(e)}",
                metadata={"query": query},
            )

    def _format_table(
        self, columns: list[str], rows: list[dict[str, Any]]
    ) -> str:
        """Format query results as a readable table."""
        if not rows:
            return "No results."

        # Limit output
        display_rows = rows[:100]
        lines: list[str] = []

        # Header
        lines.append(" | ".join(columns))
        lines.append("-" * len(lines[0]))

        # Rows
        for row in display_rows:
            values = [str(row.get(col, "")) for col in columns]
            lines.append(" | ".join(values))

        if len(rows) > 100:
            lines.append(f"... ({len(rows) - 100} more rows)")

        return "\n".join(lines)
