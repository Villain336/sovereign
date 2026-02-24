"""Invoice Tool - generate invoices and payment links.

Enables the agent to:
- Generate professional HTML invoices
- Create Stripe payment links (when configured)
- Track invoice status
- Send invoices via email
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from sovereign.tools.base import Tool, ToolParameter, ToolResult


def _get_invoice_path() -> Path:
    """Get the invoice data storage path."""
    inv_dir = Path.home() / ".sovereign" / "invoices"
    inv_dir.mkdir(parents=True, exist_ok=True)
    return inv_dir


def _load_invoices() -> list[dict[str, Any]]:
    """Load invoices from disk."""
    path = _get_invoice_path() / "invoices.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def _save_invoices(invoices: list[dict[str, Any]]) -> None:
    """Save invoices to disk."""
    path = _get_invoice_path() / "invoices.json"
    path.write_text(json.dumps(invoices, indent=2, default=str), encoding="utf-8")


class InvoiceGenerateTool(Tool):
    """Generate a professional invoice."""

    name = "invoice_generate"
    description = (
        "Generate a professional HTML invoice for a client. Creates a printable "
        "invoice with line items, totals, and payment instructions. Use this after "
        "closing a deal to bill the client."
    )
    parameters = [
        ToolParameter(
            name="client_name",
            description="Client/company name",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="client_email",
            description="Client email address",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="items",
            description=(
                "Line items as JSON array: "
                '[{"description": "Service", "quantity": 1, "unit_price": 100}]'
            ),
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="due_days",
            description="Payment due in N days (default 30)",
            param_type="integer",
            required=False,
            default=30,
        ),
        ToolParameter(
            name="notes",
            description="Additional notes on the invoice",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="from_name",
            description="Your business name (default: from config)",
            param_type="string",
            required=False,
            default="Sovereign AI Agency",
        ),
    ]
    category = "business"
    risk_level = 0.2

    async def execute(self, **kwargs: Any) -> ToolResult:
        client_name = kwargs.get("client_name", "")
        client_email = kwargs.get("client_email", "")
        items_json = kwargs.get("items", "[]")
        due_days = kwargs.get("due_days", 30)
        notes = kwargs.get("notes", "")
        from_name = kwargs.get("from_name", "Sovereign AI Agency")

        if not client_name or not client_email:
            return ToolResult(
                success=False, error="client_name and client_email are required"
            )

        try:
            if isinstance(items_json, str):
                items = json.loads(items_json)
            else:
                items = items_json
        except json.JSONDecodeError:
            return ToolResult(success=False, error="Invalid items JSON format")

        if not items:
            return ToolResult(success=False, error="At least one line item is required")

        # Calculate totals
        subtotal = sum(
            item.get("quantity", 1) * item.get("unit_price", 0) for item in items
        )
        tax = subtotal * 0.0  # No tax by default
        total = subtotal + tax

        # Generate invoice
        invoice_id = str(uuid.uuid4())[:8].upper()
        now = datetime.now(timezone.utc)
        due_date = datetime(
            now.year, now.month, min(now.day + due_days, 28),
            tzinfo=timezone.utc,
        )

        invoice_data = {
            "id": invoice_id,
            "from_name": from_name,
            "client_name": client_name,
            "client_email": client_email,
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "created_at": now.isoformat(),
            "due_date": due_date.isoformat(),
            "status": "pending",
            "notes": notes,
        }

        # Save to disk
        invoices = _load_invoices()
        invoices.append(invoice_data)
        _save_invoices(invoices)

        # Generate HTML
        html = self._generate_html(invoice_data)
        html_path = _get_invoice_path() / f"invoice_{invoice_id}.html"
        html_path.write_text(html, encoding="utf-8")

        return ToolResult(
            success=True,
            output=(
                f"Invoice #{invoice_id} generated for {client_name}\n"
                f"Total: ${total:,.2f}\n"
                f"Due: {due_date.strftime('%Y-%m-%d')}\n"
                f"Saved to: {html_path}"
            ),
            metadata={
                "invoice_id": invoice_id,
                "total": total,
                "html_path": str(html_path),
                "client_name": client_name,
                "client_email": client_email,
            },
        )

    def _generate_html(self, invoice: dict[str, Any]) -> str:
        """Generate professional invoice HTML."""
        items_html = ""
        for item in invoice["items"]:
            qty = item.get("quantity", 1)
            price = item.get("unit_price", 0)
            line_total = qty * price
            items_html += f"""
            <tr>
                <td>{item.get("description", "")}</td>
                <td style="text-align:center">{qty}</td>
                <td style="text-align:right">${price:,.2f}</td>
                <td style="text-align:right">${line_total:,.2f}</td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Invoice #{invoice["id"]}</title>
<style>
body {{ font-family: -apple-system, sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; color: #1e293b; }}
.header {{ display: flex; justify-content: space-between; margin-bottom: 40px; }}
.header h1 {{ color: #2563eb; margin: 0; }}
.invoice-info {{ text-align: right; }}
.parties {{ display: flex; justify-content: space-between; margin-bottom: 40px; }}
.from, .to {{ width: 45%; }}
.label {{ color: #64748b; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; }}
table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; }}
th {{ background: #f1f5f9; padding: 12px 16px; text-align: left; font-weight: 600; }}
td {{ padding: 12px 16px; border-bottom: 1px solid #e2e8f0; }}
.totals {{ text-align: right; margin-top: 24px; }}
.totals .total {{ font-size: 1.5rem; font-weight: 800; color: #2563eb; }}
.notes {{ margin-top: 40px; padding: 20px; background: #f8fafc; border-radius: 8px; }}
.footer {{ margin-top: 60px; text-align: center; color: #94a3b8; font-size: 0.875rem; }}
@media print {{ body {{ padding: 0; }} }}
</style>
</head>
<body>
<div class="header">
    <h1>INVOICE</h1>
    <div class="invoice-info">
        <div><strong>Invoice #:</strong> {invoice["id"]}</div>
        <div><strong>Date:</strong> {invoice["created_at"][:10]}</div>
        <div><strong>Due:</strong> {invoice["due_date"][:10]}</div>
        <div><strong>Status:</strong> {invoice["status"].upper()}</div>
    </div>
</div>

<div class="parties">
    <div class="from">
        <div class="label">From</div>
        <strong>{invoice["from_name"]}</strong>
    </div>
    <div class="to">
        <div class="label">Bill To</div>
        <strong>{invoice["client_name"]}</strong><br>
        {invoice["client_email"]}
    </div>
</div>

<table>
    <thead>
        <tr>
            <th>Description</th>
            <th style="text-align:center">Qty</th>
            <th style="text-align:right">Unit Price</th>
            <th style="text-align:right">Amount</th>
        </tr>
    </thead>
    <tbody>
        {items_html}
    </tbody>
</table>

<div class="totals">
    <div>Subtotal: ${invoice["subtotal"]:,.2f}</div>
    <div>Tax: ${invoice["tax"]:,.2f}</div>
    <div class="total">Total: ${invoice["total"]:,.2f}</div>
</div>

{"<div class='notes'><strong>Notes:</strong> " + invoice["notes"] + "</div>" if invoice.get("notes") else ""}

<div class="footer">
    Generated by Sovereign AI | {invoice["created_at"][:10]}
</div>
</body>
</html>"""


class PaymentLinkTool(Tool):
    """Create a Stripe payment link for collecting payments."""

    name = "payment_link"
    description = (
        "Create a Stripe payment link that can be sent to clients for easy "
        "online payment. Requires STRIPE_SECRET_KEY environment variable."
    )
    parameters = [
        ToolParameter(
            name="amount",
            description="Payment amount in USD (e.g., 500.00)",
            param_type="number",
            required=True,
        ),
        ToolParameter(
            name="description",
            description="What the payment is for",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="client_email",
            description="Client email for the payment",
            param_type="string",
            required=False,
        ),
    ]
    category = "business"
    risk_level = 0.4
    requires_approval = True

    async def execute(self, **kwargs: Any) -> ToolResult:
        amount = kwargs.get("amount", 0)
        description = kwargs.get("description", "")

        if not amount or not description:
            return ToolResult(
                success=False, error="amount and description are required"
            )

        stripe_key = os.environ.get("STRIPE_SECRET_KEY", "")
        if not stripe_key:
            return ToolResult(
                success=False,
                error=(
                    "Stripe not configured. Set STRIPE_SECRET_KEY environment variable. "
                    "Get it from https://dashboard.stripe.com/apikeys"
                ),
            )

        try:
            amount_cents = int(amount * 100)

            async with httpx.AsyncClient() as client:
                # Create a price
                price_response = await client.post(
                    "https://api.stripe.com/v1/prices",
                    auth=(stripe_key, ""),
                    data={
                        "unit_amount": amount_cents,
                        "currency": "usd",
                        "product_data[name]": description,
                    },
                )

                if price_response.status_code != 200:
                    return ToolResult(
                        success=False,
                        error=f"Stripe price creation failed: {price_response.text}",
                    )

                price_data = price_response.json()
                price_id = price_data["id"]

                # Create a payment link
                link_response = await client.post(
                    "https://api.stripe.com/v1/payment_links",
                    auth=(stripe_key, ""),
                    data={
                        "line_items[0][price]": price_id,
                        "line_items[0][quantity]": 1,
                    },
                )

                if link_response.status_code != 200:
                    return ToolResult(
                        success=False,
                        error=f"Stripe link creation failed: {link_response.text}",
                    )

                link_data = link_response.json()
                payment_url = link_data["url"]

                return ToolResult(
                    success=True,
                    output=f"Payment link created: {payment_url}\nAmount: ${amount:,.2f}\nFor: {description}",
                    metadata={
                        "payment_url": payment_url,
                        "amount": amount,
                        "description": description,
                        "stripe_price_id": price_id,
                    },
                )

        except Exception as e:
            return ToolResult(
                success=False, error=f"Payment link creation failed: {str(e)}"
            )
