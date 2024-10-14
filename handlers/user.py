import asyncio
import email
import imaplib
import re
from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query import orm_get_accounts_by_game
from inlinekeyboars.inline_kbcreate import Menucallback, inkbcreate
from aiogram.fsm.state import StatesGroup
from handlers.menu_proccesing import game_catalog, game_searching, get_menu_content, vidachalogs

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

    result = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name
    )
    if result is None:
        await callback.answer("Не удалось получить данные.", show_alert=True)
        return
    media, reply_markup = result
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


@user_router.callback_query(lambda c: c.data.startswith('show_cat_'))
async def process_show_game(callback_query: types.CallbackQuery, session: AsyncSession):
    # Извлекаем категорию из колбек-данных
    game_cat = callback_query.data.split('_')[2]  # Получаем название категории
    message_text, kbds = await game_catalog(session, game_cat, level=2)
    # Отправляем сообщение пользователю
    await callback_query.message.edit_media(message_text, reply_markup=kbds)
    await callback_query.answer()



@user_router.message()
async def game_search(message: types.Message, session: AsyncSession):  
    game = message.text
    account_qwe = await orm_get_accounts_by_game(session, game)
    games_list = [account.gamesonaacaunt for account in account_qwe]
    if game not in games_list or not F.text:
        await message.answer('Напиши старт')
        return
    for account in account_qwe:
        account_info = (
            f"{account.description}\n" 
            f"Цена: {account.price} rub"
        )

        kbds = inkbcreate(btns={
                "Купить 💵":    f"buyacc_{account.gamesonaacaunt}"
        })
        await message.answer_photo(account.image,caption=account_info, reply_markup=kbds)
        await message.delete()

@user_router.callback_query(F.data.startswith('buyacc_'))
async def buy_acc(callback:types.CallbackQuery, session:AsyncSession):
    game = callback.data.split('_')[-1]
    image, kbds = await game_searching(session, game)
    await callback.message.edit_media(image, reply_markup=kbds)


@user_router.callback_query(F.data.startswith('oplatil_'))
async def oplata(callback: types.CallbackQuery, session:AsyncSession):
    game = callback.data.split('_')[-1]
    image, kbds = await vidachalogs(session, game)
    await callback.message.edit_media(image, reply_markup=kbds)



@user_router.callback_query(F.data.startswith('chek_mail_'))
async def chek_mail(callback: types.CallbackQuery, session: AsyncSession):
    game = callback.data.split('_')[-1]
    
    result = await orm_get_accounts_by_game(session, game)
    for account in result:
        user_data = (account.accmail, account.imap)
        try:
            loop = asyncio.get_event_loop()
            # Создание цикла событий asyncio

            if user_data is None:
                await callback.message.answer("Не удалось получить данные из почтового ящика")
                return
            # Проверка наличия данных пользователя из почтового ящика

            mail_connection = await loop.run_in_executor(
                None, lambda: imaplib.IMAP4_SSL(IMAP_SERVER)
            )
            # Установка защищенного соединения с почтовым сервером

            mail_connection.login(user_data[0], user_data[1])
            mail_connection.select("INBOX")
            # Вход в почтовый ящик и выбор папки "INBOX"

            status, data = mail_connection.search(None, "FROM", '"Steam"')
            # Поиск писем от Steam

            latest_email_id = data[0].split()[-1]
            status, data = mail_connection.fetch(latest_email_id, "(RFC822)")
            # Извлечение последнего письма от Steam

            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            # Извлечение содержимого письма

            decoded_payload = None
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        decoded_payload = part.get_payload(decode=True).decode("utf-8")
                        break
            else:
                decoded_payload = email_message.get_payload(decode=True).decode("utf-8")
            # Декодирование содержимого письма

            if decoded_payload:
                match = re.search(r'Россия(.*?)Если это были не вы', decoded_payload, re.DOTALL)
                extracted_phrase = match.group(1).strip()
                await callback.message.answer(f"{extracted_phrase}")
            else:
                await callback.message.answer("Не удалось декодировать содержимое письма")
            # Извлечение кода доступа из письма и отправка его пользователю

        except Exception as e:
            await callback.message.answer(f"Произошла ошибка при чтении почты: {e}")
        finally:
            if "mail_connection" in locals():
                mail_connection.logout()
