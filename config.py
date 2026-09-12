"""
config.py
Central configuration loader for Smart Finance.
Loads environment variables and exposes typed configuration values.
Never hardcode secrets here.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load variables from a local .env file if present (never committed to VCS).
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_PATH = str(DATA_DIR / "expenses.db")

# ---------------------------------------------------------------------------
# AI / OpenRouter
# ---------------------------------------------------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()

# MODEL_NAME is the single canonical, configurable model identifier used
# throughout the project (agent.py, tools.py, and any future callers).
# It is read from the OPENROUTER_MODEL environment variable so the model
# stays configurable via .env, and defaults to "openrouter/free".
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "openrouter/free").strip()

# OPENROUTER_MODEL is kept as an alias of MODEL_NAME for backward
# compatibility with any code that still refers to it by that name.
OPENROUTER_MODEL = MODEL_NAME

AI_ENABLED = bool(OPENROUTER_API_KEY)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
APP_NAME = "SMART FINANCE"
APP_TAGLINE = "AI-Powered Personal Finance Analytics Platform"
CURRENCY_SYMBOL = "\u20b9"  # Indian Rupee sign

EXPENSE_CATEGORIES = [
    "Food",
    "Shopping",
    "Travel",
    "Bills",
    "Education",
    "Healthcare",
    "Entertainment",
    "Other",
]

# Minimum password requirements
PASSWORD_MIN_LENGTH = 8
