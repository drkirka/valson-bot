import asyncio
from aiogram import Bot, Dispatcher

from bot.config import BOT_TOKEN
from bot.database import init_db
from bot.handlers import router


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())