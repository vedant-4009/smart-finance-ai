"""
auth.py
Secure authentication: signup, login, password hashing and validation.

Passwords are hashed with PBKDF2-HMAC-SHA256 and a unique per-user salt.
Plain-text passwords are never stored, printed, or logged.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Tuple

import config
from database import db_cursor

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_PBKDF2_ITERATIONS = 260_000
_SALT_BYTES = 16


@dataclass
class User:
    id: int
    name: str
    email: str
    created_at: str


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256. Returns 'salt_hex$hash_hex'."""
    if salt is None:
        salt = os.urandom(_SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return f"{salt.hex()}${derived.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a plaintext password against a stored 'salt_hex$hash_hex' value."""
    try:
        salt_hex, _hash_hex = stored_hash.split("$", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    candidate = hash_password(password, salt)
    return _constant_time_eq(candidate, stored_hash)


def _constant_time_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    if len(password) < config.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {config.PASSWORD_MIN_LENGTH} characters long."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    return True, ""


# ---------------------------------------------------------------------------
# Signup / Login
# ---------------------------------------------------------------------------
def signup(name: str, email: str, password: str, confirm_password: str) -> Tuple[bool, str, Optional[User]]:
    name = (name or "").strip()
    email = (email or "").strip().lower()

    if not name:
        return False, "Full name is required.", None
    if not email:
        return False, "Email is required.", None
    if not is_valid_email(email):
        return False, "Please enter a valid email address.", None
    if not password:
        return False, "Password is required.", None
    if password != confirm_password:
        return False, "Passwords do not match.", None

    strong, message = validate_password_strength(password)
    if not strong:
        return False, message, None

    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cur.fetchone() is not None:
            return False, "An account with this email already exists.", None

        password_hash = hash_password(password)
        created_at = datetime.now(timezone.utc).isoformat()
        cur.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, created_at),
        )
        user_id = cur.lastrowid

    return True, "Account created successfully.", User(id=user_id, name=name, email=email, created_at=created_at)


def login(email: str, password: str) -> Tuple[bool, str, Optional[User]]:
    email = (email or "").strip().lower()
    if not email or not password:
        return False, "Invalid email or password.", None

    with db_cursor() as cur:
        cur.execute(
            "SELECT id, name, email, password_hash, created_at FROM users WHERE email = ?",
            (email,),
        )
        row = cur.fetchone()

    if row is None:
        return False, "Invalid email or password.", None

    if not verify_password(password, row["password_hash"]):
        return False, "Invalid email or password.", None

    user = User(id=row["id"], name=row["name"], email=row["email"], created_at=row["created_at"])
    return True, "Login successful.", user
