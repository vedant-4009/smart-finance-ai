"""
models.py
Data models and CRUD operations for expenses.

CRITICAL: every query in this module is scoped to a user_id. There is no
function here capable of returning or mutating another user's data, and the
user_id must always come from the authenticated session, never from a form
field or URL parameter.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from database import db_cursor


@dataclass
class Expense:
    id: int
    user_id: int
    amount: float
    category: str
    description: str
    expense_date: str


def create_expense(user_id: int, amount: float, category: str, description: str, expense_date: str) -> int:
    """Insert a new expense for the given user. Returns the new expense id."""
    if amount is None or amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    if not category:
        raise ValueError("Category is required.")
    if not expense_date:
        raise ValueError("Expense date is required.")

    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO expenses (user_id, amount, category, description, expense_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, float(amount), category, description or "", expense_date),
        )
        return cur.lastrowid


def get_expenses(user_id: int) -> List[Expense]:
    """Return all expenses belonging to user_id, most recent first."""
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT id, user_id, amount, category, description, expense_date
            FROM expenses
            WHERE user_id = ?
            ORDER BY expense_date DESC, id DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()

    return [
        Expense(
            id=row["id"],
            user_id=row["user_id"],
            amount=row["amount"],
            category=row["category"],
            description=row["description"] or "",
            expense_date=row["expense_date"],
        )
        for row in rows
    ]


def get_expense_by_id(expense_id: int, user_id: int) -> Optional[Expense]:
    """Fetch a single expense, but only if it belongs to user_id."""
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT id, user_id, amount, category, description, expense_date
            FROM expenses
            WHERE id = ? AND user_id = ?
            """,
            (expense_id, user_id),
        )
        row = cur.fetchone()

    if row is None:
        return None

    return Expense(
        id=row["id"],
        user_id=row["user_id"],
        amount=row["amount"],
        category=row["category"],
        description=row["description"] or "",
        expense_date=row["expense_date"],
    )


def update_expense(
    expense_id: int,
    user_id: int,
    amount: float,
    category: str,
    description: str,
    expense_date: str,
) -> bool:
    """Update an expense. Ownership is enforced in the WHERE clause."""
    if amount is None or amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    with db_cursor() as cur:
        cur.execute(
            """
            UPDATE expenses
            SET amount = ?, category = ?, description = ?, expense_date = ?
            WHERE id = ? AND user_id = ?
            """,
            (float(amount), category, description or "", expense_date, expense_id, user_id),
        )
        return cur.rowcount > 0


def delete_expense(expense_id: int, user_id: int) -> bool:
    """Delete an expense. Ownership is enforced in the WHERE clause."""
    with db_cursor() as cur:
        cur.execute(
            "DELETE FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id),
        )
        return cur.rowcount > 0
