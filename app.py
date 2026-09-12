"""
app.py
Smart Finance - AI-Powered 3D Personal Finance Analytics Platform.
Main Streamlit entry point: routing between authentication and the
authenticated application (Dashboard, Add Expense, Transactions, Analytics,
AI Assistant).
"""
from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

import agent
import analytics
import auth
import config
import models
import theme
from utils.formatting import format_currency, format_date
from database import init_db

st.set_page_config(
    page_title="Smart Finance",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
theme.inject_css(st)


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------
def _init_session_state() -> None:
    defaults = {
        "authenticated": False,
        "user": None,
        "auth_view": "login",
        "page": "Dashboard",
        "chat_history": [],
        "edit_expense_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _logout() -> None:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.session_state["chat_history"] = []
    st.session_state["page"] = "Dashboard"
    st.session_state["edit_expense_id"] = None


def _current_user_id() -> int:
    """Return the authenticated user's id. Never sourced from request/form data."""
    user = st.session_state.get("user")
    if not user:
        raise RuntimeError("No authenticated user in session.")
    return user.id


# ---------------------------------------------------------------------------
# Small SVG icon helpers (no emojis anywhere in the UI)
# ---------------------------------------------------------------------------
ICON_LOGO = """<svg viewBox="0 0 24 24" fill="none"><path d="M4 15L9 9L13 13L20 5" stroke="#0b0f1e" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 5H20V10" stroke="#0b0f1e" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

_ICONS = {
    "total": """<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="#c7cef0" stroke-width="1.6"/><path d="M12 7v10M9 9.5c0-1.4 1.3-2.5 3-2.5s3 1 3 2.2c0 2.8-6 1.4-6 4.1 0 1.3 1.3 2.2 3 2.2s3-1 3-2.4" stroke="#c7cef0" stroke-width="1.6" stroke-linecap="round"/></svg>""",
    "average": """<svg viewBox="0 0 24 24" fill="none"><path d="M4 19V9M10 19V5M16 19V12M22 19V15" stroke="#c7cef0" stroke-width="1.8" stroke-linecap="round"/></svg>""",
    "count": """<svg viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="3" stroke="#c7cef0" stroke-width="1.6"/><path d="M8 9h8M8 13h8M8 17h5" stroke="#c7cef0" stroke-width="1.6" stroke-linecap="round"/></svg>""",
    "category": """<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="8" stroke="#c7cef0" stroke-width="1.6"/><path d="M12 4v8l6 3" stroke="#c7cef0" stroke-width="1.6" stroke-linecap="round"/></svg>""",
    "highest": """<svg viewBox="0 0 24 24" fill="none"><path d="M4 18L10 10L14 14L20 6" stroke="#c7cef0" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 6H20V11" stroke="#c7cef0" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
}


def _metric_card(label: str, value: str, icon_key: str) -> str:
    icon = _ICONS.get(icon_key, "")
    return f"""
    <div class="sf-metric-card">
        <div class="sf-metric-icon">{icon}</div>
        <div class="sf-metric-label">{label}</div>
        <div class="sf-metric-value">{value}</div>
    </div>
    """


# ---------------------------------------------------------------------------
# Authentication views
# ---------------------------------------------------------------------------
def render_auth() -> None:
    left, right = st.columns([1.05, 1], gap="large")

    with left:
        st.markdown(
            f"""
            <div class="sf-auth-hero">
                <div class="sf-brand-row">
                    <div class="sf-logo-mark">{ICON_LOGO}</div>
                    <div>
                        <div class="sf-brand-title">{config.APP_NAME}</div>
                        <div class="sf-brand-sub">{config.APP_TAGLINE}</div>
                    </div>
                </div>
                <div style="height: 26px;"></div>
                <div class="sf-auth-hero-badge">Personal Finance Intelligence</div>
                <div class="sf-auth-hero-title">Understand your money<br/>with clarity and depth.</div>
                <div class="sf-auth-hero-desc">
                    Smart Finance brings together secure multi-user accounts,
                    real-time analytics, and an AI assistant that reasons over
                    your own transaction data to give accurate, professional answers.
                </div>
                <div class="sf-visual-shape"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        if st.session_state["auth_view"] == "login":
            _render_login_card()
        else:
            _render_signup_card()


def _render_login_card() -> None:
    st.markdown('<div class="sf-auth-section">', unsafe_allow_html=True)
    st.markdown('<div class="sf-auth-card-title">Welcome back</div>', unsafe_allow_html=True)
    st.markdown('<div class="sf-auth-card-sub">Log in to access your financial dashboard.</div>', unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("LOGIN")

    if submitted:
        success, message, user = auth.login(email, password)
        if success:
            st.session_state["authenticated"] = True
            st.session_state["user"] = user
            st.session_state["page"] = "Dashboard"
            st.rerun()
        else:
            st.error(message)

    st.markdown(
        '<div class="sf-auth-switch">Don\'t have an account?</div>',
        unsafe_allow_html=True,
    )
    if st.button("Create Account", key="go_signup"):
        st.session_state["auth_view"] = "signup"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_signup_card() -> None:
    st.markdown('<div class="sf-auth-section">', unsafe_allow_html=True)
    st.markdown('<div class="sf-auth-card-title">Create your account</div>', unsafe_allow_html=True)
    st.markdown('<div class="sf-auth-card-sub">Start tracking and analyzing your finances.</div>', unsafe_allow_html=True)

    with st.form("signup_form", clear_on_submit=False):
        name = st.text_input("Full Name", placeholder="Jane Doe")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="At least 8 characters")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
        submitted = st.form_submit_button("CREATE ACCOUNT")

    if submitted:
        success, message, user = auth.signup(name, email, password, confirm_password)
        if success:
            st.success("Account created successfully. Please log in.")
            st.session_state["auth_view"] = "login"
            st.rerun()
        else:
            st.error(message)

    st.markdown(
        '<div class="sf-auth-switch">Already have an account?</div>',
        unsafe_allow_html=True,
    )
    if st.button("Login", key="go_login"):
        st.session_state["auth_view"] = "login"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
_PAGES = ["Dashboard", "Add Expense", "Transactions", "Analytics", "AI Assistant"]


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sf-brand-row">
                <div class="sf-logo-mark">{ICON_LOGO}</div>
                <div>
                    <div class="sf-brand-title" style="font-size:1.05rem;">{config.APP_NAME}</div>
                </div>
            </div>
            <div class="sf-divider"></div>
            """,
            unsafe_allow_html=True,
        )

        for page in _PAGES:
            is_active = st.session_state["page"] == page
            if st.button(page, key=f"nav_{page}", use_container_width=True):
                st.session_state["page"] = page
                st.rerun()

        st.markdown('<div style="flex-grow: 1; min-height: 40px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sf-divider"></div>', unsafe_allow_html=True)

        user = st.session_state["user"]
        st.markdown(
            f"""
            <div class="sf-sidebar-user">
                <div class="sf-metric-label" style="margin-bottom:6px;">Logged in as</div>
                <div class="sf-sidebar-user-name">{user.name}</div>
                <div class="sf-sidebar-user-email">{user.email}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Logout", key="logout_btn", use_container_width=True):
            _logout()
            st.rerun()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def render_dashboard() -> None:
    st.markdown(f'<div class="sf-page-title">{config.APP_NAME}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sf-page-sub">{config.APP_TAGLINE}</div>', unsafe_allow_html=True)

    user_id = _current_user_id()

    if analytics.get_transaction_count(user_id) == 0:
        st.markdown(
            '<div class="sf-glass sf-empty-state">No expense data available yet.</div>',
            unsafe_allow_html=True,
        )
        return

    summary = analytics.get_financial_summary(user_id)
    highest_category = summary["highest_category"] or {"category": "N/A", "total": 0}
    highest_expense = summary["highest_expense"] or {"amount": 0}

    cols = st.columns(5)
    cards = [
        ("TOTAL SPENDING", format_currency(summary["total_spending"]), "total"),
        ("AVERAGE EXPENSE", format_currency(summary["average_expense"]), "average"),
        ("TRANSACTIONS", str(summary["transaction_count"]), "count"),
        ("HIGHEST SPENDING CATEGORY", highest_category["category"], "category"),
        ("HIGHEST INDIVIDUAL EXPENSE", format_currency(highest_expense["amount"]), "highest"),
    ]
    for col, (label, value, icon_key) in zip(cols, cards):
        with col:
            st.markdown(_metric_card(label, value, icon_key), unsafe_allow_html=True)

    st.markdown('<div style="height: 22px;"></div>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown('<div class="sf-chart-section">', unsafe_allow_html=True)
        st.markdown('<div class="sf-metric-label">SPENDING BY CATEGORY</div>', unsafe_allow_html=True)
        st.plotly_chart(analytics.build_category_donut(user_id), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="sf-chart-section">', unsafe_allow_html=True)
        st.markdown('<div class="sf-metric-label">MONTHLY SPENDING</div>', unsafe_allow_html=True)
        st.plotly_chart(analytics.build_monthly_bar(user_id), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Add Expense
# ---------------------------------------------------------------------------
def render_add_expense() -> None:
    st.markdown('<div class="sf-page-title">Add Expense</div>', unsafe_allow_html=True)
    st.markdown('<div class="sf-page-sub">Record a new transaction to your account.</div>', unsafe_allow_html=True)

    user_id = _current_user_id()

    st.markdown('<div class="sf-form-section">', unsafe_allow_html=True)
    with st.form("add_expense_form", clear_on_submit=True):
        amount = st.number_input("Amount", min_value=0.0, step=50.0, format="%.2f")
        category = st.selectbox("Category", config.EXPENSE_CATEGORIES)
        description = st.text_input("Description", placeholder="Optional note about this expense")
        expense_date = st.date_input("Expense Date", value=date.today())
        submitted = st.form_submit_button("ADD EXPENSE")

    if submitted:
        try:
            models.create_expense(
                user_id=user_id,
                amount=amount,
                category=category,
                description=description,
                expense_date=expense_date.isoformat(),
            )
            st.success("Expense added successfully.")
        except ValueError as exc:
            st.error(str(exc))
        except Exception:
            st.error("Something went wrong while saving this expense. Please try again.")

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------
def render_transactions() -> None:
    st.markdown('<div class="sf-page-title">Transactions</div>', unsafe_allow_html=True)
    st.markdown('<div class="sf-page-sub">All of your recorded expenses.</div>', unsafe_allow_html=True)

    user_id = _current_user_id()
    expenses = models.get_expenses(user_id)

    if not expenses:
        st.markdown(
            '<div class="sf-glass sf-empty-state">No expense data available yet.</div>',
            unsafe_allow_html=True,
        )
        return

    filter_col1, filter_col2, filter_col3 = st.columns([2, 1.2, 1.2])
    with filter_col1:
        search_term = st.text_input("Search description", placeholder="Search...")
    with filter_col2:
        category_filter = st.selectbox("Category", ["All"] + config.EXPENSE_CATEGORIES)
    with filter_col3:
        sort_order = st.selectbox("Sort by date", ["Newest first", "Oldest first"])

    rows = expenses
    if search_term:
        rows = [e for e in rows if search_term.lower() in (e.description or "").lower()]
    if category_filter != "All":
        rows = [e for e in rows if e.category == category_filter]
    rows = sorted(rows, key=lambda e: e.expense_date, reverse=(sort_order == "Newest first"))

    if not rows:
        st.markdown(
            '<div class="sf-glass sf-empty-state">No transactions match your filters.</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="sf-table-section">', unsafe_allow_html=True)
    df = pd.DataFrame(
        [
            {
                "Date": format_date(e.expense_date),
                "Category": e.category,
                "Description": e.description,
                "Amount": format_currency(e.amount),
            }
            for e in rows
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sf-metric-label">EDIT OR DELETE A TRANSACTION</div>', unsafe_allow_html=True)

    options = {f"{format_date(e.expense_date)} \u2014 {e.category} \u2014 {format_currency(e.amount)}": e.id for e in rows}
    selected_label = st.selectbox("Select a transaction", list(options.keys()), key="tx_select")
    selected_id = options[selected_label]
    selected_expense = models.get_expense_by_id(selected_id, user_id)

    if selected_expense is None:
        return

    st.markdown('<div class="sf-form-section">', unsafe_allow_html=True)
    with st.form("edit_expense_form"):
        edit_amount = st.number_input("Amount", min_value=0.0, value=float(selected_expense.amount), step=50.0, format="%.2f")
        edit_category = st.selectbox(
            "Category",
            config.EXPENSE_CATEGORIES,
            index=config.EXPENSE_CATEGORIES.index(selected_expense.category)
            if selected_expense.category in config.EXPENSE_CATEGORIES
            else 0,
        )
        edit_description = st.text_input("Description", value=selected_expense.description)
        edit_date = st.date_input("Expense Date", value=pd.to_datetime(selected_expense.expense_date).date())

        col_a, col_b = st.columns(2)
        with col_a:
            update_clicked = st.form_submit_button("SAVE CHANGES")
        with col_b:
            delete_clicked = st.form_submit_button("DELETE")

    if update_clicked:
        try:
            models.update_expense(
                expense_id=selected_expense.id,
                user_id=user_id,
                amount=edit_amount,
                category=edit_category,
                description=edit_description,
                expense_date=edit_date.isoformat(),
            )
            st.success("Transaction updated successfully.")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        except Exception:
            st.error("Something went wrong while updating this transaction.")

    if delete_clicked:
        deleted = models.delete_expense(selected_expense.id, user_id)
        if deleted:
            st.success("Transaction deleted successfully.")
            st.rerun()
        else:
            st.error("This transaction could not be deleted.")

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
def render_analytics() -> None:
    st.markdown('<div class="sf-page-title">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sf-page-sub">Deeper insight into your spending patterns.</div>', unsafe_allow_html=True)

    user_id = _current_user_id()

    if analytics.get_transaction_count(user_id) == 0:
        st.markdown(
            '<div class="sf-glass sf-empty-state">Add your first expense to view financial analytics.</div>',
            unsafe_allow_html=True,
        )
        return

    summary = analytics.get_financial_summary(user_id)
    highest_category = summary["highest_category"] or {"category": "N/A", "total": 0}
    highest_expense = summary["highest_expense"] or {"amount": 0}

    cols = st.columns(2)
    with cols[0]:
        st.markdown(_metric_card("HIGHEST SPENDING CATEGORY", f"{highest_category['category']} \u2014 {format_currency(highest_category['total'])}", "category"), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(_metric_card("HIGHEST INDIVIDUAL EXPENSE", format_currency(highest_expense["amount"]), "highest"), unsafe_allow_html=True)

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        st.markdown('<div class="sf-chart-section">', unsafe_allow_html=True)
        st.markdown('<div class="sf-metric-label">SPENDING BY CATEGORY</div>', unsafe_allow_html=True)
        st.plotly_chart(analytics.build_category_donut(user_id), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with row1_c2:
        st.markdown('<div class="sf-chart-section">', unsafe_allow_html=True)
        st.markdown('<div class="sf-metric-label">MONTHLY SPENDING</div>', unsafe_allow_html=True)
        st.plotly_chart(analytics.build_monthly_bar(user_id), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        st.markdown('<div class="sf-chart-section">', unsafe_allow_html=True)
        st.markdown('<div class="sf-metric-label">SPENDING TREND</div>', unsafe_allow_html=True)
        st.plotly_chart(analytics.build_spending_trend(user_id), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with row2_c2:
        st.markdown('<div class="sf-chart-section">', unsafe_allow_html=True)
        st.markdown('<div class="sf-metric-label">TRANSACTION DISTRIBUTION</div>', unsafe_allow_html=True)
        st.plotly_chart(analytics.build_distribution_bar(user_id), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# AI Assistant
# ---------------------------------------------------------------------------
def render_ai_assistant() -> None:
    st.markdown('<div class="sf-page-title">AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sf-page-sub">Ask questions about your own financial data.</div>', unsafe_allow_html=True)

    if not config.AI_ENABLED:
        st.markdown(
            '<span class="sf-badge">Running in limited mode &mdash; OPENROUTER_API_KEY not configured</span>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    user_id = _current_user_id()

    st.markdown('<div class="sf-chat-section">', unsafe_allow_html=True)

    if not st.session_state["chat_history"]:
        st.markdown(
            '<div class="sf-empty-state">Ask something like "What is my total spending?" '
            'or "Give me a financial summary."</div>',
            unsafe_allow_html=True,
        )
    else:
        for role, content in st.session_state["chat_history"]:
            row_class = "user" if role == "user" else "ai"
            label = "USER" if role == "user" else "AI"
            st.markdown(
                f"""
                <div class="sf-chat-row {row_class}">
                    <div class="sf-chat-bubble {row_class}">
                        <div class="sf-chat-label">{label}</div>
                        {content}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div style="height: 14px;"></div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        question = st.text_input("Message", placeholder="Ask about your finances...", label_visibility="collapsed")
        sent = st.form_submit_button("SEND")

    if sent and question.strip():
        st.session_state["chat_history"].append(("user", question.strip()))
        with st.spinner("Analyzing your financial data..."):
            answer = agent.ask_ai(question.strip(), user_id)
        st.session_state["chat_history"].append(("ai", answer.replace("\n", "<br/>")))
        st.rerun()


# ---------------------------------------------------------------------------
# Main routing
# ---------------------------------------------------------------------------
def render_app() -> None:
    render_sidebar()

    page = st.session_state["page"]
    if page == "Dashboard":
        render_dashboard()
    elif page == "Add Expense":
        render_add_expense()
    elif page == "Transactions":
        render_transactions()
    elif page == "Analytics":
        render_analytics()
    elif page == "AI Assistant":
        render_ai_assistant()
    else:
        render_dashboard()


def main() -> None:
    _init_session_state()
    if st.session_state["authenticated"]:
        render_app()
    else:
        render_auth()


if __name__ == "__main__":
    main()
