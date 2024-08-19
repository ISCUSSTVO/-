import logging
from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram import F
from sqlalchemy import select
from inlinekeyboars.inline_kbcreate import inkbcreate
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import accounts
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton 



user_router = Router()

logger = logging.getLogger(__name__)



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
            'Категории игр': 'categ',
            'Все доступные аккаунты': 'allacc',
            'Поиск аккаунта с игрой': 'searchgame',
            'Определение категории по игре': 'search_cat_ongame'
        })
    )

@user_router.callback_query(F.data == 'categ')
async def categor(cb: types.CallbackQuery, session: AsyncSession):
    try:
        result = await session.execute(select(accounts))
        account_list = result.scalars().all()
        
        if account_list:
            categories = {}
            # Группируем аккаунты по категориям
            for account in account_list:
                if account.categories not in categories:
                    categories[account.categories] = []
                categories[account.categories].append(account)

            # Отправляем категории и создаем инлайн-кнопки
            for category, accounts in categories.items():
                await cb.message.answer(f"Категория: {category}", reply_markup=inkbcreate(btns={
                    f"Показать аккаунты в категории: {category}": f'show_accounts:{category}'
                }))
        else:
            await cb.message.answer(
                'Нет категорий, братик', reply_markup=inkbcreate(btns={
                    'В меню': 'menu'
                })
            )
    except Exception as e:
        logger.error(f"Ошибка при получении категорий: {e}")
        await cb.message.answer("Произошла ошибка при получении категорий.")

@user_router.callback_query(F.data.startswith('show_accounts:'))
async def show_accounts(cb: types.CallbackQuery, session: AsyncSession):
    category = cb.data.split(':')[1]  # Получаем категорию из callback_data
    try:
        result = await session.execute(select(accounts).where(accounts.categories == category))
        account_list = result.scalars().all()
        
        if account_list:
            for account in account_list:
                await cb.message.answer(
                    f"Аккаунт: {account.acclog}, Пароль: {account.accpass}, Игры: {account.gamesonaacaunt}, Цена: {account.price}"
                )
        else:
            await cb.message.answer(
                f'Нет аккаунтов в категории: {category}'
            )
    except Exception as e:
        logger.error(f"Ошибка при получении аккаунтов для категории {category}: {e}")
        await cb.message.answer("Произошла ошибка при получении аккаунтов.")

            


@user_router.message(F.text.lower().contains('аккаунты'))
@user_router.callback_query(F.data == "allacc")
async def view_all_accounts(message_or_query: types.Message | types.CallbackQuery, session: AsyncSession):
    global account
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
            desc_name = account.name if account.name else "Без названия"
            account_info = ({account.image},
                            f"Аккаунт: {desc_name}\n"
                            f"Игры: {account.gamesonaacaunt}\n"
                            f"Цена: {account.price}")

            # Создаем инлайн-кнопку для каждого аккаунта
            inline_button = InlineKeyboardButton(text=f"Подробнее о {desc_name}", callback_data=f"details_{desc_name}")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])

            # Отправляем информацию об аккаунте в отдельном сообщении
            await message.answer(account_info, reply_markup=keyboard)
    else:
        await message.answer(
            'Нет аккаунтов братик', reply_markup=inkbcreate(btns={
                'В меню': 'menu'
            })
        )

@user_router.callback_query(F.data.startswith("details_"))
async def account_details(callback: types.CallbackQuery):
    account_name = callback.data.split("_", 1)[1]  # Получаем имя аккаунта

    # Здесь можно добавить логику для получения более подробной информации
    await callback.message.answer(f"Вы выбрали аккаунт: {account_name}.\n{account.description}")




@user_router.callback_query(F.data == 'searchgame')
async def search_game(callback: types.CallbackQuery):
    await callback.message.answer('Введи название игры')
    @user_router.message()
    async def process_game_name(message: types.Message, session: AsyncSession):
        game_name = message.text  # Получаем название игры от пользователя
    
        # Выполняем запрос к базе данных
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


@user_router.message()
async def qwe(message: types.Message):
    await message.answer(
        text='Мужик нажми на интерисующую комманду', reply_markup=inkbcreate(btns={
                'В меню': 'menu'
        })
    )


