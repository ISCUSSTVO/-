import asyncio
from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram import F
from inlinekeyboars.inline_kbcreate import inline_kbcreate


user_router = Router()

@user_router.message(F.text.lower().contains('старт'))
@user_router.message(CommandStart())
async def comm_start(message: types.Message):
    await message.answer(
        'это был старт'
    )

@user_router.message(F.text.lower().contains('меню'))
@user_router.message(Command('menu'))
async def comm_cat(message: types.Message):
    await message.answer(
        'категории игр бота', reply_markup=inline_kbcreate(btns={
            'гонки': f'car_game',
            'шутеры': f'shootgame'
        })
    )

@user_router.message()
async def qwe(message: types.Message):
    await message.answer(
        text='Мужик нажми на интерисующую комманду', reply_markup=inline_kbcreate(btns={
            'Категории': f'category' ,
            'Поиск аккаунта с игрой': f'searchgame',
            'Определение категории по игре': f'search_cat_ongame'
        })
    )

@user_router.callback_query(F.data == ('searchgame'))
async def chek_cat(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("хуй")

@user_router.callback_query(F.data == ('car_game'))
async def check_carrgames(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("ди нахуй")


@user_router.callback_query(F.data == ('car_game'))
async def check_carrgames(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("ди нахуй")


