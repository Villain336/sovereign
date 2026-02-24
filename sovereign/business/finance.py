"""Finance Tracker - track income, expenses, budgets, and financial health.

Provides financial tracking capabilities for autonomous business operations,
including budget management, expense categorization, and P&L reporting.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    REFUND = "refund"
    TRANSFER = "transfer"


class ExpenseCategory(str, Enum):
    LLM_API = "llm_api"
    TOOLS_SERVICES = "tools_services"
    MARKETING = "marketing"
    INFRASTRUCTURE = "infrastructure"
    LABOR = "labor"
    SOFTWARE = "software"
    OTHER = "other"


class Transaction(BaseModel):
    """A single financial transaction."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_type: TransactionType
    amount_usd: float
    category: ExpenseCategory = ExpenseCategory.OTHER
    description: str = ""
    source: str = ""
    reference: str = ""
    tags: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class Budget(BaseModel):
    """A budget allocation."""

    name: str
    category: ExpenseCategory
    allocated_usd: float
    spent_usd: float = 0.0
    period: str = "monthly"  # daily, weekly, monthly

    @property
    def remaining_usd(self) -> float:
        return self.allocated_usd - self.spent_usd

    @property
    def utilization_pct(self) -> float:
        return (self.spent_usd / self.allocated_usd * 100) if self.allocated_usd > 0 else 0


class FinanceTracker:
    """Track all financial activity for autonomous business operations.

    Features:
    - Transaction logging (income & expenses)
    - Budget management and alerts
    - P&L reporting
    - Cost attribution (which agent/tool spent what)
    - Financial forecasting
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._transactions: list[Transaction] = []
        self._budgets: dict[str, Budget] = {}
        self._store_path = Path(config.data_dir) / "finance.json"
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if self._store_path.exists():
            try:
                data = json.loads(self._store_path.read_text())
                self._transactions = [Transaction(**t) for t in data.get("transactions", [])]
                self._budgets = {
                    k: Budget(**v) for k, v in data.get("budgets", {}).items()
                }
            except (json.JSONDecodeError, Exception):
                self._transactions = []
                self._budgets = {}

    def _save(self) -> None:
        data = {
            "transactions": [t.model_dump(mode="json") for t in self._transactions],
            "budgets": {k: b.model_dump(mode="json") for k, b in self._budgets.items()},
        }
        self._store_path.write_text(json.dumps(data, indent=2, default=str))

    def record_transaction(self, transaction: Transaction) -> Transaction:
        """Record a financial transaction."""
        self._transactions.append(transaction)

        # Update budget tracking
        if transaction.transaction_type == TransactionType.EXPENSE:
            for budget in self._budgets.values():
                if budget.category == transaction.category:
                    budget.spent_usd += transaction.amount_usd

        self._save()
        return transaction

    def record_expense(
        self,
        amount_usd: float,
        category: ExpenseCategory,
        description: str,
        source: str = "",
    ) -> Transaction:
        """Convenience method to record an expense."""
        txn = Transaction(
            transaction_type=TransactionType.EXPENSE,
            amount_usd=amount_usd,
            category=category,
            description=description,
            source=source,
        )
        return self.record_transaction(txn)

    def record_income(
        self,
        amount_usd: float,
        description: str,
        source: str = "",
    ) -> Transaction:
        """Convenience method to record income."""
        txn = Transaction(
            transaction_type=TransactionType.INCOME,
            amount_usd=amount_usd,
            description=description,
            source=source,
        )
        return self.record_transaction(txn)

    def set_budget(
        self,
        name: str,
        category: ExpenseCategory,
        allocated_usd: float,
        period: str = "monthly",
    ) -> Budget:
        """Set a budget for a category."""
        budget = Budget(
            name=name,
            category=category,
            allocated_usd=allocated_usd,
            period=period,
        )
        self._budgets[name] = budget
        self._save()
        return budget

    def check_budget(self, category: ExpenseCategory) -> dict[str, Any]:
        """Check budget status for a category."""
        for budget in self._budgets.values():
            if budget.category == category:
                return {
                    "budget_name": budget.name,
                    "allocated_usd": budget.allocated_usd,
                    "spent_usd": budget.spent_usd,
                    "remaining_usd": budget.remaining_usd,
                    "utilization_pct": budget.utilization_pct,
                    "over_budget": budget.spent_usd > budget.allocated_usd,
                }
        return {"error": f"No budget set for {category.value}"}

    def get_pnl(self, days: int = 30) -> dict[str, Any]:
        """Get profit and loss statement."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        period_txns = [t for t in self._transactions if t.timestamp >= cutoff]

        income = sum(
            t.amount_usd for t in period_txns if t.transaction_type == TransactionType.INCOME
        )
        expenses = sum(
            t.amount_usd for t in period_txns if t.transaction_type == TransactionType.EXPENSE
        )

        # Breakdown by category
        expense_breakdown: dict[str, float] = {}
        for txn in period_txns:
            if txn.transaction_type == TransactionType.EXPENSE:
                cat = txn.category.value
                expense_breakdown[cat] = expense_breakdown.get(cat, 0) + txn.amount_usd

        return {
            "period_days": days,
            "total_income_usd": income,
            "total_expenses_usd": expenses,
            "net_profit_usd": income - expenses,
            "profit_margin_pct": ((income - expenses) / income * 100) if income > 0 else 0,
            "expense_breakdown": expense_breakdown,
            "transaction_count": len(period_txns),
        }

    def get_burn_rate(self, days: int = 30) -> float:
        """Calculate daily burn rate (average daily expenses)."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        expenses = sum(
            t.amount_usd
            for t in self._transactions
            if t.transaction_type == TransactionType.EXPENSE and t.timestamp >= cutoff
        )
        return expenses / max(days, 1)

    def forecast_runway(self, current_balance_usd: float) -> dict[str, Any]:
        """Forecast how long the business can sustain at current burn rate."""
        daily_burn = self.get_burn_rate(30)
        daily_income = sum(
            t.amount_usd
            for t in self._transactions
            if t.transaction_type == TransactionType.INCOME
            and t.timestamp >= datetime.now(timezone.utc) - timedelta(days=30)
        ) / 30

        net_daily = daily_income - daily_burn
        if net_daily >= 0:
            runway_days = float("inf")
        elif daily_burn > 0:
            runway_days = current_balance_usd / abs(net_daily)
        else:
            runway_days = float("inf")

        return {
            "current_balance_usd": current_balance_usd,
            "daily_burn_usd": daily_burn,
            "daily_income_usd": daily_income,
            "net_daily_usd": net_daily,
            "runway_days": runway_days,
            "sustainable": net_daily >= 0,
        }
