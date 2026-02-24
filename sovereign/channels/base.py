"""Base Channel interface for all communication channels."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ChannelMessage(BaseModel):
    """A message received from or sent to a channel."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel_type: str = ""  # slack, discord, telegram, webhook, email
    sender: str = ""
    recipient: str = ""
    content: str = ""
    thread_id: str = ""
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class Channel(ABC):
    """Abstract base class for communication channels.

    Each channel implementation provides:
    - send_message: Send a message to a recipient/channel
    - receive_messages: Poll for new messages
    - send_notification: Send a notification/alert
    """

    name: str = ""
    channel_type: str = ""

    @abstractmethod
    async def send_message(
        self,
        recipient: str,
        content: str,
        thread_id: str = "",
        attachments: list[dict[str, Any]] | None = None,
    ) -> ChannelMessage:
        """Send a message."""
        ...

    @abstractmethod
    async def receive_messages(
        self,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[ChannelMessage]:
        """Receive recent messages."""
        ...

    async def send_notification(
        self,
        title: str,
        body: str,
        level: str = "info",
        recipient: str = "",
    ) -> ChannelMessage:
        """Send a notification/alert."""
        content = f"**[{level.upper()}]** {title}\n{body}"
        return await self.send_message(recipient=recipient, content=content)
