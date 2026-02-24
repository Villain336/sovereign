"""Email Client Tool - send and manage emails.

Supports SMTP for sending and IMAP for reading emails.
Used by outreach agents for campaigns and communication.
"""

from __future__ import annotations

import asyncio
import email
import email.mime.multipart
import email.mime.text
import smtplib
from typing import Any

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class EmailSendTool(Tool):
    """Send emails via SMTP."""

    name = "email_send"
    description = (
        "Send an email to one or more recipients. Supports plain text and HTML content. "
        "Use this for outreach, notifications, reports, and automated communication."
    )
    parameters = [
        ToolParameter(
            name="to",
            description="Recipient email address(es), comma-separated for multiple",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="subject",
            description="Email subject line",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="body",
            description="Email body content",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="html",
            description="Whether the body is HTML (default: false)",
            param_type="boolean",
            required=False,
            default=False,
        ),
        ToolParameter(
            name="cc",
            description="CC recipients, comma-separated",
            param_type="string",
            required=False,
        ),
    ]
    category = "communication"
    risk_level = 0.5
    requires_approval = True

    def __init__(
        self,
        smtp_host: str = "",
        smtp_port: int = 587,
        username: str = "",
        password: str = "",
    ) -> None:
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._username = username
        self._password = password

    async def execute(self, **kwargs: Any) -> ToolResult:
        to = kwargs.get("to", "")
        subject = kwargs.get("subject", "")
        body = kwargs.get("body", "")
        is_html = kwargs.get("html", False)
        cc = kwargs.get("cc", "")

        if not all([to, subject, body]):
            return ToolResult(success=False, error="to, subject, and body are required")

        if not self._smtp_host or not self._username:
            return ToolResult(
                success=False,
                error="SMTP not configured. Set email settings in config.",
            )

        try:
            msg = email.mime.multipart.MIMEMultipart()
            msg["From"] = self._username
            msg["To"] = to
            msg["Subject"] = subject
            if cc:
                msg["Cc"] = cc

            content_type = "html" if is_html else "plain"
            msg.attach(email.mime.text.MIMEText(body, content_type))

            # Run SMTP in a thread to avoid blocking
            recipients = [addr.strip() for addr in to.split(",")]
            if cc:
                recipients.extend(addr.strip() for addr in cc.split(","))

            def _send() -> None:
                with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                    server.starttls()
                    server.login(self._username, self._password)
                    server.sendmail(self._username, recipients, msg.as_string())

            await asyncio.get_event_loop().run_in_executor(None, _send)

            return ToolResult(
                success=True,
                output=f"Email sent to {to} with subject: {subject}",
                metadata={
                    "to": to,
                    "subject": subject,
                    "cc": cc,
                    "recipient_count": len(recipients),
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Email send failed: {str(e)}",
                metadata={"to": to, "subject": subject},
            )
