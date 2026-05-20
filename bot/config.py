import os
from dotenv import load_dotenv

load_dotenv(override=True)

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
DB_PATH = os.getenv("DB_PATH", "bot.db").strip() or "bot.db"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Create .env file.")