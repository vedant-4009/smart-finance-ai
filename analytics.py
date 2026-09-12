"""
analytics.py
Pure, deterministic analytics functions computed from a user's expenses.

Every function here takes a user_id and returns numbers/structures derived
strictly from that user's rows in the database. Nothing here ever touches
another user's data, and nothing here is generated or guessed by an LLM.
These functions back both the Streamlit UI (dashboard/analytics charts) and
the AI assistant's tool-calling layer (see tools.py).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from models import get_expenses

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def _expenses_dataframe(user_id: int) -> pd.DataFrame:
    expenses = get_expenses(user_id)
    if not expenses:
        return pd.DataFrame(columns=["id", "user_id", "amount", "category", "description", "expense_date"])

    df = pd.DataFrame([e.__dict__ for e in expenses])
    df["expense_date"] = pd.to_datetime(df["expense_date"], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Core metrics (used by both UI and AI tools)
# ---------------------------------------------------------------------------
def get_total_spending(user_id: int) -> float:
    df = _expenses_dataframe(user_id)
    if df.empty:
        return 0.0
    return round(float(df["amount"].sum()), 2)


def get_average_expense(user_id: int) -> float:
    df = _expenses_dataframe(user_id)
    if df.empty:
        return 0.0
    return round(float(df["amount"].mean()), 2)


def get_transaction_count(user_id: int) -> int:
    df = _expenses_dataframe(user_id)
    return int(len(df))


def get_category_spending(user_id: int) -> Dict[str, float]:
    df = _expenses_dataframe(user_id)
    if df.empty:
        return {}
    grouped = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    return {str(k): round(float(v), 2) for k, v in grouped.items()}


def get_highest_category(user_id: int) -> Optional[Dict[str, Any]]:
    category_spending = get_category_spending(user_id)
    if not category_spending:
        return None
    category, total = next(iter(category_spending.items()))
    return {"category": category, "total": total}


def get_highest_expense(user_id: int) -> Optional[Dict[str, Any]]:
    df = _expenses_dataframe(user_id)
    if df.empty:
        return None
    row = df.loc[df["amount"].idxmax()]
    return {
        "amount": round(float(row["amount"]), 2),
        "category": str(row["category"]),
        "description": str(row["description"] or ""),
        "expense_date": row["expense_date"].strftime("%Y-%m-%d") if pd.notnull(row["expense_date"]) else "",
    }


def get_monthly_spending(user_id: int) -> Dict[str, float]:
    df = _expenses_dataframe(user_id)
    if df.empty:
        return {}
    df = df.dropna(subset=["expense_date"])
    if df.empty:
        return {}
    monthly = df.groupby(df["expense_date"].dt.to_period("M"))["amount"].sum().sort_index()
    return {str(period): round(float(value), 2) for period, value in monthly.items()}


def get_financial_summary(user_id: int) -> Dict[str, Any]:
    return {
        "total_spending": get_total_spending(user_id),
        "average_expense": get_average_expense(user_id),
        "transaction_count": get_transaction_count(user_id),
        "highest_category": get_highest_category(user_id),
        "highest_expense": get_highest_expense(user_id),
    }


# ---------------------------------------------------------------------------
# Chart builders (Plotly) for the dashboard / analytics UI
# ---------------------------------------------------------------------------
_PLOTLY_TEMPLATE = "plotly_dark"
_ACCENT_COLORS = ["#7C9CFF", "#5EE6C8", "#F2C078", "#F27F7F", "#B98BFF", "#6FD3F2", "#F2A6D0", "#9AF29E"]


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        template=_PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(text=message, showarrow=False, font=dict(size=15, color="#9aa4c7"))
        ],
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=320,
    )
    return fig


def build_category_donut(user_id: int) -> go.Figure:
    data = get_category_spending(user_id)
    if not data:
        return _empty_figure("No expense data available yet.")

    fig = go.Figure(
        data=[
            go.Pie(
                labels=list(data.keys()),
                values=list(data.values()),
                hole=0.62,
                marker=dict(colors=_ACCENT_COLORS, line=dict(color="#0e1326", width=2)),
                textinfo="label+percent",
                textfont=dict(size=12, color="#e7ebff"),
            )
        ]
    )
    fig.update_layout(
        template=_PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(font=dict(color="#c7cef0")),
        margin=dict(t=10, b=10, l=10, r=10),
        height=340,
    )
    return fig


def build_monthly_bar(user_id: int) -> go.Figure:
    data = get_monthly_spending(user_id)
    if not data:
        return _empty_figure("No expense data available yet.")

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(data.keys()),
                y=list(data.values()),
                marker=dict(color="#7C9CFF", line=dict(color="#5EE6C8", width=1)),
            )
        ]
    )
    fig.update_layout(
        template=_PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Month", color="#c7cef0", gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(title="Amount", color="#c7cef0", gridcolor="rgba(255,255,255,0.06)"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=340,
    )
    return fig


def build_spending_trend(user_id: int) -> go.Figure:
    df = _expenses_dataframe(user_id)
    if df.empty:
        return _empty_figure("No expense data available yet.")

    df = df.dropna(subset=["expense_date"]).sort_values("expense_date")
    if df.empty:
        return _empty_figure("No expense data available yet.")

    daily = df.groupby(df["expense_date"].dt.date)["amount"].sum().reset_index()
    daily.columns = ["date", "amount"]
    daily["cumulative"] = daily["amount"].cumsum()

    fig = go.Figure(
        data=[
            go.Scatter(
                x=daily["date"],
                y=daily["cumulative"],
                mode="lines",
                fill="tozeroy",
                line=dict(color="#5EE6C8", width=3),
                fillcolor="rgba(94, 230, 200, 0.15)",
            )
        ]
    )
    fig.update_layout(
        template=_PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Date", color="#c7cef0", gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(title="Cumulative Spending", color="#c7cef0", gridcolor="rgba(255,255,255,0.06)"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=340,
    )
    return fig


def build_distribution_bar(user_id: int) -> go.Figure:
    df = _expenses_dataframe(user_id)
    if df.empty:
        return _empty_figure("No expense data available yet.")

    fig = px.histogram(
        df,
        x="amount",
        nbins=10,
        template=_PLOTLY_TEMPLATE,
        color_discrete_sequence=["#B98BFF"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Transaction Amount", color="#c7cef0", gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(title="Number of Transactions", color="#c7cef0", gridcolor="rgba(255,255,255,0.06)"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=340,
        bargap=0.15,
    )
    return fig
