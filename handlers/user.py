import asyncio
import re
import email
import imaplib
from aiogram import types, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram import F
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from db.engine import AsyncSessionLocal
from db.orm_query import orm_get_accounts_by_game1
from inlinekeyboars.inline_kbcreate import Menucallback, inkbcreate, get_services_btns4
from db.models import Accounts
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from handlers.menu_proccesing import gamecatalog, get_menu_content, handle_game_selection

user_router = Router()


account_list = [] 
IMAP_SERVER = "imap.mail.ru"
SMTP_SERVER = "smtp.mail.ru"


class Form(StatesGroup):
    waiting_for_game_name = 'waiting_for_game_name'


#@user_router.message(CommandStart())
#@user_router.message(F.text.lower().contains('старт'))
#@user_router.callback_query(F.data == ('menu'))
#async def comm_cat(cb_or_msg: types.CallbackQuery | types.Message):
#    if isinstance(cb_or_msg, types.CallbackQuery):
#        await cb_or_msg.answer()
#        message = cb_or_msg.message
#    else:
#        message = cb_or_msg
#    await message.answer(
#        'Выбирай что ты хочешь', reply_markup=inkbcreate(btns={
#            'Ваша корзина': 'checkbacket',
#            'Категории игр': 'categ',
#            'Все доступные аккаунты': 'allacc',
#            'Поиск аккаунта с игрой': 'searchgame',
#        }, sizes=(2,2))
#    )

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


@user_router.callback_query(lambda c: c.data.startswith('show_game_'))
async def process_game_selection(callback_query: types.CallbackQuery):
    game_name = callback_query.data.split('_')[2]  # Получаем имя игры
    page = 1  # Начальная страница
    level = 3  # Уровень, который вам нужен

    # Правильное использование AsyncSessionLocal
    async with AsyncSessionLocal as session:
        await handle_game_selection(callback_query, session, game_name,  level, page)


@user_router.message(F.text.lower().contains('й'))
async def yow(msg: types.Message):
    await msg.answer('ЙОООООООООООООООООООООООу')


@user_router.message(F.text)
async def gamesearch(message: types.Message, session: AsyncSession):  
    level = 3
    game = message.text.strip()  # Убираем лишние пробелы
    account_qwe = await orm_get_accounts_by_game1(session, game)
    
    print(account_qwe)  # Отладочное сообщение

    p = 0
    for service in account_qwe:  # Проходим по всем найденным услугам
        p+=1
        account_info = (
            f"{service.description}\n"  # Используем service вместо account_qwe
            f"Игра: {service.gamesonaacaunt}\n"  # Используем service
            f"Цена: {service.price} rub"
        )

        kbds = get_services_btns4(
            level=level,
            service_id=service.id  # Используем service вместо services
        )
    if p>0:
        await message.answer_photo(photo=service.image,caption=account_info, reply_markup=kbds)
    else:
        await message.answer('Напиши старт')

##################Список всех аккаунтов в будующем только кнопки################################################################
@user_router.message(F.text.lower().contains('аккаунты'))
@user_router.callback_query(F.data == "allacc")
async def view_all_accounts(message_or_query: types.Message | types.CallbackQuery, session: AsyncSession):
    if isinstance(message_or_query, types.CallbackQuery):
        await message_or_query.answer()
        message = message_or_query.message
    else:
        message = message_or_query

    # Получаем все аккаунты из таблицы accounts
    result = await session.execute(select(Accounts))
    account_list = result.scalars().all()

    if account_list:
        for account in account_list:
            description = account.description if account.description else "Нет описания"
            account_info = (
                f"Аккаунт: {description}\n"
                f"Игры: {account.gamesonaacaunt}\n"
                f"Цена: {account.price}"
            )

            # Создаем инлайн-кнопку для каждого аккаунта
            inline_button = InlineKeyboardButton(text=f"Подробнее о {description}", callback_data=f"details_{description}_{description}")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])

            # Отправляем информацию об аккаунте с кнопкой "Подробнее" и изображением
            if account.image:  # Проверяем, есть ли изображение
                await message.answer_photo(photo=account.image, caption=account_info, reply_markup=keyboard)
            else:
                await message.answer(account_info, reply_markup=keyboard)
    else:
        await message.answer(
            'Нет аккаунтов ', reply_markup=inkbcreate(btns={
                'В меню': 'menu'
            })
        )
##################Список всех категорий в будующем только кнопки################################################################
@user_router.callback_query(F.data == 'categ')
async def categor(cb: types.CallbackQuery, session: AsyncSession):
    result = await session.execute(select(Accounts))
    account_list = result.scalars().all()
        
    if account_list:
        categories = {}
        # Группируем аккаунты по категориям
        for account in account_list:
            if account.categories not in categories:
                categories[account.categories] = []
            categories[account.categories].append(account)

        # Отправляем категории и создаем инлайн-кнопки
        for category_name in categories.keys():
            await cb.message.answer(
                f"Категория: {category_name}",
                reply_markup=inkbcreate(btns={
                    "Показать аккаунты": f'show_accounts:{category_name}'
                })
            )
    else:
        await cb.message.answer(
            'Нет категорий, братик', 
            reply_markup=inkbcreate(btns={
                'В меню': 'menu'
            })
        )

##################Список всех аккаунтов в категории в будующем только кнопки################################################################
@user_router.callback_query(F.data.startswith('show_accounts:'))
async def show_accounts(cb: types.CallbackQuery, session: AsyncSession):
    category = cb.data.split(':')[1]  # Получаем категорию из callback_data
    result = await session.execute(select(Accounts).where(Accounts.categories == category))
    account_list = result.scalars().all()
    
    if account_list:
        for account in account_list:       
            await cb.message.answer_photo(
                photo=account.image , 
                caption=f"Имя: {account.name}\nИгры: {account.gamesonaacaunt}\nЦена: {account.price}",
                reply_markup=inkbcreate(btns={
                    f"Подробнее о {account.name}": f"details_{account.name}_{account.description}"
                })
            )
    else:
        await cb.message.answer(
            f'Нет аккаунтов в категории: {category}'
            )

##################Детали аккаунта################################################################
@user_router.callback_query(F.data.startswith('details_'))
async def account_details(cb: types.CallbackQuery, session: AsyncSession):
    _, account_name, description = cb.data.split('_')
    
    # Получаем аккаунт из базы данных
    result = await session.execute(select(Accounts).where(Accounts.name == account_name))
    account = result.scalars().first()

    if account:
        account_info = (
            f"Имя: {account.name}\n"
            f"Описание: {description}\n"
            f"Игры: {account.gamesonaacaunt}\n"
            f"Цена: {account.price}"
        )
        
        # Создаем кнопки для добавления в корзину и выбора другого аккаунта
        buttons = {
            "Добавить в корзину": f"addback_{account.name}",
            "Выбрать другой аккаунт": "choose_another_account"
        }
        
        keyboard = inkbcreate(btns=buttons)

        await cb.message.answer(account_info, reply_markup=keyboard)
    else:
        await cb.message.answer("Аккаунт не найден.")


##################Выбор другого аккаунта################################################################
@user_router.callback_query(F.data == 'choose_another_account')
async def choose_another_account(cb: types.CallbackQuery, session: AsyncSession):
    # Логика для отображения списка доступных аккаунтов
    result = await session.execute(select(Accounts))
    accounts = result.scalars().all()

    if accounts:
        accounts_buttons = {account.name: f"details_{account.name}_{account.description}" for account in accounts}
        keyboard = inkbcreate(btns=accounts_buttons)

        await cb.message.answer("Выберите другой аккаунт:", reply_markup=keyboard)
    else:
        await cb.message.answer("Нет доступных аккаунтов.")

##################Добавление акакаунта в корзину ################################################################

##################Поиск игры################################################################
@user_router.callback_query(F.data == 'searchgame')
async def search_game(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_game_name)  # Устанавливаем состояние
    await callback.message.answer('Введи название игры')

@user_router.message(StateFilter(Form.waiting_for_game_name))
async def process_game_name(message: types.Message, session: AsyncSession, state: FSMContext):
    game_name = message.text  # Получаем название игры от пользователя

    # Удаляем вызов session() и просто используем session
    result = await session.execute(select(Accounts).where(Accounts.gamesonaacaunt.contains(game_name)))
    account_list = result.scalars().all()

    if account_list:
        for account in account_list:
            desc_name = account.description if account.description else "Без описания"
            price = account.price
            name = account.name
            
            games_on_account = account.gamesonaacaunt.split(',')
            games_list = "\n".join([f"- {game.strip()}" for game in games_on_account])

            message_text = f"Аккаунт: {name}\nОписание: {desc_name}\nЦена: {price}\nИгры на аккаунте:\n{games_list}"

            await message.answer_photo(photo=account.image, caption=message_text, reply_markup=inkbcreate(btns={
                'Найти ещё': 'searchgame',
                'В главное меню': 'menu',
                'Добавить в корзину': f'addback_{account.name}'
            }))
    else:
        await message.answer("К сожалению, аккаунты с искомой игрой не найдены.", reply_markup=inkbcreate(btns={
            'Другая игра?': 'searchgame',
            'В главное меню': 'menu'
        }))

    await state.clear()


##################Корзина ################################################################

##################Обработчик оплаты ################################################################
@user_router.callback_query(F.data.startswith('pay_'))
async def pay_account(cb: types.CallbackQuery,):
    account_name = cb.data.split('_')[1]
    # Логика обработки оплаты (например, отправка пользователю информации о способах оплаты)
    await cb.message.answer(f"Вы выбрали оплату для аккаунта: {account_name}", reply_markup=inkbcreate(btns={
        'Получить код': f'takecode_{account_name}'
    }))

##################Получиение кода с почты ################################################################
@user_router.callback_query(F.data.startswith('takecode_'))
async def get_last_steam_email(cb: types.CallbackQuery, session: AsyncSession):
    account_name = cb.data.split('_')[1]
    result = await session.execute(select(Accounts).where(Accounts.name == account_name))
    account = result.scalars().first()
    user_data = (account.accmail, account.imap)

    if user_data is None:
        await cb.message.answer("Не удалось получить данные из почтового ящика")
        return

    try:
        loop = asyncio.get_event_loop()

        mail_connection = await loop.run_in_executor(
            None, lambda: imaplib.IMAP4_SSL(IMAP_SERVER)
        )
        mail_connection.login(user_data[0], user_data[1])
        mail_connection.select("INBOX")

        # Поиск писем от Steam
        status, email_ids = mail_connection.search(None, 'FROM "Steam"')
        
        if status != 'OK':
            await cb.message.answer("Ошибка при поиске писем.")
            return

        email_ids = email_ids[0].split()
        
        if not email_ids:
            await cb.message.answer("Нет писем от Steam.")
            return

        latest_email_id = email_ids[-1].decode()  # Убедитесь, что ID в строковом формате
        status, data = mail_connection.fetch(latest_email_id, "(RFC822)")
        
        if status != 'OK':
            await cb.message.answer(f"Ошибка при получении письма: {status}")
            return

        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)

        decoded_payload = None
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    decoded_payload = part.get_payload(decode=True).decode("utf-8")
                    break
        else:
            decoded_payload = email_message.get_payload(decode=True).decode("utf-8")

        if decoded_payload:
            match = re.search(r'Код доступа(.*?)Если это были не вы', decoded_payload, re.DOTALL)
            if match:
                extracted_phrase = match.group(1).strip()
                await cb.message.answer(f"{extracted_phrase}")
            else:
                await cb.message.answer("Не удалось найти заданные фразы в письме")
        else:
            await cb.message.answer("Не удалось декодировать содержимое письма")

    except Exception as e:
        await cb.message.answer(f"Произошла ошибка при чтении почты: {e}")
    finally:
        if "mail_connection" in locals():
            mail_connection.logout()


##################обработчик сообщений вне команд################################################################


