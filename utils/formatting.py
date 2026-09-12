"""
utils/formatting.py
Deterministic money and date formatting helpers shared across the app and the AI layer.
Formatting is centralized here so the AI assistant can never present numbers
in an inconsistent or hallucinated format.
"""
from __future__ import annotations

from datetime import datetime

import config


def format_currency(amount: float) -> str:
    """Format a number as Indian Rupees, e.g. 4700.0 -> '\u20b91,200.00'."""
    if amount is None:
        amount = 0.0
    return f"{config.CURRENCY_SYMBOL}{amount:,.2f}"


def format_date(date_str: str) -> str:
    """Normalize a stored date string (YYYY-MM-DD) for display."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return date_str or ""


def format_month_label(period_str: str) -> str:
    """Convert a 'YYYY-MM' period string into a readable label, e.g. 'Sep 2026'."""
    try:
        dt = datetime.strptime(period_str, "%Y-%m")
        return dt.strftime("%b %Y")
    except (ValueError, TypeError):
        return period_str or ""
