"""Slack Channel - send and receive messages via Slack API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from sovereign.channels.base import Channel, ChannelMessage


class SlackChannel(Channel):
    """Slack integration for team communication.

    Uses the Slack Web API for sending messages and
    receiving notifications. Supports channels and DMs.
    """

    name = "slack"
    channel_type = "slack"

    def __init__(
        self,
        bot_token: str = "",
        app_token: str = "",
        default_channel: str = "",
    ) -> None:
        self._bot_token = bot_token
        self._app_token = app_token
        self._default_channel = default_channel
        self._base_url = "https://slack.com/api"

    async def send_message(
        self,
        recipient: str,
        content: str,
        thread_id: str = "",
        attachments: list[dict[str, Any]] | None = None,
    ) -> ChannelMessage:
        """Send a message to a Slack channel or DM."""
        channel = recipient or self._default_channel
        if not channel:
            return ChannelMessage(
                channel_type="slack",
                content=content,
                metadata={"error": "No channel specified"},
            )

        if not self._bot_token:
            return ChannelMessage(
                channel_type="slack",
                content=content,
                metadata={"error": "Slack bot token not configured"},
            )

        payload: dict[str, Any] = {
            "channel": channel,
            "text": content,
        }
        if thread_id:
            payload["thread_ts"] = thread_id

        if attachments:
            payload["attachments"] = attachments

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._base_url}/chat.postMessage",
                    headers={"Authorization": f"Bearer {self._bot_token}"},
                    json=payload,
                )
                data = response.json()

            if data.get("ok"):
                return ChannelMessage(
                    channel_type="slack",
                    sender="sovereign",
                    recipient=channel,
                    content=content,
                    thread_id=data.get("ts", ""),
                    metadata={"slack_ts": data.get("ts"), "channel": channel},
                )
            else:
                return ChannelMessage(
                    channel_type="slack",
                    content=content,
                    metadata={"error": data.get("error", "Unknown error")},
                )
        except Exception as e:
            return ChannelMessage(
                channel_type="slack",
                content=content,
                metadata={"error": str(e)},
            )

    async def receive_messages(
        self,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[ChannelMessage]:
        """Receive recent messages from the default Slack channel."""
        if not self._bot_token or not self._default_channel:
            return []

        params: dict[str, Any] = {
            "channel": self._default_channel,
            "limit": limit,
        }
        if since:
            params["oldest"] = str(since.timestamp())

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self._base_url}/conversations.history",
                    headers={"Authorization": f"Bearer {self._bot_token}"},
                    params=params,
                )
                data = response.json()

            if not data.get("ok"):
                return []

            messages: list[ChannelMessage] = []
            for msg in data.get("messages", []):
                messages.append(
                    ChannelMessage(
                        channel_type="slack",
                        sender=msg.get("user", ""),
                        recipient=self._default_channel,
                        content=msg.get("text", ""),
                        thread_id=msg.get("thread_ts", ""),
                        timestamp=datetime.fromtimestamp(
                            float(msg.get("ts", 0)), tz=timezone.utc
                        ),
                        metadata={"slack_ts": msg.get("ts")},
                    )
                )
            return messages

        except Exception:
            return []
