import asyncio
import logging

from aiogram import Bot, Dispatcher

from .config import TELEGRAM_TOKEN
from .handlers import router
from .storage import JSONStorage

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    storage = JSONStorage(path="fsm_storage.json") # <-- ИСПОЛЬЗУЕМ JSONStorage
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        await dp.start_polling(bot)
    finally:
        await storage.close()

if __name__ == "__main__":
    asyncio.run(main())