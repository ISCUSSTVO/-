from aiogram import types, Router, F
from aiogram.filters import CommandStart
#from aiogram.types import InputMediaPhoto
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query import orm_check_catalog1, orm_get_accounts_by_game, orm_get_banner
from inlinekeyboars.inline_kbcreate import Menucallback, inkbcreate
from aiogram.fsm.state import State, StatesGroup
from handlers.menu_proccesing import chek_mail, game_catalog, game_searching, get_menu_content, take_code, vidachalogs

user_router = Router()


account_list = [] 





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


@user_router.callback_query(F.data.startswith('show_cat_'))
async def process_show_game(callback_query: types.CallbackQuery, session: AsyncSession):
    # Извлекаем категорию из колбек-данных
    game_cat = callback_query.data.split('_')[2]  # Получаем название категории
    message_text, kbds = await game_catalog(session, game_cat, level=3)
    # Отправляем сообщение пользователю
    await callback_query.message.edit_media(message_text, reply_markup=kbds)
    await callback_query.answer()


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
async def chek_mail1(callback: types.CallbackQuery, session: AsyncSession):
    game = callback.data.split('_')[-1]

    qwe, result = await chek_mail(session, game)
    if result:
        await callback.message.answer(result)
    else:
        await callback.message.answer(qwe)
        
############################Получение кода купленного аккаунта############################
class GetCode(StatesGroup):
    user_data = State()

@user_router.callback_query(F.data == Menucallback(level=1, menu_name='steam_guard').pack())
async def handle_steam_guard(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):

    image = await take_code(session, level=1)
    await state.set_state(GetCode.user_data)
    await callback_query.message.edit_media(media=image)
   


@user_router.message(GetCode.user_data)
async def chek_code_guard(session: AsyncSession, message:types.Message, state: FSMContext):
    await take_code(session,level=1)
    qwe = await state.update_data(user_data=message.text)
    result = await orm_check_catalog1(session, qwe)
    if qwe == result:
        await message.answer('динахуй')
    else:
        await message.answer("ебать ты крутой")


    #qwe,image = await chek_mail(session, user_data)
    #if image:
    #    await message.edit_media(media=image)
    #else:
    #    await message.edit_text(qwe)
#





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