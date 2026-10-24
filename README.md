# Telegram Lead Capture Bot — Portfolio Demo

A working English-language Telegram bot demo for auto-detailing businesses. It guides a potential customer through a simple quote-request flow, saves structured lead information in SQLite, and notifies an administrator in Telegram.

**This is a demo, not a real business.** Replace branding, services, and privacy text before using it with real clients.

## Features

- Consent step before gathering contact information
- Service selection with Telegram buttons
- Name and phone validation
- Optional vehicle details (up to 500 characters)
- SQLite persistence with timestamps
- Administrator notification with escaped user input
- `/start`, `/cancel`, `/delete` commands
- Friendly handling when notification delivery fails

## Quick start (Windows PowerShell)

1. Install Python 3.11+ and verify with `py --version`.
2. Open a terminal in this folder.
3. Create environment and install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env`, and edit `.env` with your values:

```powershell
Copy-Item .env.example .env
```

5. In Telegram, open **@BotFather**, send `/newbot`, and save the bot token **only in your local `.env`**.
6. Open **@userinfobot** (or another trusted ID-finding method) to find your numeric Telegram user ID; set it as `ADMIN_CHAT_ID`. Open a conversation with your new bot first. An administrator must initiate a chat with the bot before the bot can message them.
7. Run:

```powershell
python bot.py
```

8. Open your bot, send `/start`, agree to the demo privacy note, and complete a sample request.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Data and security

- Never commit `.env`, real lead databases, tokens, customer messages, or screenshots containing personal information.
- Only use synthetic leads for the public portfolio demo.
- `/delete` removes database records for the requesting Telegram user. It **cannot** delete administrator notifications already delivered in Telegram.
- SQLite and in-memory FSM suit a small demo only. Production deployments need persistent conversation state, admin access controls, retention policies, rate limiting, backups, and jurisdiction-appropriate privacy documentation.
- This bot does not book appointments or invent prices.

## Portfolio description

**Telegram Lead Capture Bot for Auto Detailing**

Built an English-language Telegram bot prototype that collects customer quote requests, validates contact information, stores requests in a structured database, and sends instant notifications to the business owner. Technologies: Python, aiogram 3, Telegram Bot API, SQLite.

## Suggested portfolio media

1. Start screen and consent flow (synthetic info only)
2. Service selection and contact collection
3. Administrator lead notification (synthetic info only)
4. 30–60 second screen recording of a complete demo flow
