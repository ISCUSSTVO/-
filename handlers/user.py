from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram import F
from sqlalchemy import select
from inlinekeyboars.inline_kbcreate import inkbcreate
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import accounts
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton 



user_router = Router()



@user_router.message(F.text.lower().contains('старт'))
@user_router.message(CommandStart())
async def comm_start(message: types.Message):
    await message.answer(
        'Здарова', reply_markup=inkbcreate(btns={
            'Главное меню': 'menu',
        })
    )

@user_router.message(F.text.lower().contains('меню'))
@user_router.callback_query(F.data == ('menu'))
async def comm_cat(callback: types.CallbackQuery):
    await callback.message.answer(
        'Выбирай что ты хочешь', reply_markup=inkbcreate(btns={
            'Категории игр': 'menu',
            'Все доступные аккаунты': 'allacc',
            'Поиск аккаунта с игрой': 'searchgame',
            'Определение категории по игре': 'search_cat_ongame'
        })
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
    result = await session.execute(select(accounts))
    account_list = result.scalars().all()

    if account_list:
        accounts_info = ""
        for account in account_list:
            category_name = account.categories if account.categories else "Без категории"
            accounts_info += f"Категории: {category_name}\nИгры: {account.gamesonaacaunt}"

        await message.answer(
            f'Список аккаунтов с играми:'
        )
        await message.answer(
            f'{accounts_info}'
        )
    else:
        await message.answer(
            'В базе данных нет аккаунтов с играми.'
        )

@user_router.callback_query(F.data == ('searchgame'))
async def check_carrgames(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "zxc"
    )


@user_router.callback_query(F.data == ('search_cat_ongame'))
async def check_gamecat(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "qwe"
    )


@user_router.callback_query(F.data == ('car_game'))
async def check_carrgames(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
            "ди нахуй"
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
    result = await session.execute(select(accounts))
    account_list = result.scalars().all()

    if account_list:
        for account in account_list:
            desc_name = account.description if account.description else "Без описания"
            account_info = (f"Описание: {desc_name}\n"
                            f"Игры: {account.gamesonaacaunt}\n"
                            f"Цена: {account.price}")

            # Создаем инлайн-кнопку для каждого аккаунта
            inline_button = InlineKeyboardButton(text=f"Подробнее о {desc_name}", callback_data=f"details_{desc_name}")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])

            # Отправляем информацию об аккаунте в отдельном сообщении
            await message.answer(account_info, reply_markup=keyboard)

@user_router.callback_query(F.data.startswith("details_"))
async def account_details(callback: types.CallbackQuery):
    account_name = callback.data.split("_", 1)[1]  # Получаем имя аккаунта

    # Здесь можно добавить логику для получения более подробной информации
    await callback.message.answer(f"Вы выбрали аккаунт: {account_name}. Подробности можно добавить здесь.")


@user_router.callback_query(F.data == ('searchgame'))
async def check_carrgames(callback: types.CallbackQuery):
    await callback.message.answer(
        'Введи название игры аккаунт с которой хочешь найти'
    )

@user_router.message(F.text)
async def search_game(message: types.Message, session: AsyncSession):
    game_name = message.text.strip()  # Получаем название игры от пользователя

    # Запрос к базе данных для поиска аккаунтов, содержащих игру
    result = await session.execute(select(accounts).where(accounts.gamesonaacaunt.contains(game_name)))
    account_list = result.scalars().all()

    if account_list:
        for account in account_list:
            desc_name = account.description if account.description else "Без описания"
            price = account.price
            
            # Получаем список игр из аккаунта
            games_on_account = account.gamesonaacaunt.split(',')  # Предполагаем, что игры разделены запятыми
            games_list = "\n".join([f"- {game.strip()}" for game in games_on_account])

            # Формируем сообщение с информацией об аккаунте
            message_text = f"Аккаунт:\nОписание: {desc_name}\nЦена: {price}\nИгры на аккаунте:\n{games_list}"

            # Отправляем сообщение с информацией об аккаунте
            await message.answer(message_text, reply_markup=inkbcreate(btns={
                'Найти ещё': 'searchgame',
                'В главное меню': 'menu'
            }))
    else:
        await message.answer("К сожалению, аккаунты с искомой игрой не найдены.", reply_markup=inkbcreate(btns={
            'Другая игра?': 'searchgame',
            'В главное меню': 'menu'
        }))

@user_router.callback_query(F.data == ('search_cat_ongame'))
async def check_gamecat(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "qwe"
    )


@user_router.callback_query(F.data == ('car_game'))
async def check_carrgames(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
            "ди нахуй"
    )

@user_router.message()
async def qwe(message: types.Message):
    await message.answer(
        text='Мужик нажми на интерисующую комманду', reply_markup=inkbcreate(btns={
            'Категории': 'menu' ,
            'Поиск аккаунта с игрой': 'searchgame',
            'Определение категории по игре': 'search_cat_ongame'
        })
    )


