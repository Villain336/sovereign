"""Revenue Tracker - track and optimize revenue streams.

Monitors multiple revenue streams, identifies opportunities,
and provides optimization recommendations.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig


class RevenueType(str, Enum):
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    COMMISSION = "commission"
    AFFILIATE = "affiliate"
    SERVICE = "service"
    PRODUCT = "product"


class RevenueStream(BaseModel):
    """A revenue stream being tracked."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    revenue_type: RevenueType
    description: str = ""
    monthly_target_usd: float = 0.0
    is_active: bool = True
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class RevenueEntry(BaseModel):
    """A single revenue data point."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stream_id: str
    amount_usd: float
    source: str = ""
    customer: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class RevenueTracker:
    """Track and optimize revenue across multiple streams.

    Features:
    - Multi-stream revenue tracking
    - Target vs actual comparison
    - Revenue trend analysis
    - Customer revenue attribution
    - Growth rate calculation
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._streams: dict[str, RevenueStream] = {}
        self._entries: list[RevenueEntry] = []
        self._store_path = Path(config.data_dir) / "revenue.json"
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if self._store_path.exists():
            try:
                data = json.loads(self._store_path.read_text())
                self._streams = {
                    sid: RevenueStream(**sdata) for sid, sdata in data.get("streams", {}).items()
                }
                self._entries = [RevenueEntry(**e) for e in data.get("entries", [])]
            except (json.JSONDecodeError, Exception):
                self._streams = {}
                self._entries = []

    def _save(self) -> None:
        data = {
            "streams": {sid: s.model_dump(mode="json") for sid, s in self._streams.items()},
            "entries": [e.model_dump(mode="json") for e in self._entries],
        }
        self._store_path.write_text(json.dumps(data, indent=2, default=str))

    def add_stream(self, stream: RevenueStream) -> RevenueStream:
        """Add a revenue stream to track."""
        self._streams[stream.id] = stream
        self._save()
        return stream

    def record_revenue(self, entry: RevenueEntry) -> RevenueEntry:
        """Record a revenue event."""
        self._entries.append(entry)
        self._save()
        return entry

    def get_total_revenue(self, days: int = 30) -> float:
        """Get total revenue over a period."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return sum(e.amount_usd for e in self._entries if e.timestamp >= cutoff)

    def get_revenue_by_stream(self, days: int = 30) -> dict[str, float]:
        """Get revenue breakdown by stream."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        by_stream: dict[str, float] = {}
        for entry in self._entries:
            if entry.timestamp >= cutoff:
                stream_name = self._streams.get(entry.stream_id, RevenueStream(name="unknown", revenue_type=RevenueType.ONE_TIME)).name
                by_stream[stream_name] = by_stream.get(stream_name, 0) + entry.amount_usd
        return by_stream

    def get_growth_rate(self, days: int = 30) -> float:
        """Calculate revenue growth rate (period over period)."""
        now = datetime.now(timezone.utc)
        current_period = sum(
            e.amount_usd for e in self._entries
            if e.timestamp >= now - timedelta(days=days)
        )
        previous_period = sum(
            e.amount_usd for e in self._entries
            if now - timedelta(days=days * 2) <= e.timestamp < now - timedelta(days=days)
        )
        if previous_period > 0:
            return ((current_period - previous_period) / previous_period) * 100
        return 0.0

    def get_mrr(self) -> float:
        """Calculate Monthly Recurring Revenue."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        recurring_streams = {
            sid for sid, s in self._streams.items()
            if s.revenue_type in (RevenueType.SUBSCRIPTION, RevenueType.RECURRING)
        }
        return sum(
            e.amount_usd for e in self._entries
            if e.stream_id in recurring_streams and e.timestamp >= cutoff
        )

    def get_performance_report(self) -> dict[str, Any]:
        """Generate a comprehensive revenue performance report."""
        total_30d = self.get_total_revenue(30)
        total_7d = self.get_total_revenue(7)
        mrr = self.get_mrr()
        growth = self.get_growth_rate(30)
        by_stream = self.get_revenue_by_stream(30)

        # Target vs actual
        target_vs_actual: dict[str, dict[str, float]] = {}
        for sid, stream in self._streams.items():
            if stream.is_active and stream.monthly_target_usd > 0:
                actual = sum(
                    e.amount_usd for e in self._entries
                    if e.stream_id == sid
                    and e.timestamp >= datetime.now(timezone.utc) - timedelta(days=30)
                )
                target_vs_actual[stream.name] = {
                    "target_usd": stream.monthly_target_usd,
                    "actual_usd": actual,
                    "achievement_pct": (actual / stream.monthly_target_usd) * 100,
                }

        return {
            "total_revenue_30d_usd": total_30d,
            "total_revenue_7d_usd": total_7d,
            "mrr_usd": mrr,
            "growth_rate_pct": growth,
            "revenue_by_stream": by_stream,
            "target_vs_actual": target_vs_actual,
            "active_streams": sum(1 for s in self._streams.values() if s.is_active),
        }
