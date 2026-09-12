"""
agent.py
AI Finance Assistant agent layer.

The assistant supports two types of questions:

1. Personal finance questions:
   These use approved tools and the authenticated user's real financial data.

2. General finance and conversational questions:
   These are answered by the AI model without accessing personal financial data.

Flow for personal finance questions:
    User Question
        -> Intent Router
        -> Approved Tool
        -> Analytics
        -> SQLite
        -> Current User's Data Only
        -> Response

Flow for general questions:
    User Question
        -> OpenRouter AI
        -> General AI Response

The LLM never receives direct database access.
Every personal finance tool is executed with the authenticated user's user_id.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

import config
import tools


_MAX_TOOL_ROUNDS = 3


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are the Smart Finance AI Assistant, a professional personal finance analytics assistant.

Rules you must always follow:
- You do not have direct access to any database.
- You may only obtain personal financial figures by calling the provided tools.
- Never invent, estimate, or guess a user's financial number, transaction, category, or date.
- Use the tool result as the source of truth for personal financial data.
- All monetary values returned by tools are already formatted.
- Do not recompute or modify financial values returned by tools.
- Keep responses clear, useful, and professional.
- Do not repeat the user's question.
- Do not use emojis.
- Do not provide investment, loan, tax, insurance, or other regulated financial advice.
- For general finance questions, provide practical educational information.
- For personal financial questions, use the available tools whenever possible.
"""

GENERAL_SYSTEM_PROMPT = """You are the Smart Finance AI Assistant.

You are a helpful, professional general-purpose personal finance assistant.

You can answer general questions about:
- budgeting
- saving money
- expense management
- spending habits
- financial organization
- emergency funds
- financial planning concepts
- money management
- general personal finance education

Important rules:
- Do not invent personal financial data.
- Do not claim to know the user's income, expenses, balance, transactions, or financial situation unless the application provides that information through an approved tool.
- Give practical and understandable answers.
- Keep answers concise but useful.
- Do not repeat the user's question.
- Do not use emojis.
- Do not provide personalized investment, loan, tax, insurance, or other regulated financial advice.
- When the user asks for general advice, answer naturally instead of saying that the request is unsupported.
"""


# ---------------------------------------------------------------------------
# Deterministic intent routing
# ---------------------------------------------------------------------------

_INTENT_PATTERNS: List[Tuple[str, str]] = [
    (
        "get_saving_suggestions",
        r"reduce.{0,25}(expense|expenses|spending|spend|cost|costs)|"
        r"(expense|expenses|spending|spend|cost|costs).{0,25}(reduce|cut|lower)|"
        r"save money|"
        r"saving.{0,20}(money|expense|expenses|spending)|"
        r"how can i save|"
        r"how to save|"
        r"where can i cut|"
        r"ways to save|"
        r"cut my expenses|"
        r"reduce my spending|"
        r"how to reduce spending|"
        r"how to reduce expenses|"
        r"how can i reduce my expenses|"
        r"manage.{0,25}(expense|expenses|spending|spend)|"
        r"(expense|expenses|spending|spend).{0,25}manage|"
        r"control.{0,25}(expense|expenses|spending|spend)|"
        r"(expense|expenses|spending|spend).{0,25}control",
    ),
    (
        "get_financial_summary",
        r"\b(financial )?summary\b|"
        r"give me a summary|"
        r"analyze my finances|"
        r"overall financial|"
        r"overall spending summary",
    ),
    (
        "get_highest_category",
        r"(highest|top|most).{0,25}categor|"
        r"categor.{0,25}(highest|top|most)|"
        r"where am i spending the most|"
        r"which category.*most",
    ),
    (
        "get_highest_expense",
        r"(highest|largest|biggest).{0,20}(expense|transaction|purchase)|"
        r"(expense|transaction|purchase).{0,20}(highest|largest|biggest)|"
        r"biggest expense|"
        r"largest expense",
    ),
    (
        "get_average_expense",
        r"\baverage\b|"
        r"average expense|"
        r"average spending",
    ),
    (
        "get_transaction_count",
        r"how many transactions|"
        r"number of transactions|"
        r"transaction count|"
        r"how many expenses|"
        r"number of expenses",
    ),
    (
        "get_monthly_spending",
        r"\bmonthly\b|"
        r"by month|"
        r"per month|"
        r"each month|"
        r"monthly spending",
    ),
    (
        "get_category_spending",
        r"by category|"
        r"per category|"
        r"spending by category|"
        r"category.{0,10}spend|"
        r"category wise|"
        r"category-wise",
    ),
    (
        "get_total_spending",
        r"\btotal\b.*spend|"
        r"total spending|"
        r"how much.*(spend|spent)|"
        r"total expense|"
        r"how much have i spent|"
        r"how much did i spend",
    ),
]


def route_intent(question: str) -> Optional[str]:
    """Return the matching finance tool name for a recognized question."""

    normalized = (question or "").strip().lower()

    if not normalized:
        return None

    for tool_name, pattern in _INTENT_PATTERNS:
        if re.search(pattern, normalized):
            return tool_name

    return None


# ---------------------------------------------------------------------------
# OpenRouter client
# ---------------------------------------------------------------------------

def _get_client():
    """Create the OpenRouter client lazily."""

    from openai import OpenAI

    return OpenAI(
        api_key=config.OPENROUTER_API_KEY,
        base_url=config.OPENROUTER_BASE_URL,
    )


# ---------------------------------------------------------------------------
# Personal finance AI with tools
# ---------------------------------------------------------------------------

def _run_llm_with_tools(
    question: str,
    user_id: int,
    tool_names: List[str],
) -> str:
    """Run an AI conversation using only approved finance tools."""

    client = _get_client()

    tool_schemas = tools.get_tool_schemas(tool_names)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    for _ in range(_MAX_TOOL_ROUNDS):

        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=messages,
            tools=tool_schemas if tool_schemas else None,
            tool_choice="auto" if tool_schemas else None,
        )

        message = response.choices[0].message

        tool_calls = getattr(message, "tool_calls", None)

        if not tool_calls:
            return (message.content or "").strip()

        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in tool_calls
                ],
            }
        )

        for tool_call in tool_calls:

            tool_name = tool_call.function.name

            result = tools.call_tool(
                tool_name,
                user_id,
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

    return (
        "The assistant could not complete this request. "
        "Please try rephrasing your question."
    )


# ---------------------------------------------------------------------------
# General AI conversation
# ---------------------------------------------------------------------------

def _run_general_llm(question: str) -> str:
    """Generate a general AI response without accessing personal data."""

    client = _get_client()

    messages = [
        {
            "role": "system",
            "content": GENERAL_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    response = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=messages,
        temperature=0.7,
    )

    message = response.choices[0].message

    return (message.content or "").strip()


# ---------------------------------------------------------------------------
# Local fallback responses
# ---------------------------------------------------------------------------

def _local_general_response(question: str) -> str:
    """
    Provide useful responses when the AI model is unavailable.
    This prevents the assistant from showing only an error message.
    """

    question_lower = question.lower()

    if any(
        phrase in question_lower
        for phrase in [
            "manage expense",
            "manage expenses",
            "manage spending",
            "control expense",
            "control expenses",
            "control spending",
            "reduce expense",
            "reduce expenses",
            "reduce spending",
            "save money",
            "saving money",
            "cut expenses",
            "cut my expenses",
            "budget",
            "budgeting",
        ]
    ) or any(
        typo in question_lower
        for typo in [
            "expance",
            "expences",
            "expence",
        ]
    ):
        return (
            "A practical long-term approach to managing expenses is:\n\n"
            "1. Track every expense consistently.\n"
            "2. Identify your highest spending categories.\n"
            "3. Separate essential and non-essential expenses.\n"
            "4. Set realistic limits for high-spending categories.\n"
            "5. Review your transactions every week.\n"
            "6. Reduce unnecessary recurring expenses.\n"
            "7. Set a regular savings target.\n"
            "8. Review your progress every month.\n\n"
            "The key to a sustainable solution is consistent expense "
            "tracking, realistic category limits, and regular reviews."
        )

    if any(
        phrase in question_lower
        for phrase in [
            "financial discipline",
            "spending habit",
            "spending habits",
            "bad spending habits",
        ]
    ):
        return (
            "To improve financial discipline:\n\n"
            "1. Track expenses regularly.\n"
            "2. Avoid unnecessary impulse purchases.\n"
            "3. Set limits for major spending categories.\n"
            "4. Review transactions every week.\n"
            "5. Set a consistent savings target.\n"
            "6. Review your progress at the end of each month."
        )

    if any(
        phrase in question_lower
        for phrase in [
            "emergency fund",
            "emergency savings",
        ]
    ):
        return (
            "An emergency fund is money kept aside for unexpected essential "
            "expenses. A good starting approach is to build it gradually, "
            "keep it separate from everyday spending, and contribute to it "
            "regularly."
        )

    if any(
        phrase in question_lower
        for phrase in [
            "financial plan",
            "plan my finances",
            "financial planning",
        ]
    ):
        return (
            "A simple financial planning process is:\n\n"
            "1. Track your income and expenses.\n"
            "2. Create a realistic budget.\n"
            "3. Build emergency savings.\n"
            "4. Control unnecessary spending.\n"
            "5. Set short-term and long-term financial goals.\n"
            "6. Review your progress regularly."
        )

    return (
        "I can help with budgeting, saving, expense management, "
        "spending habits, financial organization, and analysis of "
        "your recorded expenses."
    )


# ---------------------------------------------------------------------------
# Main AI assistant
# ---------------------------------------------------------------------------

def ask_ai(question: str, user_id: int) -> str:
    """Answer a finance or general question for the authenticated user."""

    question = (question or "").strip()

    if not question:
        return "Please enter a question."

    # ---------------------------------------------------------------
    # Step 1: Detect known personal finance questions.
    # ---------------------------------------------------------------

    intent_tool = route_intent(question)

    if intent_tool:

        try:
            return tools.call_tool(
                intent_tool,
                user_id,
            )

        except Exception:
            return (
                "Unable to analyze your financial data right now. "
                "Please try again."
            )

    # ---------------------------------------------------------------
    # Step 2: Use OpenRouter for general and natural-language questions.
    # ---------------------------------------------------------------

    if config.AI_ENABLED:

        try:
            answer = _run_general_llm(question)

            if answer:
                return answer

        except Exception:
            pass

    # ---------------------------------------------------------------
    # Step 3: Local fallback if the AI model is unavailable.
    # ---------------------------------------------------------------

    return _local_general_response(question)