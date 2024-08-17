import asyncio
from aiogram import types, Router
from aiogram.filters import CommandStart, Command
user_router = Router()

@user_router.message(CommandStart())
async def comm_start(message: types.Message):
    await message.answer('это был старт')

@user_router.message(Command('cat'))
async def comm_cat(message: types.Message):
    await message.answer('категории игр бота')

@user_router.message()
async def qwe(message: types.Message):
    await message.answer(message.text)
