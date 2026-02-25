"""Inbound Message Handler - receive messages and trigger agent actions.

Like OpenClaw's WhatsApp/Telegram integration, this allows users to
text Sovereign and have it act on messages autonomously. Supports:
- Telegram bot (webhook + polling)
- Slack bot (events API)
- Generic webhook (any HTTP POST)

Messages are parsed, queued as tasks, and processed by the daemon.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from sovereign.config import SovereignConfig
from sovereign.core.task_queue import TaskQueue


class InboundMessage:
    """Represents an incoming message from any channel."""

    def __init__(
        self,
        text: str,
        sender: str = "",
        channel: str = "unknown",
        channel_id: str = "",
        reply_to: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.text = text
        self.sender = sender
        self.channel = channel
        self.channel_id = channel_id
        self.reply_to = reply_to
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()


class InboundRouter:
    """Routes inbound messages to the task queue.

    Parses messages, determines intent, and creates tasks.
    Also maintains a conversation log for context.
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self.queue = TaskQueue()
        self._conversation_log = os.path.join(
            config.data_dir, "conversations.json",
        )

    async def handle_message(self, message: InboundMessage) -> dict[str, Any]:
        """Process an inbound message and queue it as a task.

        Returns a response dict with task_id and acknowledgment.
        """
        # Log the conversation
        self._log_message(message)

        # Parse intent from message
        intent = self._parse_intent(message.text)

        # Create a task from the message
        task_id = self.queue.add_task(
            goal=message.text,
            priority=intent.get("priority", 5),
            agent_role=intent.get("agent_role", "general"),
            metadata={
                "source": message.channel,
                "sender": message.sender,
                "channel_id": message.channel_id,
                "reply_to": message.reply_to,
                "intent": intent,
            },
        )

        return {
            "task_id": task_id,
            "acknowledged": True,
            "message": f"Got it! Working on: {message.text[:100]}",
            "intent": intent,
        }

    def _parse_intent(self, text: str) -> dict[str, Any]:
        """Parse the intent of a message to determine priority and agent."""
        text_lower = text.lower().strip()

        # Urgent keywords
        urgent_words = {"urgent", "asap", "immediately", "now", "critical", "emergency"}
        is_urgent = any(w in text_lower for w in urgent_words)

        # Agent routing based on keywords
        agent_role = "general"
        if any(w in text_lower for w in ["research", "find", "look up", "search"]):
            agent_role = "researcher"
        elif any(w in text_lower for w in ["code", "build", "fix", "debug", "program"]):
            agent_role = "coder"
        elif any(w in text_lower for w in ["market", "advertise", "campaign", "content", "post"]):
            agent_role = "marketer"
        elif any(w in text_lower for w in ["analyze", "report", "metric", "data", "numbers"]):
            agent_role = "analyst"
        elif any(w in text_lower for w in ["email", "call", "reach out", "contact", "message"]):
            agent_role = "outreach"

        return {
            "priority": 2 if is_urgent else 5,
            "agent_role": agent_role,
            "is_urgent": is_urgent,
        }

    def _log_message(self, message: InboundMessage) -> None:
        """Log inbound message to conversation history."""
        conversations = self._load_conversations()
        conversations.append({
            "text": message.text,
            "sender": message.sender,
            "channel": message.channel,
            "timestamp": message.timestamp,
            "metadata": message.metadata,
        })
        # Keep last 5000
        if len(conversations) > 5000:
            conversations = conversations[-5000:]
        with open(self._conversation_log, "w", encoding="utf-8") as f:
            json.dump(conversations, f, indent=2)

    def _load_conversations(self) -> list[dict[str, Any]]:
        """Load conversation history."""
        if not os.path.exists(self._conversation_log):
            return []
        try:
            with open(self._conversation_log, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def get_conversation_context(
        self, channel_id: str = "", limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Get recent conversation context for a channel."""
        conversations = self._load_conversations()
        if channel_id:
            conversations = [
                c for c in conversations
                if c.get("metadata", {}).get("channel_id") == channel_id
            ]
        return conversations[-limit:]


def create_telegram_webhook_handler(config: SovereignConfig) -> Any:
    """Create a FastAPI router for Telegram webhook.

    Usage: Include this router in your FastAPI app to receive
    Telegram messages and process them as tasks.
    """
    try:
        from fastapi import APIRouter, Request
    except ImportError:
        return None

    router = APIRouter(prefix="/webhook/telegram", tags=["telegram"])
    inbound = InboundRouter(config)

    @router.post("/")
    async def telegram_webhook(request: Request) -> dict[str, Any]:
        """Handle incoming Telegram webhook."""
        data = await request.json()

        # Extract message from Telegram update
        msg = data.get("message", {})
        text = msg.get("text", "")
        sender = msg.get("from", {}).get("username", "unknown")
        chat_id = str(msg.get("chat", {}).get("id", ""))

        if not text:
            return {"ok": True, "skipped": True}

        message = InboundMessage(
            text=text,
            sender=sender,
            channel="telegram",
            channel_id=chat_id,
            reply_to=chat_id,
        )

        result = await inbound.handle_message(message)

        # Send acknowledgment back to Telegram
        token = config.channels.telegram_bot_token
        if token and chat_id:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": result.get("message", "Working on it..."),
                    },
                )

        return {"ok": True, "task_id": result.get("task_id")}

    return router


def create_slack_webhook_handler(config: SovereignConfig) -> Any:
    """Create a FastAPI router for Slack events.

    Usage: Include this router in your FastAPI app to receive
    Slack messages and process them as tasks.
    """
    try:
        from fastapi import APIRouter, Request
    except ImportError:
        return None

    router = APIRouter(prefix="/webhook/slack", tags=["slack"])
    inbound = InboundRouter(config)

    @router.post("/events")
    async def slack_events(request: Request) -> dict[str, Any]:
        """Handle Slack Events API."""
        data = await request.json()

        # Handle Slack URL verification challenge
        if data.get("type") == "url_verification":
            return {"challenge": data.get("challenge", "")}

        event = data.get("event", {})
        if event.get("type") != "message":
            return {"ok": True}

        # Ignore bot messages
        if event.get("bot_id"):
            return {"ok": True}

        text = event.get("text", "")
        sender = event.get("user", "unknown")
        channel_id = event.get("channel", "")

        if not text:
            return {"ok": True}

        message = InboundMessage(
            text=text,
            sender=sender,
            channel="slack",
            channel_id=channel_id,
            reply_to=channel_id,
        )

        result = await inbound.handle_message(message)

        # Post acknowledgment back to Slack
        token = config.channels.slack_bot_token
        if token and channel_id:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    "https://slack.com/api/chat.postMessage",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "channel": channel_id,
                        "text": result.get("message", "Working on it..."),
                    },
                )

        return {"ok": True, "task_id": result.get("task_id")}

    return router


def create_generic_webhook_handler(config: SovereignConfig) -> Any:
    """Create a generic webhook handler for any HTTP POST.

    Accepts JSON with at minimum a "text" field.
    """
    try:
        from fastapi import APIRouter, Request
    except ImportError:
        return None

    router = APIRouter(prefix="/webhook", tags=["webhook"])
    inbound = InboundRouter(config)

    @router.post("/message")
    async def generic_webhook(request: Request) -> dict[str, Any]:
        """Handle generic webhook message."""
        data = await request.json()

        text = data.get("text", data.get("message", ""))
        if not text:
            return {"ok": False, "error": "No text/message field provided"}

        message = InboundMessage(
            text=text,
            sender=data.get("sender", "webhook"),
            channel="webhook",
            channel_id=data.get("channel_id", ""),
            metadata=data.get("metadata", {}),
        )

        result = await inbound.handle_message(message)
        return {"ok": True, **result}

    return router
