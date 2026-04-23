"""Email Client Tool - send and manage emails.

Supports SMTP for sending and IMAP for reading emails.
Used by outreach agents for campaigns and communication.
"""

from __future__ import annotations

import asyncio
import email
import email.mime.multipart
import email.mime.text
import imaplib
import smtplib
from email.header import decode_header
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


class EmailReceiveTool(Tool):
    """Read emails from an IMAP mailbox."""

    name = "email_receive"
    description = (
        "Read emails from an IMAP mailbox. Can fetch recent messages, search by "
        "subject/sender, and read message bodies. Use this to monitor inboxes, "
        "check for replies, and process incoming emails autonomously."
    )
    parameters = [
        ToolParameter(
            name="folder",
            description="Mailbox folder to read from (default: INBOX)",
            param_type="string",
            required=False,
            default="INBOX",
        ),
        ToolParameter(
            name="count",
            description="Number of recent emails to fetch (default: 10)",
            param_type="integer",
            required=False,
            default=10,
        ),
        ToolParameter(
            name="search_subject",
            description="Filter emails by subject keyword",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="search_from",
            description="Filter emails by sender address",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="unread_only",
            description="Only fetch unread messages (default: false)",
            param_type="boolean",
            required=False,
            default=False,
        ),
    ]
    category = "communication"
    risk_level = 0.2

    def __init__(
        self,
        imap_host: str = "",
        imap_port: int = 993,
        username: str = "",
        password: str = "",
    ) -> None:
        self._imap_host = imap_host
        self._imap_port = imap_port
        self._username = username
        self._password = password

    async def execute(self, **kwargs: Any) -> ToolResult:
        folder = kwargs.get("folder", "INBOX")
        count = min(int(kwargs.get("count", 10)), 50)
        search_subject = kwargs.get("search_subject", "")
        search_from = kwargs.get("search_from", "")
        unread_only = kwargs.get("unread_only", False)

        if not self._imap_host or not self._username:
            return ToolResult(
                success=False,
                error="IMAP not configured. Set email settings in config.",
            )

        def _fetch() -> list[dict[str, str]]:
            mail = imaplib.IMAP4_SSL(self._imap_host, self._imap_port)
            mail.login(self._username, self._password)
            mail.select(folder, readonly=True)

            # Build search criteria
            criteria_parts: list[str] = []
            if unread_only:
                criteria_parts.append("UNSEEN")
            if search_subject:
                criteria_parts.append(f'SUBJECT "{search_subject}"')
            if search_from:
                criteria_parts.append(f'FROM "{search_from}"')

            criteria = " ".join(criteria_parts) if criteria_parts else "ALL"
            _, msg_nums = mail.search(None, criteria)

            msg_ids = msg_nums[0].split()
            # Get most recent messages
            msg_ids = msg_ids[-count:] if len(msg_ids) > count else msg_ids
            msg_ids.reverse()  # Most recent first

            messages: list[dict[str, str]] = []
            for msg_id in msg_ids:
                _, msg_data = mail.fetch(msg_id, "(RFC822)")
                if not msg_data or not msg_data[0]:
                    continue
                raw = msg_data[0]
                if not isinstance(raw, tuple) or len(raw) < 2:
                    continue

                msg = email.message_from_bytes(raw[1])

                # Decode subject
                subject_header = msg.get("Subject", "")
                decoded_parts = decode_header(subject_header)
                subject = ""
                for part, charset in decoded_parts:
                    if isinstance(part, bytes):
                        subject += part.decode(charset or "utf-8", errors="replace")
                    else:
                        subject += str(part)

                # Extract body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        if ctype == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode("utf-8", errors="replace")
                                break
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode("utf-8", errors="replace")

                messages.append({
                    "from": msg.get("From", ""),
                    "to": msg.get("To", ""),
                    "subject": subject,
                    "date": msg.get("Date", ""),
                    "body": body[:2000],
                })

            mail.logout()
            return messages

        try:
            messages = await asyncio.get_event_loop().run_in_executor(
                None, _fetch,
            )

            if not messages:
                return ToolResult(
                    success=True,
                    output="No messages found matching criteria.",
                    metadata={"folder": folder, "count": 0},
                )

            output_lines = [f"Found {len(messages)} message(s) in {folder}:\n"]
            for i, msg in enumerate(messages, 1):
                output_lines.append(f"--- Message {i} ---")
                output_lines.append(f"  From: {msg['from']}")
                output_lines.append(f"  Subject: {msg['subject']}")
                output_lines.append(f"  Date: {msg['date']}")
                output_lines.append(f"  Body: {msg['body'][:300]}")
                output_lines.append("")

            return ToolResult(
                success=True,
                output="\n".join(output_lines),
                metadata={
                    "folder": folder,
                    "count": len(messages),
                    "messages": messages,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Email receive failed: {str(e)}",
                metadata={"folder": folder},
            )
