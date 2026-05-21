# Valson Bot

Telegram bot for collecting and browsing waltz partner profiles.

## Features

- Create and edit profiles
- Upload photos
- Browse profiles
- SQLite database

## Setup

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m bot.main
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m bot.main
```

## Configuration

Edit `.env`:

```env
BOT_TOKEN=your_bot_token
```
