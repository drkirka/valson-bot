# Valson Bot

Telegram bot for collecting and browsing waltz partner profiles.

## Features

- Create or update profile
- Upload photo
- Browse profiles by class
- Pagination
- Delete own profile
- SQLite storage

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m bot.main
