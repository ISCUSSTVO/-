from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram import F
from sqlalchemy import select
from inlinekeyboars.inline_kbcreate import inkbcreate
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import accounts



user_router = Router()



@user_router.message(F.text.lower().contains('старт'))
@user_router.message(CommandStart())
async def comm_start(message: types.Message):
    await message.answer(
        'Здарова', reply_markup=inkbcreate(btns={
            'Категории игр': 'menu',
            'Все доступные аккаунты': 'allacc',
            'Поиск аккаунта с игрой': 'searchgame',
            'Определение категории по игре': 'search_cat_ongame'
        })
    )

@user_router.message(F.text.lower().contains('меню'))
@user_router.callback_query(F.data == ('menu'))
async def comm_cat(callback: types.CallbackQuery):
    await callback.message.answer(
        'категории игр бота', reply_markup=inkbcreate(btns={
            'гонки': f'car_game',
            'шутеры': f'shootgame'
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

@user_router.message()
async def qwe(message: types.Message):
    await message.answer(
        text='Мужик нажми на интерисующую комманду', reply_markup=inkbcreate(btns={
            'Категории': 'menu' ,
            'Поиск аккаунта с игрой': 'searchgame',
            'Определение категории по игре': 'search_cat_ongame'
        })
    )


