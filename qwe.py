import asyncio
import os

from aiogram import Bot, Dispatcher
from handlers.user import user_router

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


ALUPD = ['message', 'callbackquery', 'edited_message']
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()


dp.include_routers(user_router)

async def main():
    bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALUPD)

asyncio.run(main())