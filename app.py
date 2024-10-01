import asyncio
import os
from aiogram import Bot, Dispatcher
from db.engine import create_db, drop_db, session_maker



from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from midleware.db import DataBaseSession


from handlers.admin import adm_router
from handlers.user import user_router


bot = Bot(token=os.getenv('TOKEN'), )
dp = Dispatcher()

dp.include_routers(adm_router, user_router)

async def on_startup():
    run_param = False
    if run_param:
        await drop_db()
    await create_db()
    print(
        'Бот запущен и готов к работе!'
    )  

async def on_shutdown():
    print (
        'Бот лег'
    )





async def main():
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())
