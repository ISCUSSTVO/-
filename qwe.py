import asyncio
import os

from aiogram import Bot, Dispatcher
from handlers.user import user_router
from handlers.admin import admin_router


from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())



bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()


dp.include_routers(user_router, admin_router)


async def on_startup(dp):
    print("Бот запущен и готов к работе!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())