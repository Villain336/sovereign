"""Webhook Channel - receive and send webhook notifications."""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime
from typing import Any

import httpx

from sovereign.channels.base import Channel, ChannelMessage


class WebhookChannel(Channel):
    """Webhook integration for event-driven communication.

    Supports both sending webhooks (outgoing) and receiving
    webhook callbacks (incoming) for event-driven automation.
    """

    name = "webhook"
    channel_type = "webhook"

    def __init__(
        self,
        secret: str = "",
        default_url: str = "",
    ) -> None:
        self._secret = secret
        self._default_url = default_url
        self._received: list[ChannelMessage] = []

    async def send_message(
        self,
        recipient: str,
        content: str,
        thread_id: str = "",
        attachments: list[dict[str, Any]] | None = None,
    ) -> ChannelMessage:
        """Send a webhook to a URL."""
        url = recipient or self._default_url
        if not url:
            return ChannelMessage(
                channel_type="webhook",
                content=content,
                metadata={"error": "No webhook URL specified"},
            )

        payload = {
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "sovereign",
        }
        if thread_id:
            payload["thread_id"] = thread_id

        headers: dict[str, str] = {"Content-Type": "application/json"}

        # Sign the payload if secret is configured
        if self._secret:
            body = json.dumps(payload)
            signature = hmac.new(
                self._secret.encode(), body.encode(), hashlib.sha256
            ).hexdigest()
            headers["X-Sovereign-Signature"] = f"sha256={signature}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)

            return ChannelMessage(
                channel_type="webhook",
                sender="sovereign",
                recipient=url,
                content=content,
                metadata={
                    "status_code": response.status_code,
                    "url": url,
                },
            )
        except Exception as e:
            return ChannelMessage(
                channel_type="webhook",
                content=content,
                metadata={"error": str(e), "url": url},
            )

    async def receive_messages(
        self,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[ChannelMessage]:
        """Get received webhook messages."""
        messages = self._received[-limit:]
        if since:
            messages = [m for m in messages if m.timestamp >= since]
        return messages

    def process_incoming(
        self,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> ChannelMessage | None:
        """Process an incoming webhook payload.

        Validates the signature if a secret is configured.
        """
        headers = headers or {}

        # Verify signature if secret is configured
        if self._secret:
            signature = headers.get("X-Sovereign-Signature", "")
            body = json.dumps(payload)
            expected = hmac.new(
                self._secret.encode(), body.encode(), hashlib.sha256
            ).hexdigest()
            expected_sig = f"sha256={expected}"
            if not hmac.compare_digest(signature, expected_sig):
                return None

        message = ChannelMessage(
            channel_type="webhook",
            sender=payload.get("source", "external"),
            content=payload.get("content", json.dumps(payload)),
            metadata=payload,
        )
        self._received.append(message)
        return message
