# Smart Finance

### AI-Powered Personal Finance Analytics Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-red?style=for-the-badge&logo=streamlit)](https://smart-finance-ai.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/vedant-4009/smart-finance-ai)

Smart Finance is a multi-user personal finance analytics platform built with Python and Streamlit.

The application allows users to securely create an account, manage their expenses, analyze spending patterns, and interact with an AI Finance Assistant that provides insights and practical expense-reduction suggestions based on recorded financial data.

---

## Live Demo

**Try the application online:**

https://smart-finance-ai.streamlit.app/

**GitHub Repository:**

https://github.com/vedant-4009/smart-finance-ai

---

## Project Overview

Managing personal expenses becomes difficult when spending data is scattered across different places.

Smart Finance provides a centralized platform where users can:

- Create and manage their own account
- Record daily expenses
- Edit and delete transactions
- Search and filter expenses
- Analyze spending patterns
- View interactive financial charts
- Ask natural-language questions to an AI Finance Assistant
- Get practical suggestions for reducing unnecessary spending

The application follows a multi-user architecture where each user's financial data is isolated using an authenticated `user_id`.

---

## Key Features

### Secure Authentication

- User signup and login
- Email validation
- Unique email enforcement
- Password confirmation
- Secure password hashing
- Generic login error messages
- Session-based authentication
- Secure logout

### Expense Management

Users can manage their financial transactions through complete CRUD operations:

- Add expenses
- Edit expenses
- Delete expenses
- Search transactions
- Filter transactions
- Sort transactions
- Select expense categories
- Select transaction dates
- Add descriptions

### Personal Dashboard

The dashboard provides an overview of the user's financial activity.

It includes:

- Total spending
- Average expense
- Transaction count
- Highest expense
- Spending overview
- Category-based insights
- Interactive charts

### Analytics

Smart Finance provides interactive financial analytics using Plotly.

Analytics include:

- Spending by category
- Monthly spending trends
- Expense distribution
- Category comparison
- Spending patterns

### AI Finance Assistant

The application includes an AI-powered Finance Assistant using OpenRouter.

The assistant can answer questions such as:

```text
What is my total spending?
