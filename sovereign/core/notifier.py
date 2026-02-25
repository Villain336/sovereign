"""Notification System - alerts users when tasks complete.

Supports multiple notification channels:
- Desktop notifications (OS-level)
- File-based notifications (always works)
- Webhook (HTTP POST)
- Email (if SMTP configured)
- Telegram (if bot token configured)
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sovereign.config import SovereignConfig


class Notifier:
    """Multi-channel notification dispatcher.

    Writes all notifications to ~/.sovereign/notifications.json
    and additionally sends via configured channels (webhook, email, telegram).
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._notifications_file = os.path.join(config.data_dir, "notifications.json")
        Path(config.data_dir).mkdir(parents=True, exist_ok=True)

    async def notify(
        self,
        title: str,
        body: str,
        level: str = "info",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Send a notification through all configured channels."""
        notification = {
            "id": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
            "title": title,
            "body": body,
            "level": level,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "delivered_via": [],
        }

        # Always write to file
        self._write_to_file(notification)
        notification["delivered_via"].append("file")

        # Webhook
        if self.config.channels.webhook_secret:
            sent = await self._send_webhook(notification)
            if sent:
                notification["delivered_via"].append("webhook")

        # Telegram
        if self.config.channels.telegram_bot_token:
            sent = await self._send_telegram(notification)
            if sent:
                notification["delivered_via"].append("telegram")

        # Email
        if self.config.channels.email_smtp_host and self.config.channels.email_username:
            sent = await self._send_email(notification)
            if sent:
                notification["delivered_via"].append("email")

    def _write_to_file(self, notification: dict[str, Any]) -> None:
        """Write notification to the notifications JSON file."""
        notifications = self._load_notifications()
        notifications.append(notification)
        # Keep last 1000
        if len(notifications) > 1000:
            notifications = notifications[-1000:]
        with open(self._notifications_file, "w", encoding="utf-8") as f:
            json.dump(notifications, f, indent=2)

    def _load_notifications(self) -> list[dict[str, Any]]:
        """Load existing notifications from file."""
        if not os.path.exists(self._notifications_file):
            return []
        try:
            with open(self._notifications_file, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def get_recent(self, count: int = 20) -> list[dict[str, Any]]:
        """Get recent notifications."""
        notifications = self._load_notifications()
        return notifications[-count:]

    def get_unread(self) -> list[dict[str, Any]]:
        """Get notifications that haven't been marked as read."""
        notifications = self._load_notifications()
        return [n for n in notifications if not n.get("read")]

    def mark_read(self, notification_id: str) -> None:
        """Mark a notification as read."""
        notifications = self._load_notifications()
        for n in notifications:
            if n.get("id") == notification_id:
                n["read"] = True
                break
        with open(self._notifications_file, "w", encoding="utf-8") as f:
            json.dump(notifications, f, indent=2)

    async def _send_webhook(self, notification: dict[str, Any]) -> bool:
        """Send notification via webhook."""
        webhook_url = os.environ.get("SOVEREIGN_WEBHOOK_URL", "")
        if not webhook_url:
            return False
        try:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    webhook_url,
                    json=notification,
                    headers={"X-Webhook-Secret": self.config.channels.webhook_secret},
                )
                return resp.status_code < 400
        except Exception:
            return False

    async def _send_telegram(self, notification: dict[str, Any]) -> bool:
        """Send notification via Telegram bot."""
        token = self.config.channels.telegram_bot_token
        chat_id = os.environ.get("SOVEREIGN_TELEGRAM_CHAT_ID", "")
        if not token or not chat_id:
            return False

        text = f"*{notification['title']}*\n\n{notification['body']}"

        try:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": "Markdown",
                    },
                )
                return resp.status_code == 200
        except Exception:
            return False

    async def _send_email(self, notification: dict[str, Any]) -> bool:
        """Send notification via email."""
        try:
            import smtplib
            from email.mime.text import MIMEText

            msg = MIMEText(notification["body"])
            msg["Subject"] = f"[Sovereign] {notification['title']}"
            msg["From"] = self.config.channels.email_username
            msg["To"] = self.config.channels.email_username  # Self-notify

            with smtplib.SMTP(
                self.config.channels.email_smtp_host,
                self.config.channels.email_smtp_port,
            ) as server:
                server.starttls()
                server.login(
                    self.config.channels.email_username,
                    self.config.channels.email_password,
                )
                server.send_message(msg)
            return True
        except Exception:
            return False
