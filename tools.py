"""
tools.py
Approved Python tools that the AI agent is allowed to call.

The LLM never touches SQLite directly. It can only invoke the functions
registered here, each of which is hard-scoped to a single user_id supplied
by the authenticated Streamlit session.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

import analytics
from utils.formatting import format_currency, format_date, format_month_label


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def tool_get_total_spending(user_id: int) -> str:
    total = analytics.get_total_spending(user_id)

    if analytics.get_transaction_count(user_id) == 0:
        return "No expense data available yet."

    return f"Total Spending: {format_currency(total)}"


def tool_get_average_expense(user_id: int) -> str:
    if analytics.get_transaction_count(user_id) == 0:
        return "No expense data available yet."

    avg = analytics.get_average_expense(user_id)

    return f"Average Expense: {format_currency(avg)}"


def tool_get_category_spending(user_id: int) -> str:
    data = analytics.get_category_spending(user_id)

    if not data:
        return "No expense data available yet."

    lines = [
        f"{category}: {format_currency(amount)}"
        for category, amount in data.items()
    ]

    return "Spending by Category\n\n" + "\n".join(lines)


def tool_get_monthly_spending(user_id: int) -> str:
    data = analytics.get_monthly_spending(user_id)

    if not data:
        return "No expense data available yet."

    lines = [
        f"{format_month_label(period)}: {format_currency(amount)}"
        for period, amount in data.items()
    ]

    return "Monthly Spending\n\n" + "\n".join(lines)


def tool_get_highest_expense(user_id: int) -> str:
    highest = analytics.get_highest_expense(user_id)

    if highest is None:
        return "No expense data available yet."

    lines = [
        f"Highest Individual Expense: {format_currency(highest['amount'])}",
        f"Category: {highest['category']}",
    ]

    if highest["description"]:
        lines.append(f"Description: {highest['description']}")

    lines.append(f"Date: {format_date(highest['expense_date'])}")

    return "\n".join(lines)


def tool_get_highest_category(user_id: int) -> str:
    highest = analytics.get_highest_category(user_id)

    if highest is None:
        return "No expense data available yet."

    return (
        f"Highest Spending Category: {highest['category']}\n"
        f"Total Spending: {format_currency(highest['total'])}"
    )


def tool_get_transaction_count(user_id: int) -> str:
    count = analytics.get_transaction_count(user_id)

    return f"Transactions: {count}"


def tool_get_financial_summary(user_id: int) -> str:
    summary = analytics.get_financial_summary(user_id)

    if summary["transaction_count"] == 0:
        return "There is no recorded expense data available."

    lines = [
        "Financial Summary",
        "",
        f"Total Spending: {format_currency(summary['total_spending'])}",
        f"Average Expense: {format_currency(summary['average_expense'])}",
        f"Transactions: {summary['transaction_count']}",
    ]

    highest_category = summary["highest_category"]

    if highest_category:
        lines.append(
            f"Highest Spending Category: {highest_category['category']} — "
            f"{format_currency(highest_category['total'])}"
        )

    highest_expense = summary["highest_expense"]

    if highest_expense:
        lines.append(
            f"Highest Individual Expense: "
            f"{format_currency(highest_expense['amount'])}"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Saving suggestions
# ---------------------------------------------------------------------------

def tool_get_saving_suggestions(user_id: int) -> str:
    """Analyze the user's expenses and provide practical saving suggestions."""

    summary = analytics.get_financial_summary(user_id)

    if summary["transaction_count"] == 0:
        return "There is no recorded expense data available."

    category_data = analytics.get_category_spending(user_id)

    if not category_data:
        return "There is no recorded expense data available."

    total_spending = summary["total_spending"]

    sorted_categories = sorted(
        category_data.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    suggestions = [
        "Expense Reduction Suggestions",
        "",
    ]

    top_categories = sorted_categories[:3]

    for index, (category, amount) in enumerate(top_categories, start=1):

        percentage = (
            (amount / total_spending) * 100
            if total_spending > 0
            else 0
        )

        suggestions.append(
            f"{index}. {category}: {format_currency(amount)} "
            f"({percentage:.1f}% of total spending)."
        )

        suggestions.append(
            f"   Review your {category.lower()} expenses and identify "
            f"non-essential purchases that can be reduced."
        )

    highest_category = sorted_categories[0][0]

    suggestions.append("")

    suggestions.append(
        f"Priority: Focus first on {highest_category} because it is "
        f"your highest spending category."
    )

    suggestions.append(
        "Track your spending regularly and set realistic limits for "
        "your highest spending categories."
    )

    return "\n".join(suggestions)


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOL_REGISTRY: Dict[str, Callable[[int], str]] = {
    "get_total_spending": tool_get_total_spending,
    "get_average_expense": tool_get_average_expense,
    "get_category_spending": tool_get_category_spending,
    "get_monthly_spending": tool_get_monthly_spending,
    "get_highest_expense": tool_get_highest_expense,
    "get_highest_category": tool_get_highest_category,
    "get_transaction_count": tool_get_transaction_count,
    "get_financial_summary": tool_get_financial_summary,
    "get_saving_suggestions": tool_get_saving_suggestions,
}


# ---------------------------------------------------------------------------
# Tool descriptions for OpenAI-style function calling
# ---------------------------------------------------------------------------

_TOOL_DESCRIPTIONS: Dict[str, str] = {
    "get_total_spending":
        "Get the user's total spending across all recorded expenses.",

    "get_average_expense":
        "Get the user's average expense amount.",

    "get_category_spending":
        "Get the user's total spending broken down by category.",

    "get_monthly_spending":
        "Get the user's total spending broken down by month.",

    "get_highest_expense":
        "Get the user's single highest individual expense.",

    "get_highest_category":
        "Get the category in which the user has spent the most in total.",

    "get_transaction_count":
        "Get the total number of expense transactions recorded for the user.",

    "get_financial_summary":
        "Get a complete financial summary for the user including total "
        "spending, average expense, transaction count, highest category, "
        "and highest expense.",

    "get_saving_suggestions":
        "Analyze the user's recorded expenses and provide practical "
        "suggestions for reducing spending, focusing on the user's highest "
        "spending categories. Do not provide investment, loan, or regulated "
        "financial advice.",
}


# ---------------------------------------------------------------------------
# OpenAI-style tool schemas
# ---------------------------------------------------------------------------

def get_tool_schemas(
    tool_names: Optional[List[str]] = None,
) -> List[dict]:
    """Build OpenAI-style function-calling schemas."""

    names = (
        tool_names
        if tool_names is not None
        else list(TOOL_REGISTRY.keys())
    )

    schemas: List[dict] = []

    for name in names:

        if name not in TOOL_REGISTRY:
            continue

        schemas.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": _TOOL_DESCRIPTIONS.get(name, ""),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            }
        )

    return schemas


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------

def call_tool(tool_name: str, user_id: int) -> str:
    """Execute an approved tool for the authenticated user."""

    tool_fn = TOOL_REGISTRY.get(tool_name)

    if tool_fn is None:
        return "That request is not supported by the finance assistant."

    return tool_fn(user_id)