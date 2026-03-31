import asyncio

from aiogram import Bot

from app.bot.dispatcher import create_dispatcher
from app.bot.httpx_session import HttpxSession
from app.core.config import settings


async def main() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is empty. Add it to bot_service/.env"
        )

    session = HttpxSession()
    bot = Bot(token=settings.telegram_bot_token, session=session)
    dp = create_dispatcher()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())