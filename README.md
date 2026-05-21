# Valson Bot

Telegram bot for waltz partner search inside my ed.institution.

I started this project because students had a problem with finding a dance partner in real life. It was awkward and slow, so I decided to make a bot that gives them a simple way to create a profile, browse other profiles, like someone, and get a mutual match.

## Features

- language selection
- profile questionnaire
- profile saving and updating
- profile deletion
- browsing by class
- compatibility score
- likes
- mutual matches
- inline buttons
- SQLite database
- tests

## Stack

Python, aiogram, aiosqlite, SQLite, pytest.

## how to run

Create `.env` file:

BOT_TOKEN=your_telegram_bot_token
DB_PATH=bot.db

Install dependencies and run:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m bot.main
