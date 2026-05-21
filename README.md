# Valson Bot

Telegram bot for questionnaire-based waltz partner matching.

## Features

- Create or update profile
- Edit profile fields
- Upload photo
- Save partner preferences
- Find best matches by score
- Browse profiles by class
- Pagination
- Delete own profile
- SQLite storage

## Matching Logic

The bot uses questionnaire-based preferences to rank potential waltz partners.
Matches are scored based on class, dance role, height compatibility, experience level, and availability.
Optional tempo and goal preferences can add small extra score.

## Stack

Python, aiogram, aiosqlite, SQLite

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m bot.main
```
