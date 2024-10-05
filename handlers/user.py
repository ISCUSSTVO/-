#import asyncio
#import re
#import email
#import imaplib
from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession
from db.engine import AsyncSessionLocal
from db.orm_query import orm_get_accounts_by_game1
from inlinekeyboars.inline_kbcreate import Menucallback, get_services_btns4
from aiogram.fsm.state import StatesGroup
from handlers.menu_proccesing import gamecatalog, get_menu_content

user_router = Router()


account_list = [] 
IMAP_SERVER = "imap.mail.ru"
SMTP_SERVER = "smtp.mail.ru"


class Form(StatesGroup):
    waiting_for_game_name = 'waiting_for_game_name'

@user_router.message(F.text.lower().contains('start'))
@user_router.message(F.text.lower().contains('старт'))
@user_router.message(CommandStart())
async def start (message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)

@user_router.callback_query(Menucallback.filter())
async def user_manu(callback: types.CallbackQuery, callback_data: Menucallback, session: AsyncSession):
    page = callback_data.page if callback_data.page is not None else 1

    result = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        page=page
    )
    print(result)

    if result is None:
        await callback.answer("Не удалось получить данные.", show_alert=True)
        return

    media, reply_markup = result

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


@user_router.callback_query(lambda c: c.data.startswith('show_cat_'))
async def process_show_game(callback_query: types.CallbackQuery):
    level = 2
    # Извлекаем категорию из колбек-данных
    game_cat = callback_query.data.split('_')[2]  # Получаем название категории
    async with AsyncSessionLocal as session:
        # Получаем контент меню для уровня 2 (каталог игр)
        message_text, kbds = await gamecatalog(session, game_cat, level)

        # Отправляем сообщение пользователю
        await callback_query.message.edit_media(message_text, reply_markup=kbds)
        await callback_query.answer()


@user_router.message(F.text.lower().contains('й'))
async def yow(msg: types.Message):
    await msg.answer('ЙОООООООООООООООООООООООу')


@user_router.message()
async def gamesearch(message: types.Message, session: AsyncSession):  
    level = 3
    game = message.text.strip()  # Убираем лишние пробелы
    account_qwe = await orm_get_accounts_by_game1(session, game)
    games_list = [account.gamesonaacaunt for account in account_qwe]
    print(account_qwe)  # Отладочное сообщени
    for service in account_qwe:  # Проходим по всем найденным услугам
        account_info = (
            f"{service.description}\n"  # Используем service вместо account_qwe
            f"Игра: {service.gamesonaacaunt}\n"  # Используем service
            f"Цена: {service.price} rub"
        )

        kbds = get_services_btns4(
            level=level,
            service_id=service.id  # Используем service вместо services
        )
        await message.answer_photo(photo=service.image,caption=account_info, reply_markup=kbds)
    if game not in games_list or not F.text():
        await message.answer('Напиши старт')
        return
    
