"""Discord Channel - send and receive messages via Discord API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from sovereign.channels.base import Channel, ChannelMessage


class DiscordChannel(Channel):
    """Discord integration for community communication."""

    name = "discord"
    channel_type = "discord"

    def __init__(
        self,
        bot_token: str = "",
        default_channel_id: str = "",
    ) -> None:
        self._bot_token = bot_token
        self._default_channel_id = default_channel_id
        self._base_url = "https://discord.com/api/v10"

    async def send_message(
        self,
        recipient: str,
        content: str,
        thread_id: str = "",
        attachments: list[dict[str, Any]] | None = None,
    ) -> ChannelMessage:
        """Send a message to a Discord channel."""
        channel_id = recipient or self._default_channel_id
        if not channel_id or not self._bot_token:
            return ChannelMessage(
                channel_type="discord",
                content=content,
                metadata={"error": "Discord not configured"},
            )

        target_url = f"{self._base_url}/channels/{channel_id}/messages"
        if thread_id:
            target_url = f"{self._base_url}/channels/{thread_id}/messages"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    target_url,
                    headers={
                        "Authorization": f"Bot {self._bot_token}",
                        "Content-Type": "application/json",
                    },
                    json={"content": content},
                )
                data = response.json()

            return ChannelMessage(
                channel_type="discord",
                sender="sovereign",
                recipient=channel_id,
                content=content,
                thread_id=data.get("id", ""),
                metadata={"message_id": data.get("id")},
            )
        except Exception as e:
            return ChannelMessage(
                channel_type="discord",
                content=content,
                metadata={"error": str(e)},
            )

    async def receive_messages(
        self,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[ChannelMessage]:
        """Receive recent messages from the default Discord channel."""
        if not self._bot_token or not self._default_channel_id:
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self._base_url}/channels/{self._default_channel_id}/messages",
                    headers={"Authorization": f"Bot {self._bot_token}"},
                    params={"limit": limit},
                )
                data = response.json()

            if not isinstance(data, list):
                return []

            messages: list[ChannelMessage] = []
            for msg in data:
                messages.append(
                    ChannelMessage(
                        channel_type="discord",
                        sender=msg.get("author", {}).get("username", ""),
                        recipient=self._default_channel_id,
                        content=msg.get("content", ""),
                        thread_id=msg.get("id", ""),
                        metadata={"message_id": msg.get("id")},
                    )
                )
            return messages

        except Exception:
            return []
