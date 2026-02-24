"""Business Analytics - metrics tracking, reporting, and insights.

Tracks key business metrics over time and generates insights
to inform decision-making and strategy adjustments.
"""

from __future__ import annotations

import json
import statistics
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig


class MetricType(str, Enum):
    REVENUE = "revenue"
    COST = "cost"
    LEADS = "leads"
    CONVERSIONS = "conversions"
    TRAFFIC = "traffic"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    CUSTOM = "custom"


class Metric(BaseModel):
    """A single metric data point."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    metric_type: MetricType
    value: float
    unit: str = ""
    tags: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class MetricSummary(BaseModel):
    """Summary statistics for a metric over a period."""

    name: str
    metric_type: MetricType
    period_start: datetime
    period_end: datetime
    count: int = 0
    total: float = 0.0
    average: float = 0.0
    median: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    std_dev: float = 0.0
    trend: str = "stable"  # up, down, stable
    change_pct: float = 0.0


class Insight(BaseModel):
    """An automatically generated business insight."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    severity: str = "info"  # info, warning, critical, opportunity
    metric_name: str = ""
    recommendation: str = ""
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BusinessAnalytics:
    """Business analytics engine for tracking metrics and generating insights.

    Features:
    - Time-series metric tracking
    - Trend analysis and anomaly detection
    - Automated insight generation
    - Period-over-period comparison
    - Dashboard data generation
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._metrics: list[Metric] = []
        self._insights: list[Insight] = []
        self._store_path = Path(config.data_dir) / "analytics.json"
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if self._store_path.exists():
            try:
                data = json.loads(self._store_path.read_text())
                self._metrics = [Metric(**m) for m in data.get("metrics", [])]
                self._insights = [Insight(**i) for i in data.get("insights", [])]
            except (json.JSONDecodeError, Exception):
                self._metrics = []
                self._insights = []

    def _save(self) -> None:
        data = {
            "metrics": [m.model_dump(mode="json") for m in self._metrics],
            "insights": [i.model_dump(mode="json") for i in self._insights],
        }
        self._store_path.write_text(json.dumps(data, indent=2, default=str))

    def track(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.CUSTOM,
        unit: str = "",
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Metric:
        """Track a metric data point."""
        metric = Metric(
            name=name,
            metric_type=metric_type,
            value=value,
            unit=unit,
            tags=tags or [],
            metadata=metadata or {},
        )
        self._metrics.append(metric)
        self._save()
        return metric

    def get_summary(
        self,
        name: str,
        days: int = 30,
    ) -> MetricSummary | None:
        """Get summary statistics for a metric over a period."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        values = [
            m.value
            for m in self._metrics
            if m.name == name and m.timestamp >= cutoff
        ]

        if not values:
            return None

        # Calculate trend
        trend = "stable"
        change_pct = 0.0
        if len(values) >= 4:
            first_half = values[: len(values) // 2]
            second_half = values[len(values) // 2 :]
            avg_first = statistics.mean(first_half)
            avg_second = statistics.mean(second_half)
            if avg_first > 0:
                change_pct = ((avg_second - avg_first) / avg_first) * 100
                if change_pct > 5:
                    trend = "up"
                elif change_pct < -5:
                    trend = "down"

        # Find metric type
        metric_type = MetricType.CUSTOM
        matching = [m for m in self._metrics if m.name == name]
        if matching:
            metric_type = matching[0].metric_type

        return MetricSummary(
            name=name,
            metric_type=metric_type,
            period_start=cutoff,
            period_end=datetime.now(timezone.utc),
            count=len(values),
            total=sum(values),
            average=statistics.mean(values),
            median=statistics.median(values),
            min_value=min(values),
            max_value=max(values),
            std_dev=statistics.stdev(values) if len(values) > 1 else 0.0,
            trend=trend,
            change_pct=change_pct,
        )

    def generate_insights(self) -> list[Insight]:
        """Automatically generate business insights from tracked metrics."""
        new_insights: list[Insight] = []

        # Get all unique metric names
        metric_names = set(m.name for m in self._metrics)

        for name in metric_names:
            summary = self.get_summary(name, days=30)
            if not summary or summary.count < 3:
                continue

            # Trend insights
            if summary.trend == "up" and summary.change_pct > 20:
                insight = Insight(
                    title=f"{name} is growing significantly",
                    description=(
                        f"{name} has increased by {summary.change_pct:.1f}% "
                        f"over the past 30 days (avg: {summary.average:.2f})"
                    ),
                    severity="opportunity",
                    metric_name=name,
                    recommendation="Consider scaling resources to capitalize on this growth",
                )
                new_insights.append(insight)

            elif summary.trend == "down" and summary.change_pct < -20:
                insight = Insight(
                    title=f"{name} is declining",
                    description=(
                        f"{name} has decreased by {abs(summary.change_pct):.1f}% "
                        f"over the past 30 days"
                    ),
                    severity="warning",
                    metric_name=name,
                    recommendation="Investigate the cause and adjust strategy",
                )
                new_insights.append(insight)

            # Anomaly detection (simple: value > 2 std devs from mean)
            if summary.std_dev > 0:
                recent = [
                    m for m in self._metrics
                    if m.name == name
                ]
                if recent:
                    latest = recent[-1]
                    z_score = abs(latest.value - summary.average) / summary.std_dev
                    if z_score > 2:
                        insight = Insight(
                            title=f"Anomaly detected in {name}",
                            description=(
                                f"Latest value ({latest.value:.2f}) is "
                                f"{z_score:.1f} standard deviations from the mean"
                            ),
                            severity="warning",
                            metric_name=name,
                            recommendation="Investigate this anomaly for root cause",
                        )
                        new_insights.append(insight)

        self._insights.extend(new_insights)
        self._save()
        return new_insights

    def get_dashboard_data(self) -> dict[str, Any]:
        """Generate data for a business dashboard."""
        metric_names = sorted(set(m.name for m in self._metrics))
        summaries: dict[str, Any] = {}

        for name in metric_names:
            summary = self.get_summary(name, days=30)
            if summary:
                summaries[name] = summary.model_dump(mode="json")

        return {
            "summaries": summaries,
            "recent_insights": [
                i.model_dump(mode="json") for i in self._insights[-10:]
            ],
            "total_metrics_tracked": len(self._metrics),
            "unique_metrics": len(metric_names),
        }
