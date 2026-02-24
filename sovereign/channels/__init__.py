"""Communication channels - Slack, Discord, Telegram, email, webhooks."""

from sovereign.channels.base import Channel, ChannelMessage
from sovereign.channels.discord import DiscordChannel
from sovereign.channels.slack import SlackChannel
from sovereign.channels.telegram import TelegramChannel
from sovereign.channels.webhook import WebhookChannel

__all__ = [
    "Channel",
    "ChannelMessage",
    "SlackChannel",
    "DiscordChannel",
    "TelegramChannel",
    "WebhookChannel",
]
