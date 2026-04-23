"""Twilio Tool - SMS, voice calls, and WhatsApp messaging.

Enables the agent to communicate with humans via phone:
- Send/receive SMS messages
- Make automated voice calls with text-to-speech
- Send WhatsApp messages
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class SMSSendTool(Tool):
    """Send SMS messages via Twilio."""

    name = "sms_send"
    description = (
        "Send an SMS text message to a phone number. Use this for outreach, "
        "notifications, appointment reminders, sales follow-ups, and any "
        "communication that needs to reach someone's phone."
    )
    parameters = [
        ToolParameter(
            name="to",
            description="Recipient phone number in E.164 format (e.g., +15551234567)",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="body",
            description="The text message content (max 1600 characters)",
            param_type="string",
            required=True,
        ),
    ]
    category = "communication"
    risk_level = 0.5
    requires_approval = True

    def __init__(
        self,
        account_sid: str = "",
        auth_token: str = "",
        from_number: str = "",
    ) -> None:
        self._account_sid = account_sid or os.environ.get("TWILIO_ACCOUNT_SID", "")
        self._auth_token = auth_token or os.environ.get("TWILIO_AUTH_TOKEN", "")
        self._from_number = from_number or os.environ.get("TWILIO_PHONE_NUMBER", "")

    async def execute(self, **kwargs: Any) -> ToolResult:
        to = kwargs.get("to", "")
        body = kwargs.get("body", "")

        if not to or not body:
            return ToolResult(success=False, error="'to' and 'body' are required")

        if not self._account_sid or not self._auth_token or not self._from_number:
            return ToolResult(
                success=False,
                error=(
                    "Twilio not configured. Set TWILIO_ACCOUNT_SID, "
                    "TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables."
                ),
            )

        # Truncate to Twilio limit
        body = body[:1600]

        try:
            url = (
                f"https://api.twilio.com/2010-04-01/Accounts/"
                f"{self._account_sid}/Messages.json"
            )

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    auth=(self._account_sid, self._auth_token),
                    data={
                        "To": to,
                        "From": self._from_number,
                        "Body": body,
                    },
                )

            if response.status_code in (200, 201):
                data = response.json()
                return ToolResult(
                    success=True,
                    output=f"SMS sent to {to}: {body[:80]}...",
                    metadata={
                        "sid": data.get("sid", ""),
                        "to": to,
                        "status": data.get("status", ""),
                    },
                )
            else:
                error_data = response.json()
                return ToolResult(
                    success=False,
                    error=f"Twilio error: {error_data.get('message', response.text)}",
                    metadata={"status_code": response.status_code},
                )

        except Exception as e:
            return ToolResult(success=False, error=f"SMS send failed: {str(e)}")


class VoiceCallTool(Tool):
    """Make automated voice calls via Twilio."""

    name = "voice_call"
    description = (
        "Make an automated voice call to a phone number with text-to-speech. "
        "Use this for sales calls, appointment confirmations, urgent notifications, "
        "and any scenario where a phone call is more effective than text."
    )
    parameters = [
        ToolParameter(
            name="to",
            description="Phone number to call in E.164 format (e.g., +15551234567)",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="message",
            description="The message to speak using text-to-speech",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="voice",
            description="Voice to use: alice, man, woman (default: alice)",
            param_type="string",
            required=False,
            default="alice",
        ),
    ]
    category = "communication"
    risk_level = 0.7
    requires_approval = True

    def __init__(
        self,
        account_sid: str = "",
        auth_token: str = "",
        from_number: str = "",
    ) -> None:
        self._account_sid = account_sid or os.environ.get("TWILIO_ACCOUNT_SID", "")
        self._auth_token = auth_token or os.environ.get("TWILIO_AUTH_TOKEN", "")
        self._from_number = from_number or os.environ.get("TWILIO_PHONE_NUMBER", "")

    async def execute(self, **kwargs: Any) -> ToolResult:
        to = kwargs.get("to", "")
        message = kwargs.get("message", "")
        voice = kwargs.get("voice", "alice")

        if not to or not message:
            return ToolResult(success=False, error="'to' and 'message' are required")

        if not self._account_sid or not self._auth_token or not self._from_number:
            return ToolResult(
                success=False,
                error=(
                    "Twilio not configured. Set TWILIO_ACCOUNT_SID, "
                    "TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables."
                ),
            )

        try:
            # Build TwiML for text-to-speech
            twiml = (
                f'<Response><Say voice="{voice}">{message}</Say></Response>'
            )

            url = (
                f"https://api.twilio.com/2010-04-01/Accounts/"
                f"{self._account_sid}/Calls.json"
            )

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    auth=(self._account_sid, self._auth_token),
                    data={
                        "To": to,
                        "From": self._from_number,
                        "Twiml": twiml,
                    },
                )

            if response.status_code in (200, 201):
                data = response.json()
                return ToolResult(
                    success=True,
                    output=f"Voice call initiated to {to}",
                    metadata={
                        "sid": data.get("sid", ""),
                        "to": to,
                        "status": data.get("status", ""),
                    },
                )
            else:
                error_data = response.json()
                return ToolResult(
                    success=False,
                    error=f"Twilio error: {error_data.get('message', response.text)}",
                    metadata={"status_code": response.status_code},
                )

        except Exception as e:
            return ToolResult(success=False, error=f"Voice call failed: {str(e)}")


class WhatsAppTool(Tool):
    """Send WhatsApp messages via Twilio."""

    name = "whatsapp_send"
    description = (
        "Send a WhatsApp message to a phone number. Use this for international "
        "outreach, customer communication, and messaging in markets where "
        "WhatsApp is preferred over SMS."
    )
    parameters = [
        ToolParameter(
            name="to",
            description="Recipient WhatsApp number in E.164 format (e.g., +15551234567)",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="body",
            description="The message content",
            param_type="string",
            required=True,
        ),
    ]
    category = "communication"
    risk_level = 0.5
    requires_approval = True

    def __init__(
        self,
        account_sid: str = "",
        auth_token: str = "",
        from_number: str = "",
    ) -> None:
        self._account_sid = account_sid or os.environ.get("TWILIO_ACCOUNT_SID", "")
        self._auth_token = auth_token or os.environ.get("TWILIO_AUTH_TOKEN", "")
        self._from_number = from_number or os.environ.get("TWILIO_WHATSAPP_NUMBER", "")

    async def execute(self, **kwargs: Any) -> ToolResult:
        to = kwargs.get("to", "")
        body = kwargs.get("body", "")

        if not to or not body:
            return ToolResult(success=False, error="'to' and 'body' are required")

        if not self._account_sid or not self._auth_token or not self._from_number:
            return ToolResult(
                success=False,
                error=(
                    "Twilio WhatsApp not configured. Set TWILIO_ACCOUNT_SID, "
                    "TWILIO_AUTH_TOKEN, and TWILIO_WHATSAPP_NUMBER environment variables."
                ),
            )

        try:
            url = (
                f"https://api.twilio.com/2010-04-01/Accounts/"
                f"{self._account_sid}/Messages.json"
            )

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    auth=(self._account_sid, self._auth_token),
                    data={
                        "To": f"whatsapp:{to}",
                        "From": f"whatsapp:{self._from_number}",
                        "Body": body,
                    },
                )

            if response.status_code in (200, 201):
                data = response.json()
                return ToolResult(
                    success=True,
                    output=f"WhatsApp message sent to {to}",
                    metadata={
                        "sid": data.get("sid", ""),
                        "to": to,
                        "status": data.get("status", ""),
                    },
                )
            else:
                error_data = response.json()
                return ToolResult(
                    success=False,
                    error=f"Twilio error: {error_data.get('message', response.text)}",
                    metadata={"status_code": response.status_code},
                )

        except Exception as e:
            return ToolResult(success=False, error=f"WhatsApp send failed: {str(e)}")
