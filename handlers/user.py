import asyncio
from sqlite3 import IntegrityError
from aiogram import types, Router
from aiogram.filters import CommandStart, StateFilter
import re
import email
import imaplib
from aiogram import F
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
from inlinekeyboars.inline_kbcreate import inkbcreate
from db.models import Accounts, Backet
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext


user_router = Router()


account_list = [] 
IMAP_SERVER = "smtp.mail.ru"


class Form(StatesGroup):
    waiting_for_game_name = 'waiting_for_game_name'


@user_router.message(CommandStart())
@user_router.message(F.text.lower().contains('старт'))
@user_router.callback_query(F.data == ('menu'))
async def comm_cat(cb_or_msg: types.CallbackQuery | types.Message):
    if isinstance(cb_or_msg, types.CallbackQuery):
        await cb_or_msg.answer()
        message = cb_or_msg.message
    else:
        message = cb_or_msg
    await message.answer(
        'Выбирай что ты хочешь', reply_markup=inkbcreate(btns={
            'Ваша корзина': 'checkbacket',
            'Категории игр': 'categ',
            'Все доступные аккаунты': 'allacc',
            'Поиск аккаунта с игрой': 'searchgame',
        }, sizes=(2,2))
    )



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
            desc_name = account.name if account.name else "Без названия"
            description = account.description if account.description else "Нет описания"
            account_info = (
                f"Аккаунт: {desc_name}\n"
                f"Игры: {account.gamesonaacaunt}\n"
                f"Цена: {account.price}"
            )

            # Создаем инлайн-кнопку для каждого аккаунта
            inline_button = InlineKeyboardButton(text=f"Подробнее о {desc_name}", callback_data=f"details_{desc_name}_{description}")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])

            # Отправляем информацию об аккаунте с кнопкой "Подробнее" и изображением
            if account.image:  # Проверяем, есть ли изображение
                await message.answer_photo(photo=account.image, caption=account_info, reply_markup=keyboard)
            else:
                await message.answer(account_info, reply_markup=keyboard)
    else:
        await message.answer(
            'Нет аккаунтов братик', reply_markup=inkbcreate(btns={
                'В меню': 'menu'
            })
        )

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

@user_router.callback_query(F.data.startswith('addback_'))
async def addback(cb: types.CallbackQuery, session: AsyncSession):
    account_name = cb.data.split('_')[1]  # Извлекаем имя аккаунта из callback_data

    # Получаем аккаунт из базы данных
    result = await session.execute(select(Accounts).where(Accounts.name == account_name))
    account = result.scalars().first()

    if account:
        user_id = cb.from_user.id 
        nameacc = account.name 
        info_acc = f"{account.acclog},{account.accpass}"
        imgacc = account.image 

        # Создаем новый объект Backet
        new_backet = Backet(username=user_id, image=imgacc, name=nameacc, infoacc=info_acc)

        try:
            session.add(new_backet)
            await session.commit()
            await cb.message.answer("Аккаунт успешно добавлен в корзину!",reply_markup=inkbcreate(btns={
                'В главное меню':   'menu',
                'Ещё аккаунт': ('allacc')
            }))
        except IntegrityError:
            await session.rollback()
            await cb.message.answer("Ошибка: аккаунт уже существует в корзине.",reply_markup=inkbcreate(btns={
                'В главное меню':   'menu',
                'Ещё аккаунт': ('allacc')
                }))
        except Exception as e:
            await session.rollback()
            await cb.message.answer(f"Произошла ошибка: {str(e)}")
    else:
        await cb.message.answer("Аккаунт не найден.")

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
    
    await state.clear()  # Завершаем состояние после обработки


@user_router.callback_query(F.data == 'checkbacket')
async def chekback(cb: types.CallbackQuery, session: AsyncSession):
    user_id = cb.from_user.id

    # Получаем все элементы корзины для данного пользователя
    result = await session.execute(select(Backet).where(Backet.username == user_id))
    backet_items = result.scalars().all()

    if not backet_items:
        await cb.message.answer("Ваша корзина пуста.")
        return

    account_messages = []

    for item in backet_items:
        # Разделяем информацию об аккаунте на логин и пароль
        login, password = item.infoacc.split(',')

        # Получаем аккаунт из базы данных по логину и паролю
        account_result = await session.execute(
            select(Accounts).where(Accounts.acclog == login, Accounts.accpass == password)
        )
        account = account_result.scalars().first()

        if account:
            # Формируем сообщение с информацией об аккаунте
            account_info = (
                f"Имя: {account.name}\n"
                f"Цена: {account.price}\n"
                f"Игры на аккаунте: {account.gamesonaacaunt}\n"
            )

            # Кнопки для взаимодействия
            buttons = {
                "Оплатить": f"pay_{account.name}",
                "Убрать из корзины": f"remove_{account.name}"
            }
            keyboard = inkbcreate(btns=buttons)

            account_messages.append((account_info, keyboard))
        else:
            account_messages.append(("Аккаунт не найден в системе.", None))

    # Отправляем сообщения с информацией об аккаунтах
    for account_info, keyboard in account_messages:
        await cb.message.answer_photo(photo=account.image, caption=account_info, reply_markup=keyboard if keyboard else None)

    await cb.answer()

@user_router.callback_query(F.data.startswith('pay_'))
async def pay_account(cb: types.CallbackQuery,):
    account_name = cb.data.split('_')[1]
    # Логика обработки оплаты (например, отправка пользователю информации о способах оплаты)
    await cb.message.answer(f"Вы выбрали оплату для аккаунта: {account_name}", reply_markup=inkbcreate(btns={
        'Получить код': f'takecode_{account_name}'
    }))

@user_router.callback_query(F.data.startswith('takecode_'))
async def get_last_steam_email(cb: types.CallbackQuery, session: AsyncSession):
    account_name = cb.data.split('_')[1]
    result = await session.execute(select(Accounts).where(Accounts.name == account_name))
    account = result.scalars().first()
    user_data = (account.accmail, account.imap)
    try:
        loop = asyncio.get_event_loop()
        # Создание цикла событий asyncio
        if user_data is None:
            await cb.message.answer("Не удалось получить данные из почтового ящика")
            return
        # Проверка наличия данных пользователя из почтового ящика

        mail_connection = await loop.run_in_executor(
            None, lambda: imaplib.IMAP4_SSL(IMAP_SERVER)
        )
        # Установка защищенного соединения с почтовым сервером

        mail_connection.login(user_data[0], user_data[1])
        mail_connection.select("INBOX")
        # Вход в почтовый ящик и выбор папки "INBOX"

        data = mail_connection.search(None, "FROM", '"Steam"')
        # Поиск писем от Steam

        latest_email_id = data[0].split()[-1]
        data = mail_connection.fetch(latest_email_id, "(RFC822)")
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
            match = re.search(r'Код доступа(.*?)Если это были не вы', decoded_payload, re.DOTALL)
            if match:
                extracted_phrase = match.group(1).strip()
                await cb.message.answer(f"{extracted_phrase}")
            else:
                await cb.message.answer("Не удалось найти заданные фразы в письме")
        else:
            await cb.message.answer("Не удалось декодировать содержимое письма")
        # Извлечение кода доступа из письма и отправка его пользователю

    except Exception as e:
        await cb.message.answer(f"Произошла ошибка при чтении почты: {e}")
    finally:
        if "mail_connection" in locals():
            mail_connection.logout()



@user_router.callback_query(F.data.startswith('remove_'))
async def remove_from_backet(cb: types.CallbackQuery, session: AsyncSession):
    account_name = cb.data.split('_')[1]
    username = cb.from_user.id
    result = await session.execute(select(Backet).where(Backet.username == username, Backet.name == account_name))
    accounts_to_remove = result.scalars().all()
    if accounts_to_remove:
        await session.execute(delete(Backet).where(Backet.username == username, Backet.name == account_name))
        await cb.message.answer(f"Аккаунт {account_name} был убран из корзины.",reply_markup=inkbcreate(btns={
            'В главное меню': 'menu'
        }))
        await session.commit()
    else:
        await cb.message.answer(f"Аккаунт {account_name} не найден в корзине.")





@user_router.message()
async def qwe(message: types.Message):
    await message.answer(
        text='Мужик нажми на интерисующую комманду', reply_markup=inkbcreate(btns={
                'В меню': 'menu'
        })
    )
