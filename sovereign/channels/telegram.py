"""Telegram Channel - send and receive messages via Telegram Bot API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from sovereign.channels.base import Channel, ChannelMessage


class TelegramChannel(Channel):
    """Telegram Bot integration for messaging."""

    name = "telegram"
    channel_type = "telegram"

    def __init__(
        self,
        bot_token: str = "",
        default_chat_id: str = "",
    ) -> None:
        self._bot_token = bot_token
        self._default_chat_id = default_chat_id
        self._base_url = f"https://api.telegram.org/bot{bot_token}"
        self._last_update_id = 0

    async def send_message(
        self,
        recipient: str,
        content: str,
        thread_id: str = "",
        attachments: list[dict[str, Any]] | None = None,
    ) -> ChannelMessage:
        """Send a message via Telegram."""
        chat_id = recipient or self._default_chat_id
        if not chat_id or not self._bot_token:
            return ChannelMessage(
                channel_type="telegram",
                content=content,
                metadata={"error": "Telegram not configured"},
            )

        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": content,
            "parse_mode": "Markdown",
        }
        if thread_id:
            payload["reply_to_message_id"] = thread_id

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._base_url}/sendMessage",
                    json=payload,
                )
                data = response.json()

            if data.get("ok"):
                result = data.get("result", {})
                return ChannelMessage(
                    channel_type="telegram",
                    sender="sovereign",
                    recipient=chat_id,
                    content=content,
                    thread_id=str(result.get("message_id", "")),
                    metadata={"message_id": result.get("message_id")},
                )
            else:
                return ChannelMessage(
                    channel_type="telegram",
                    content=content,
                    metadata={"error": data.get("description", "Unknown error")},
                )
        except Exception as e:
            return ChannelMessage(
                channel_type="telegram",
                content=content,
                metadata={"error": str(e)},
            )

    async def receive_messages(
        self,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[ChannelMessage]:
        """Receive recent messages using long polling."""
        if not self._bot_token:
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self._base_url}/getUpdates",
                    params={
                        "offset": self._last_update_id + 1,
                        "limit": limit,
                        "timeout": 1,
                    },
                    timeout=10.0,
                )
                data = response.json()

            if not data.get("ok"):
                return []

            messages: list[ChannelMessage] = []
            for update in data.get("result", []):
                self._last_update_id = max(
                    self._last_update_id, update.get("update_id", 0)
                )
                msg = update.get("message", {})
                if msg:
                    sender = msg.get("from", {})
                    messages.append(
                        ChannelMessage(
                            channel_type="telegram",
                            sender=sender.get("username", str(sender.get("id", ""))),
                            recipient=str(msg.get("chat", {}).get("id", "")),
                            content=msg.get("text", ""),
                            thread_id=str(msg.get("message_id", "")),
                            timestamp=datetime.fromtimestamp(
                                msg.get("date", 0), tz=timezone.utc
                            ),
                            metadata={
                                "message_id": msg.get("message_id"),
                                "chat_type": msg.get("chat", {}).get("type", ""),
                            },
                        )
                    )
            return messages

        except Exception:
            return []
