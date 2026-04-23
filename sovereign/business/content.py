"""Content Creation Pipeline - automated content generation and management.

Manages content creation workflows for blogs, social media, emails,
and marketing materials. Tracks content performance and optimizes.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig


class ContentType(str, Enum):
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    NEWSLETTER = "newsletter"
    LANDING_PAGE = "landing_page"
    DOCUMENTATION = "documentation"
    AD_COPY = "ad_copy"
    VIDEO_SCRIPT = "video_script"
    PRESS_RELEASE = "press_release"
    CASE_STUDY = "case_study"


class ContentStatus(str, Enum):
    IDEA = "idea"
    OUTLINE = "outline"
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentPiece(BaseModel):
    """A single piece of content in the pipeline."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content_type: ContentType
    status: ContentStatus = ContentStatus.IDEA
    topic: str = ""
    outline: str = ""
    body: str = ""
    keywords: list[str] = Field(default_factory=list)
    target_audience: str = ""
    platform: str = ""  # Where it will be published
    call_to_action: str = ""

    # Performance metrics
    views: int = 0
    clicks: int = 0
    conversions: int = 0
    engagement_rate: float = 0.0

    # Metadata
    author: str = "sovereign"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContentCalendar(BaseModel):
    """Schedule for planned content."""

    entries: list[dict[str, Any]] = Field(default_factory=list)


class ContentPipeline:
    """Manages the content creation and publishing pipeline.

    Features:
    - Content ideation from market research
    - Outline and draft generation
    - SEO keyword targeting
    - Multi-platform publishing
    - Performance tracking and optimization
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._content: dict[str, ContentPiece] = {}
        self._store_path = Path(config.data_dir) / "content.json"
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if self._store_path.exists():
            try:
                data = json.loads(self._store_path.read_text())
                self._content = {
                    cid: ContentPiece(**cdata) for cid, cdata in data.items()
                }
            except (json.JSONDecodeError, Exception):
                self._content = {}

    def _save(self) -> None:
        data = {
            cid: piece.model_dump(mode="json") for cid, piece in self._content.items()
        }
        self._store_path.write_text(json.dumps(data, indent=2, default=str))

    def create_content(self, piece: ContentPiece) -> ContentPiece:
        """Add a new content piece to the pipeline."""
        self._content[piece.id] = piece
        self._save()
        return piece

    def update_content(self, content_id: str, **updates: Any) -> ContentPiece | None:
        """Update a content piece."""
        piece = self._content.get(content_id)
        if not piece:
            return None

        for key, value in updates.items():
            if hasattr(piece, key):
                setattr(piece, key, value)

        if updates.get("status") == ContentStatus.PUBLISHED:
            piece.published_at = datetime.now(timezone.utc)

        self._save()
        return piece

    def get_by_status(self, status: ContentStatus) -> list[ContentPiece]:
        """Get content by status."""
        return [c for c in self._content.values() if c.status == status]

    def get_by_type(self, content_type: ContentType) -> list[ContentPiece]:
        """Get content by type."""
        return [c for c in self._content.values() if c.content_type == content_type]

    def get_top_performing(self, limit: int = 10) -> list[ContentPiece]:
        """Get top performing published content by engagement."""
        published = [
            c for c in self._content.values() if c.status == ContentStatus.PUBLISHED
        ]
        return sorted(published, key=lambda c: c.engagement_rate, reverse=True)[:limit]

    def generate_content_ideas(
        self,
        topics: list[str],
        content_types: list[ContentType] | None = None,
        count: int = 5,
    ) -> list[ContentPiece]:
        """Generate content ideas based on topics and past performance.

        In production, this uses the LLM to generate contextually relevant
        content ideas based on market trends, competitor analysis, and
        past content performance.
        """
        types = content_types or [ContentType.BLOG_POST, ContentType.SOCIAL_MEDIA]
        ideas: list[ContentPiece] = []

        for topic in topics[:count]:
            for ct in types:
                idea = ContentPiece(
                    title=f"Content about: {topic}",
                    content_type=ct,
                    status=ContentStatus.IDEA,
                    topic=topic,
                    keywords=topic.lower().split(),
                )
                ideas.append(idea)
                self._content[idea.id] = idea

        self._save()
        return ideas[:count]

    def get_pipeline_stats(self) -> dict[str, Any]:
        """Get content pipeline analytics."""
        total = len(self._content)
        by_status: dict[str, int] = {}
        by_type: dict[str, int] = {}
        total_views = 0
        total_clicks = 0
        total_conversions = 0

        for piece in self._content.values():
            by_status[piece.status.value] = by_status.get(piece.status.value, 0) + 1
            by_type[piece.content_type.value] = by_type.get(piece.content_type.value, 0) + 1
            total_views += piece.views
            total_clicks += piece.clicks
            total_conversions += piece.conversions

        return {
            "total_content": total,
            "by_status": by_status,
            "by_type": by_type,
            "total_views": total_views,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "avg_engagement_rate": (
                sum(c.engagement_rate for c in self._content.values()) / max(total, 1)
            ),
        }

    @property
    def total_content(self) -> int:
        return len(self._content)
