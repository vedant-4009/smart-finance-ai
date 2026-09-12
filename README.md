# Smart Finance

**AI-Powered Personal Finance Analytics Platform**

A multi-user, database-backed personal finance web application built with
Streamlit, SQLite, Pandas, Plotly, and an OpenRouter-powered AI assistant.
The entire interface uses a consistent premium 3D glassmorphism FinTech
design — from the login screen to the dashboard, forms, tables, charts, and
AI chat.

---

## 1. Project Overview

Smart Finance lets each user securely sign up, log in, track expenses, and
explore their own spending through a dashboard, filterable transaction
table, and multi-chart analytics page. An AI Finance Assistant answers
natural-language questions about the user's own data using a tool-calling
architecture — it never touches the database directly and never invents
numbers.

## 2. Features

- Secure multi-user signup, login, and logout
- PBKDF2-HMAC-SHA256 password hashing with unique per-user salts
- Strict per-user data isolation on every query (dashboard, transactions,
  analytics, AI)
- Full expense CRUD: add, edit, delete, search, filter, sort
- Dashboard with key metrics and charts
- Analytics page with donut, bar, line/area, and distribution charts
- AI Finance Assistant with deterministic intent routing + LLM tool calling
  via OpenRouter
- Consistent 3D glassmorphism design across every page
- No emojis anywhere in the UI
- Graceful empty states, no fake/generated data
- Responsive layout for desktop, tablet, and mobile

## 3. Architecture

```
smart-finance/
├── app.py            # Streamlit entry point, routing, all page rendering
├── auth.py           # Signup / login / password hashing & validation
├── database.py       # SQLite connection + schema initialization
├── models.py         # Expense CRUD, always scoped to user_id
├── analytics.py       # Deterministic metrics + Plotly chart builders
├── tools.py          # Approved AI tool functions + OpenAI-style schemas
├── agent.py          # Intent routing + OpenRouter tool-calling agent
├── theme.py           # Shared 3D glassmorphism CSS
├── config.py          # Environment/config loader (no hardcoded secrets)
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── data/              # SQLite database file lives here at runtime
├── assets/            # logo/ and images/ (placeholders)
└── utils/
    ├── __init__.py
    └── formatting.py  # Deterministic currency/date formatting
```

## 4. Technology Stack

- **Python** – application language
- **Streamlit** – UI framework
- **SQLite** – embedded relational database
- **Pandas** – data aggregation for analytics
- **Plotly** – interactive charts
- **OpenAI Python SDK** pointed at **OpenRouter** – AI assistant
- **python-dotenv** – environment configuration

## 5. Database Schema

**users**

| Column         | Type    | Notes                     |
|----------------|---------|---------------------------|
| id             | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name           | TEXT    | NOT NULL                  |
| email          | TEXT    | UNIQUE, NOT NULL          |
| password_hash  | TEXT    | NOT NULL (never plaintext)|
| created_at     | TEXT    | NOT NULL (ISO timestamp)  |

**expenses**

| Column        | Type    | Notes                          |
|---------------|---------|---------------------------------|
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT       |
| user_id       | INTEGER | NOT NULL, FOREIGN KEY → users(id)|
| amount        | REAL    | NOT NULL, must be > 0           |
| category      | TEXT    | NOT NULL                        |
| description   | TEXT    |                                  |
| expense_date  | TEXT    | NOT NULL (YYYY-MM-DD)           |

## 6. Authentication

- Signup requires full name, email, password, and confirm password.
- Email format is validated and must be unique; duplicate signups are
  rejected with: *"An account with this email already exists."*
- Passwords must be at least 8 characters and include a letter and a number.
- Login failures always return the same generic message: *"Invalid email or
  password."* — the app never reveals which field was wrong.
- Logout clears the authenticated session, cached user data, and chat
  history, returning to the login screen.

## 7. Security

- Passwords are hashed with **PBKDF2-HMAC-SHA256** (260,000 iterations) and
  a unique random salt per user; only `password_hash` is stored.
- Password verification uses a constant-time comparison (`hmac.compare_digest`).
- No plaintext passwords are ever printed, logged, or returned to the client.
- No API keys or secrets are hardcoded; everything is loaded from `.env`
  via `config.py`.
- All error handling shows clean, user-facing messages — no raw tracebacks.

## 8. User Data Isolation

Every expense row carries a `user_id`. Every read, update, and delete query
in `models.py` filters — or additionally constrains — by `user_id`:

```sql
SELECT * FROM expenses WHERE user_id = ?
UPDATE expenses SET ... WHERE id = ? AND user_id = ?
DELETE FROM expenses WHERE id = ? AND user_id = ?
```

`user_id` is always read from the authenticated Streamlit session
(`st.session_state["user"]`) — never from a form field, URL parameter, or
any value that could be supplied by the client. This was verified directly:
attempting to update another user's expense by id returns `False` and makes
no change (see Testing section).

## 9. AI Agent Architecture

```
User Question
      ↓
Intent Router (deterministic, regex-based)
      ↓
Restricted Tool Schema exposed to the LLM
      ↓
OpenRouter LLM (tool-calling)
      ↓
Approved Python Tool (tools.py)
      ↓
Analytics Layer (analytics.py)
      ↓
SQLite (models.py / database.py)
      ↓
Current authenticated user's data ONLY
      ↓
Tool Result (already formatted, e.g. "₹1,200.00")
      ↓
LLM composes the final professional response
```

The LLM **never** receives a database connection or raw SQL access. It can
only call functions registered in `tools.py`, and every tool call is
executed with the `user_id` taken from the server-side session — the
model's tool-call arguments are never trusted for identity.

If `OPENROUTER_API_KEY` is not configured, the app does not break: it falls
back to answering recognized intents directly from the same tools, so the
core assistant experience still works without any external API.

## 10. AI Tool Calling

Available tools (`tools.py`):

- `get_total_spending`
- `get_average_expense`
- `get_category_spending`
- `get_monthly_spending`
- `get_highest_expense`
- `get_highest_category`
- `get_transaction_count`
- `get_financial_summary`

**Deterministic intent routing** (`agent.py`) matches common financial
questions (e.g. "What is my total spending?", "Which category has the
highest spending?") to a single tool name via regex. When an intent is
recognized, only that one tool is exposed to the LLM, which prevents
smaller/free models from selecting the wrong function. Unrecognized
questions fall back to the full tool set.

All monetary values are formatted once, centrally, in
`utils/formatting.py` (e.g. `₹1,200.00`), and tools return pre-formatted
strings — the LLM is instructed never to reformat or invent numbers.

## 11. 3D UI Architecture

All 3D styling lives in `theme.py` and is injected once per page render.
Techniques used throughout every page (auth, sidebar, dashboard, forms,
tables, charts, chat):

- `perspective()`, `rotateX()`, `rotateY()`, `translateZ()` on glass
  surfaces and cards, activated on hover for a subtle depth effect
- Layered glassmorphism (`backdrop-filter: blur`, translucent gradients,
  soft borders)
- Multi-layer soft-glow background: radial gradients, drifting blurred
  orbs, and a subtly animated perspective depth-grid
- Consistent shadow system (`--shadow-deep`, `--shadow-soft`) for
  layered elevation
- Custom-styled buttons, inputs, selects, and dataframes matching the same
  language
- No emoji usage anywhere — all icons are inline SVG

## 12. Installation

```bash
python -m venv venv
```

Activate the environment:

- **Windows (Git Bash):** `source venv/Scripts/activate`
- **macOS / Linux:** `source venv/bin/activate`

Install dependencies:

```bash
pip install -r requirements.txt
```

## 13. Environment Setup

```bash
cp .env.example .env
```

Then edit `.env`:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openrouter/free
```

The app runs without a key — the AI Assistant simply operates in a limited,
deterministic-only mode until a key is supplied.

## 14. Running the Project

```bash
streamlit run app.py
```

Open the local URL Streamlit prints (typically `http://localhost:8501`).

## 15. Testing

The following flow was executed against this codebase during development:

1. Start application — boots cleanly, no console errors
2. Signup — new account created
3. Duplicate signup — rejected with "An account with this email already exists."
4. Password mismatch — rejected with "Passwords do not match."
5. Invalid login — rejected with "Invalid email or password."
6. Valid login — session authenticated
7. Add expense — saved and visible immediately
8. Edit expense — updated in place
9. Delete expense — removed
10. Dashboard — metrics and charts render correctly
11. Analytics — all four charts render correctly
12. Transactions — search, filter, and sort work
13. AI Assistant — chat interface sends/receives messages
14. "What is my total spending?" → correct total
15. "Which category has the highest spending?" → correct category
16. "What is my highest individual expense?" → correct expense
17. "What is my average expense?" → correct average
18. "Show my monthly spending." → correct monthly breakdown
19. "Give me a financial summary." → correct full summary
20. Logout — session and chat history cleared, returns to login

**Multi-user isolation test** (executed directly against the data layer):

- User A recorded `Food ₹500` and `Shopping ₹1,000` → total **₹1,500.00**
- User B recorded `Travel ₹2,000` and `Education ₹3,000` → total **₹5,000.00**
- User A's transaction list contained only Food/Shopping; User B's
  contained only Travel/Education
- The AI assistant returned each user's own total correctly, with no
  cross-contamination
- Attempting to update User A's expense while authenticated as User B
  (`models.update_expense(expense_id, wrong_user_id, ...)`) returned
  `False` and made no change, confirming ownership is enforced at the
  query level

## 16. Future Improvements

- CSV/PDF export of transactions and analytics
- Budgets and spending alerts per category
- Multi-currency support
- OAuth-based login in addition to email/password
- Server-side rate limiting on the AI assistant endpoint

## 17. Interview Explanation

> Smart Finance is a multi-user, AI-powered personal finance analytics
> platform built using Python, Streamlit, SQLite, Pandas, Plotly, and
> OpenRouter.
>
> The platform provides secure user authentication and associates every
> expense with a `user_id`. All database and analytics queries are filtered
> using the authenticated user's ID, preventing cross-user data access.
>
> The AI assistant uses an agent-based tool-calling architecture. The LLM
> cannot directly access the database — it can only invoke approved Python
> financial tools, each of which is scoped to the current session's user.
>
> Deterministic intent routing is used for common financial questions to
> reduce incorrect tool selection when using free LLM models, by exposing
> only the single relevant tool for a recognized question.
>
> Financial values are retrieved from the database and formatted
> deterministically, so the AI can never hallucinate a number — it can only
> present what the tools return.
